#!/usr/bin/env python3
"""Build, upload, redownload and verify an unpublished Kp release candidate.

Never publishes a release, moves an existing tag, or overwrites an asset.
Requires Python 3.10+, git, gh and an authorized GH_TOKEN for this repository.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

REPOSITORY = "aaalshehre2024/klebsiella-amr-genomics"
BRANCH = "release/kp-manuscript-2026-11-14-rc1"
SOURCE_COMMIT = "ce5c15154cb4eb96a149c0aec0c3ee12f69931ca"
SOURCE_IMPORT = "source_data/2026-11-13_existing_analysis"
SOURCE_HELPER = "scripts/publication/collect_existing_sources.py"
SOURCE_ARCHIVE = "Klebsiella_existing_sources_2026-11-13.zip"
SOURCE_PREFIX = "Klebsiella_existing_sources/"
RELEASE_DIRECTORY = "release_data/2026-11-14_rc1"
TITLE = "K. pneumoniae manuscript release candidate (14 November 2026)"


def run(arguments: list[str], *, cwd: Path, optional_404: bool = False,
        log: Path | None = None) -> str | None:
    completed = subprocess.run(arguments, cwd=cwd, text=True, capture_output=True,
                               timeout=900, check=False)
    if log is not None:
        log.write_text(completed.stdout + completed.stderr, encoding="utf-8")
    if completed.returncode:
        if optional_404 and "(HTTP 404)" in completed.stderr:
            return None
        raise RuntimeError(f"{arguments[0]} failed ({completed.returncode}): "
                           + completed.stderr.strip() + "\n" + completed.stdout[-2000:])
    return completed.stdout


def api(root: Path, endpoint: str, *, optional: bool = False,
        fields: dict[str, str] | None = None) -> dict | list | None:
    command = ["gh", "api", "--method", "POST" if fields else "GET", endpoint]
    for key, value in (fields or {}).items():
        command += ["-f", f"{key}={value}"]
    output = run(command, cwd=root, optional_404=optional)
    return None if output is None else json.loads(output)


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
                    encoding="utf-8")


def tag_commit(root: Path, tag: str) -> str | None:
    reference = api(root, f"repos/{REPOSITORY}/git/ref/tags/{tag}", optional=True)
    if reference is None:
        return None
    obj = reference["object"]
    for _ in range(10):
        if obj["type"] == "commit":
            return obj["sha"]
        if obj["type"] != "tag":
            raise RuntimeError("Release tag does not resolve to a commit")
        obj = api(root, f"repos/{REPOSITORY}/git/tags/{obj['sha']}")["object"]
    raise RuntimeError("Too many nested annotated tags")


def find_release(root: Path, tag: str) -> dict | None:
    # List includes drafts for authorized writers; the by-tag endpoint describes
    # published releases and must not be used to conclude a draft is absent.
    matches = []
    page = 1
    while True:
        releases = api(root, f"repos/{REPOSITORY}/releases?per_page=100&page={page}")
        matches.extend(item for item in releases if item.get("tag_name") == tag)
        if len(releases) < 100:
            break
        page += 1
    if len(matches) > 1:
        raise RuntimeError("Multiple releases use this tag; resolve before resuming")
    return matches[0] if matches else None


def require_draft(root: Path, tag: str, head: str) -> dict:
    release = find_release(root, tag)
    if release is None:
        raise RuntimeError("Expected draft release could not be found")
    if release.get("draft") is not True or release.get("prerelease") is not True:
        raise RuntimeError("Existing release must remain a draft and a prerelease")
    if tag_commit(root, tag) != head:
        raise RuntimeError("Release tag no longer identifies the exact build commit")
    return release


def asset_map(root: Path, release_id: int) -> dict:
    result = {}
    page = 1
    while True:
        assets = api(root, f"repos/{REPOSITORY}/releases/{release_id}/assets?per_page=100&page={page}")
        for asset in assets:
            if asset["name"] in result:
                raise RuntimeError("Duplicate release asset name")
            result[asset["name"]] = asset
        if len(assets) < 100:
            return result
        page += 1


def download_assets(root: Path, tag: str, names: list[str], destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    if any(destination.iterdir()):
        raise RuntimeError(f"Fresh download directory is not empty: {destination}")
    command = ["gh", "release", "download", tag, "--repo", REPOSITORY,
               "--dir", str(destination)]
    for name in names:
        command += ["--pattern", name]
    run(command, cwd=root)
    if {p.name for p in destination.iterdir()} != set(names):
        raise RuntimeError("Downloaded asset names do not match the requested exact set")


def ensure_asset(root: Path, tag: str, head: str, path: Path, helper,
                 *, report: bool = False) -> dict:
    release = require_draft(root, tag, head)
    assets = asset_map(root, release["id"])
    name = path.name
    digest = helper.sha256_file(path)

    def same_remote(asset_name: str) -> bool:
        with tempfile.TemporaryDirectory(prefix="kp-existing-asset-", dir=root / "release_build") as tmp:
            folder = Path(tmp) / "fresh"
            download_assets(root, tag, [asset_name], folder)
            return helper.equal_files(path, folder / asset_name)

    if name in assets:
        if same_remote(name):
            return {"name": name, "sha256": digest, "size_bytes": path.stat().st_size,
                    "id": assets[name]["id"], "action": "reused_identical_asset"}
        if not report:
            raise RuntimeError(f"Existing asset has different bytes; refusing replacement: {name}")
        name = f"{path.stem}-{digest[:12]}{path.suffix}"
        if name in assets:
            if not same_remote(name):
                raise RuntimeError(f"Versioned report asset has conflicting bytes: {name}")
            return {"name": name, "sha256": digest, "size_bytes": path.stat().st_size,
                    "id": assets[name]["id"], "action": "reused_identical_asset"}
    upload_path = path
    if name != path.name:
        upload_path = root / "release_build" / "versioned_reports" / name
        upload_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, upload_path)
    require_draft(root, tag, head)
    run(["gh", "release", "upload", tag, str(upload_path), "--repo", REPOSITORY], cwd=root)
    uploaded = asset_map(root, release["id"])[name]
    if uploaded.get("state") != "uploaded" or uploaded.get("size") != path.stat().st_size:
        raise RuntimeError(f"Asset upload did not complete: {name}")
    return {"name": name, "sha256": digest, "size_bytes": path.stat().st_size,
            "id": uploaded["id"], "action": "uploaded"}


def verify_source(root: Path, archive: Path, destination: Path, log: Path, helper) -> dict:
    destination.mkdir(parents=True, exist_ok=False)
    with zipfile.ZipFile(archive) as z:
        helper.checked_zip(z)
        for item in z.infolist():
            if not item.filename.startswith(SOURCE_PREFIX):
                raise RuntimeError("Source archive has an unexpected root directory")
            relative = helper.safe_name(item.filename, item.is_dir())
            target = destination / relative
            if item.is_dir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                with z.open(item) as source, target.open("xb") as output:
                    shutil.copyfileobj(source, output)
    extracted = destination / SOURCE_PREFIX.rstrip("/")
    run([sys.executable, str(extracted / SOURCE_HELPER), "verify", "--destination",
         str(extracted / SOURCE_IMPORT)], cwd=root, log=log)
    status = json.loads((extracted / SOURCE_IMPORT / "SOURCE_STATUS.json").read_text())
    if status.get("source_files") != 77 or status.get("scientific_reproduction") != "NOT_RUN":
        raise RuntimeError("Frozen source status does not match the expected source-import scope")
    return {"status": "PASS", "source_files": status["source_files"],
            "zip_warnings": status.get("zip_warnings"), "scientific_reproduction": "NOT_RUN",
            "sha256": helper.sha256_file(archive), "size_bytes": archive.stat().st_size,
            "scope": "Integrity of the frozen 77-source-file import; existing archive warning retained."}


def main(root: Path) -> dict:
    root = root.resolve()
    directory = root / RELEASE_DIRECTORY
    spec = importlib.util.spec_from_file_location("kp_release_builder", directory / "build_and_verify.py")
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    if os.environ.get("GITHUB_REPOSITORY", REPOSITORY) != REPOSITORY:
        raise RuntimeError("Unexpected GitHub repository")
    if os.environ.get("GITHUB_ACTIONS") == "true" and os.environ.get("GITHUB_REF") != f"refs/heads/{BRANCH}":
        raise RuntimeError("This workflow must run from the release candidate branch")
    head = run(["git", "rev-parse", "HEAD"], cwd=root).strip()
    if not re.fullmatch(r"[0-9a-f]{40}", head):
        raise RuntimeError("Invalid build commit")
    if os.environ.get("GITHUB_SHA") and os.environ["GITHUB_SHA"] != head:
        raise RuntimeError("Checkout does not match the workflow event commit")
    run(["git", "cat-file", "-e", f"{SOURCE_COMMIT}^{{commit}}"], cwd=root)
    expected_lines = (directory / "EXPECTED_MASTER_SHA256.txt").read_text().split()
    if not expected_lines:
        raise RuntimeError("Missing expected master SHA-256")
    expected_sha = helper.sha_expectation(expected_lines[0])
    notes_file = directory / "RELEASE_NOTES.md"
    original_notes = notes_file.read_text(encoding="utf-8")
    build = root / "release_build"
    downloaded = root / "release_download"
    if downloaded.exists() and any(downloaded.iterdir()):
        raise RuntimeError("Use a fresh release_download directory for each invocation")
    build_result = helper.build(argparse.Namespace(repo_root=root, output=build))
    master = build / build_result["master"]["archive"]
    if helper.sha256_file(master) != expected_sha:
        raise RuntimeError("Master archive differs from the independently retained, pinned expected hash")
    source = build / SOURCE_ARCHIVE
    if source.exists():
        raise RuntimeError("Use a fresh build directory for the source snapshot")
    run(["git", "archive", "--format=zip", f"--prefix={SOURCE_PREFIX}",
         f"--output={source}", SOURCE_COMMIT, SOURCE_IMPORT, SOURCE_HELPER], cwd=root)
    source_hash = helper.sha256_file(source)
    source_sidecar = build / (SOURCE_ARCHIVE + ".sha256")
    source_sidecar.write_text(f"{source_hash}  {SOURCE_ARCHIVE}\n", encoding="ascii")
    source_build = verify_source(root, source, build / "source_extracted",
                                 build / "source_build_verification.log", helper)
    print("Pinned master archive and frozen source snapshot verified locally.", flush=True)

    tag = f"kp-manuscript-2026-11-14-rc1-{head[:7]}"
    observed_tag = tag_commit(root, tag)
    if observed_tag is None:
        api(root, f"repos/{REPOSITORY}/git/refs", fields={"ref": f"refs/tags/{tag}", "sha": head})
    elif observed_tag != head:
        raise RuntimeError("Existing tag points to another commit; refusing to move it")
    if tag_commit(root, tag) != head:
        raise RuntimeError("Could not verify exact remote tag")
    release = find_release(root, tag)
    if release is None:
        run(["gh", "release", "create", tag, "--repo", REPOSITORY, "--verify-tag",
             "--target", head, "--draft", "--prerelease", "--latest=false", "--title", TITLE,
             "--notes-file", str(notes_file)], cwd=root)
    release = require_draft(root, tag, head)
    print(f"Unpublished draft: {release['html_url']}", flush=True)

    uploaded = []
    core = [master, build / (master.name + ".sha256"), source, source_sidecar]
    for path in core:
        uploaded.append(ensure_asset(root, tag, head, path, helper))
    for path in (build / "BUILD_VERIFICATION.json", build / "source_build_verification.log"):
        uploaded.append(ensure_asset(root, tag, head, path, helper, report=True))

    require_draft(root, tag, head)
    download_assets(root, tag, [p.name for p in core], downloaded)
    for retained in core:
        if not helper.equal_files(retained, downloaded / retained.name):
            raise RuntimeError(f"Release download differs from retained build: {retained.name}")
    helper.verify(argparse.Namespace(archive=downloaded / master.name,
                  expected_sha256=expected_sha, expected_file=master,
                  report=downloaded / "DOWNLOAD_VERIFICATION.json"))
    source_download = verify_source(root, downloaded / source.name,
                                    downloaded / "source_extracted",
                                    downloaded / "source_download_verification.log", helper)
    if source_download["sha256"] != source_build["sha256"]:
        raise RuntimeError("Downloaded source hash mismatch")
    for path in (downloaded / "DOWNLOAD_VERIFICATION.json", downloaded / "source_download_verification.log"):
        uploaded.append(ensure_asset(root, tag, head, path, helper, report=True))

    run_id = os.environ.get("GITHUB_RUN_ID")
    run_url = f"https://github.com/{REPOSITORY}/actions/runs/{run_id}" if run_id else None
    scope = json.loads((directory / "release_scope.json").read_text())
    receipt = {
        "status": "DRAFT_ASSETS_DOWNLOADED_AND_VERIFIED",
        "observed_utc": datetime.now(timezone.utc).isoformat(),
        "repository": REPOSITORY, "tag": tag, "release_id": release["id"],
        "release_url": release["html_url"], "draft": True, "prerelease": True,
        "source_commit": SOURCE_COMMIT, "build_commit": head, "workflow_run_url": run_url,
        "master_archive": {"name": master.name, "sha256": expected_sha,
                           "size_bytes": master.stat().st_size, "byte_comparison": "PASS"},
        "source_archive": {"name": source.name, **source_download, "byte_comparison": "PASS"},
        "assets": uploaded, "release_scope": scope,
        "scientific_scope": "Archive integrity and release download verification ran here. The separate bundled scientific_verification.json records the prior scoped numerical reproduction. This workflow does not rerun scientific analyses or establish full manuscript reproducibility.",
        "publication_performed": False,
    }
    write_json(downloaded / "RELEASE_RECEIPT.json", receipt)
    receipt_asset = ensure_asset(root, tag, head, downloaded / "RELEASE_RECEIPT.json", helper, report=True)
    summary = (
        "\n\n## Verified release downloads\n\n"
        f"Build commit: `{head}`. Source snapshot: `{SOURCE_COMMIT}`.\n\n"
        f"Master archive SHA-256: `{expected_sha}`.\n\n"
        f"Source archive SHA-256: `{source_hash}`.\n\n"
        "Both ZIPs and their checksum files were downloaded from this draft and matched the retained build bytes. "
        "Internal archive checksums and the 77-file source integrity check passed. "
        "The existing source archive warning remains documented.\n\n"
        f"Verification receipt: `{receipt_asset['name']}`.\n\n"
        "This release remains an unpublished draft. Scientific reproduction and the latest Figure 1 plotting-source limitation are described in the bundled scope records.\n"
    )
    if run_url:
        summary += f"\n[Verification workflow]({run_url})\n"
    updated_notes = build / "VERIFIED_RELEASE_NOTES.md"
    updated_notes.write_text(original_notes.rstrip() + summary, encoding="utf-8")
    require_draft(root, tag, head)
    run(["gh", "release", "edit", tag, "--repo", REPOSITORY, "--draft=true",
         "--prerelease=true", "--latest=false", "--notes-file", str(updated_notes)], cwd=root)
    final = require_draft(root, tag, head)
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        with open(summary_path, "a", encoding="utf-8") as output:
            output.write(f"## Draft release verified\n\n[Review draft]({final['html_url']})\n\n"
                         f"Tag: `{tag}`\n\nMaster SHA-256: `{expected_sha}`\n\n"
                         "The release remains unpublished. See attached verification reports and documented scientific scope.\n")
    print(json.dumps(receipt, indent=2, ensure_ascii=False, sort_keys=True))
    return receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    arguments = parser.parse_args()
    try:
        main(arguments.repo_root)
    except Exception as error:
        failure = {"status": "FAILED", "observed_utc": datetime.now(timezone.utc).isoformat(),
                   "error": str(error), "publication_performed": False}
        write_json(arguments.repo_root.resolve() / "release_download" / "RELEASE_FAILURE.json", failure)
        print(f"FAIL: {error}", file=sys.stderr)
        raise SystemExit(1)
