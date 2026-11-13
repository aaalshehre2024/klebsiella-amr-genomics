#!/usr/bin/env python3
"""Import the 77 inventoried Klebsiella source files without changing originals.

Python 3.10+, standard library only. This preserves evidence; it does not run
the scientific analysis or establish the manuscript's reported quantities.
"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys
import zipfile

LIMIT = 50 * 1024**2
SUMS = "SHA256SUMS"
EXPECTED = {"candidate_current_tsv": 17, "additional_draft_tsv": 1,
            "candidate_newick": 22, "native_result_txt": 4, "historical_csv": 1,
            "result_bundle_zip": 30, "analysis_starter_zip": 1,
            "publication_setup_zip": 1}
FIELDS = ["path", "source_relative_path", "category", "bytes", "sha256"]
SECTION2 = "=== 2. CONTENTS OF KLEBORATE RESULTS ==="
SECTION3 = "=== 3. ANALYSIS SCRIPTS, TABLES, TREES AND MANIFESTS ==="


def safe_relative(name: str) -> None:
    if (not name or name.startswith("/") or re.match(r"^[A-Za-z]:", name) or "\\" in name
            or any(ord(c) < 32 or ord(c) == 127 for c in name)
            or any(p in {"", ".", "..", ".git"} for p in name.split("/"))
            or PurePosixPath(name).as_posix() != name):
        raise ValueError(f"Unsafe relative path: {name!r}")


def checked_path(raw: str | Path) -> Path:
    path = Path(raw).expanduser().absolute()
    if ".." in path.parts:
        raise ValueError("Use an absolute path without '..'.")
    for part in (path, *path.parents):
        if part.is_symlink():
            raise ValueError(f"Symlink is not accepted: {part}")
    return path.resolve()


def digest(path: Path, target: Path | None = None) -> tuple[int, str]:
    before = path.stat()
    if not stat.S_ISREG(before.st_mode):
        raise ValueError(f"Not an ordinary file: {path}")
    h = hashlib.sha256()
    out = target.open("xb") if target is not None else None
    try:
        with path.open("rb") as source:
            for block in iter(lambda: source.read(1024**2), b""):
                h.update(block)
                if out is not None:
                    out.write(block)
    finally:
        if out is not None:
            out.close()
    after = path.stat()
    signature = lambda s: (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns)
    if signature(before) != signature(after):
        raise ValueError(f"Source changed while reading: {path}")
    return after.st_size, h.hexdigest()


def files_in(root: Path) -> dict[str, Path]:
    files = {}
    for current, dirs, names in os.walk(root, followlinks=False):
        for name in dirs + names:
            path = Path(current) / name
            relative = path.relative_to(root).as_posix()
            safe_relative(relative)
            mode = path.lstat().st_mode
            if not stat.S_ISDIR(mode) and not stat.S_ISREG(mode):
                raise ValueError(f"Symlink or special file: {relative}")
            if stat.S_ISREG(mode):
                files[relative] = path
    return dict(sorted(files.items()))


def select_sources(project: Path, inventory: Path) -> list[tuple[Path, str]]:
    text = inventory.read_text(encoding="utf-8-sig")
    first, rest = text.split(SECTION2, 1)
    zip_listing, loose_listing = rest.split(SECTION3, 1)
    setup = [line.split("Archive:", 1)[1].strip()
             for line in first.splitlines() if line.startswith("Archive:")]
    if len(setup) != 1:
        raise ValueError("The report must identify exactly one setup ZIP.")
    names = [line.split(None, 8)[8] for line in zip_listing.splitlines() if line.startswith("-")]
    if len(names) != 31 or len(set(names)) != 31:
        raise ValueError("Expected exactly 31 distinct ZIP names in report section 2.")
    sources = [(Path(setup[0]), "publication_setup_zip")]
    results_dir = project / "2. Collections of Results" / "kleborate_results"
    for name in names:
        if Path(name).name != name or not name.lower().endswith(".zip"):
            raise ValueError(f"Invalid result ZIP filename: {name!r}")
        category = "analysis_starter_zip" if name == "Klebsiella_GitHub_Analysis_Starter.zip" else "result_bundle_zip"
        sources.append((results_dir / name, category))
    paths = [Path(line) for line in loose_listing.splitlines() if line.startswith("/")]
    if len(paths) != 45:
        raise ValueError("Expected exactly 45 explicit loose paths in report section 3.")
    for path in paths:
        relative = path.relative_to(project).as_posix()
        if path.suffix.lower() == ".tsv":
            category = "candidate_current_tsv" if relative.startswith("1. ALL PDG000000012.2573/") else "additional_draft_tsv"
        else:
            category = {".newick": "candidate_newick", ".txt": "native_result_txt", ".csv": "historical_csv"}.get(path.suffix.lower())
        if category is None:
            raise ValueError(f"Unexpected loose file type: {path}")
        sources.append((path, category))
    selected = []
    for raw, category in sources:
        path = checked_path(raw)
        relative = path.relative_to(project).as_posix()
        safe_relative(relative)
        if not path.is_file():
            raise ValueError(f"Missing source file: {path}")
        if path.stat().st_size > LIMIT:
            raise ValueError(f"Source exceeds 50 MiB; use a release asset for this file: {path}")
        selected.append((path, category))
    if len({p for p, _ in selected}) != 77 or Counter(c for _, c in selected) != Counter(EXPECTED):
        raise ValueError("Source identities/categories do not match the expected 77-file inventory.")
    return sorted(selected)


def zip_integrity(path: Path, relative: str) -> dict:
    row = {"path": relative, "status": "", "members": 0, "unsafe_member_count": 0, "detail": ""}
    try:
        with zipfile.ZipFile(path) as archive:
            members = archive.infolist()
            row["members"] = len(members)
            unsafe = []
            for member in members:
                name = member.filename.rstrip("/")
                try:
                    safe_relative(name)
                    mode = (member.external_attr >> 16) & 0o170000
                    if mode not in (0, stat.S_IFREG, stat.S_IFDIR):
                        raise ValueError("Special archive member")
                except ValueError:
                    unsafe.append(member.filename)
            row["unsafe_member_count"] = len(unsafe)
            if sum(m.file_size for m in members) > 1024**3:
                row.update(status="NOT_CRC_TESTED_EXPANSION_LIMIT", detail="Declared uncompressed size exceeds 1 GiB; original ZIP retained.")
            else:
                bad = archive.testzip()
                row.update(status="CRC_FAILURE" if bad else ("WARN_UNSAFE_MEMBERS" if unsafe else "PASS_CRC"), detail=bad or "")
            if unsafe:
                row["detail"] += " Unsafe member examples: " + json.dumps(unsafe[:10], ensure_ascii=False)
    except Exception as exc:
        # Corrupt compression streams can raise zlib/EOF errors as well as BadZipFile.
        row.update(status="UNREADABLE_ZIP", detail=type(exc).__name__ + ": " + str(exc))
    return row


def write_csv(path: Path, fields: list[str], rows: list[dict]) -> None:
    with path.open("x", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def verify(destination: Path) -> None:
    if not destination.is_dir():
        raise ValueError("Snapshot folder does not exist.")
    files = files_in(destination)
    sums = {}
    for line in (destination / SUMS).read_text(encoding="utf-8").splitlines():
        match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
        if not match:
            raise ValueError("Invalid checksum manifest line.")
        sha, name = match.groups()
        safe_relative(name)
        if name == SUMS or name in sums:
            raise ValueError("Duplicate/self-referential checksum entry.")
        sums[name] = sha
    if set(sums) != set(files) - {SUMS}:
        raise ValueError("Missing or unexpected snapshot files.")
    measurements = {name: digest(files[name]) for name in sums}
    if any(measurements[name][1] != sha for name, sha in sums.items()):
        raise ValueError("SHA-256 mismatch: the snapshot has changed.")
    with (destination / "FILE_MANIFEST.csv").open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != FIELDS:
            raise ValueError("Unexpected file manifest columns.")
        rows = list(reader)
    named = set()
    for row in rows:
        name = row["path"]
        safe_relative(row["source_relative_path"])
        if name != "original_files/" + row["source_relative_path"] or name in named:
            raise ValueError("Invalid/duplicate source manifest mapping.")
        named.add(name)
        if measurements.get(name) != (int(row["bytes"]), row["sha256"]):
            raise ValueError(f"Source manifest measurement mismatch: {name}")
    counts = Counter(row["category"] for row in rows)
    if counts != Counter(EXPECTED) or named != {n for n in files if n.startswith("original_files/")}:
        raise ValueError("Original file membership/categories differ from the expected inventory.")
    status = json.loads((destination / "SOURCE_STATUS.json").read_text(encoding="utf-8"))
    with (destination / "ZIP_INTEGRITY.csv").open(encoding="utf-8", newline="") as f:
        zips = list(csv.DictReader(f))
    if len(zips) != 32 or {r["path"] for r in zips} != {r["path"] for r in rows if r["path"].lower().endswith(".zip")}:
        raise ValueError("ZIP integrity report does not cover the selected 32 archives.")
    warnings = sum(r["status"] != "PASS_CRC" for r in zips)
    if (status.get("source_files") != 77 or status.get("category_counts") != dict(counts)
            or status.get("zip_warnings") != warnings or status.get("scientific_reproduction") != "NOT_RUN"
            or status.get("manuscript_quantities_validated") is not False):
        raise ValueError("Source status metadata is inconsistent.")
    print(f"PASS: all 77 original files and generated metadata match; nested ZIP warnings: {warnings}.")
    print("This is source-file integrity only. Scientific reproduction has not been run.")


def import_sources(project: Path, inventory: Path, destination: Path) -> None:
    if not project.is_dir() or not inventory.is_file():
        raise ValueError("Project folder or inventory report does not exist.")
    if destination.exists() or not destination.parent.is_dir():
        raise ValueError("Destination must be new and its parent must already exist.")
    if destination.is_relative_to(project) or project.is_relative_to(destination):
        raise ValueError("Create the import outside the original project.")
    selected = select_sources(project, inventory)  # Preflight every selected path and size.
    destination.mkdir()
    rows, zip_rows = [], []
    for source, category in selected:
        relative = source.relative_to(project).as_posix()
        name = "original_files/" + relative
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        size, sha = digest(source, target)
        if size > LIMIT or digest(target) != (size, sha):
            raise ValueError(f"Copy/size verification failed: {relative}")
        rows.append(dict(path=name, source_relative_path=relative, category=category, bytes=size, sha256=sha))
        if source.suffix.lower() == ".zip":
            zip_rows.append(zip_integrity(target, name))
    write_csv(destination / "FILE_MANIFEST.csv", FIELDS, rows)
    write_csv(destination / "ZIP_INTEGRITY.csv", list(zip_rows[0]), zip_rows)
    warnings = sum(r["status"] != "PASS_CRC" for r in zip_rows)
    status = {"schema_version": 1, "imported_utc": datetime.now(timezone.utc).isoformat(),
              "source_files": len(rows), "category_counts": dict(Counter(r["category"] for r in rows)),
              "inventory_report_sha256": digest(inventory)[1], "zip_warnings": warnings,
              "scientific_reproduction": "NOT_RUN", "manuscript_quantities_validated": False}
    (destination / "SOURCE_STATUS.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    (destination / ".gitignore").write_text("!original_files/\n!original_files/**\n", encoding="utf-8")
    (destination / ".gitattributes").write_text("* -text -filter -ident\n", encoding="utf-8")
    (destination / "README.md").write_text(
        "# Inventoried source evidence\n\n"
        "This snapshot preserves 77 existing source files at their original relative paths. "
        "It contains 17 candidate current TSV exports, one additional draft TSV, 22 candidate Newicks, "
        "four native result TXT tables, one historical CSV, 30 result ZIPs, one analysis starter ZIP "
        "and one publication setup ZIP. No archive was extracted or repaired.\n\n"
        "FILE_MANIFEST.csv records original file identities, sizes and SHA-256 hashes. "
        "SHA256SUMS covers the original files and generated metadata, excluding itself. "
        "ZIP_INTEGRITY.csv reports nested archive CRC/readability checks and unsafe-member warnings; "
        f"{warnings} archive(s) require review. Damaged archives remain as original evidence.\n\n"
        "This is a source import, not a validated manuscript release. No scientific analysis was run, "
        "no reported manuscript quantities were certified, and no tree or historical/current output "
        "selection was inferred from filenames. Assess the actual contents and provenance before analysis.\n",
        encoding="utf-8")
    (destination / SUMS).write_text("".join(f"{digest(path)[1]}  {name}\n" for name, path in files_in(destination).items()), encoding="utf-8")
    verify(destination)
    print("Import ready for review:", destination)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    imp = commands.add_parser("import")
    imp.add_argument("--project", required=True)
    imp.add_argument("--inventory", required=True)
    imp.add_argument("--destination", required=True)
    ver = commands.add_parser("verify")
    ver.add_argument("--destination", required=True)
    args = parser.parse_args()
    try:
        destination = checked_path(args.destination)
        if args.command == "import":
            import_sources(checked_path(args.project), checked_path(args.inventory), destination)
        else:
            verify(destination)
        return 0
    except (OSError, ValueError, KeyError, IndexError, UnicodeError) as exc:
        print(f"STOP: {exc}", file=sys.stderr)
        print("Do not commit an incomplete import. Originals were not modified; use a new destination after correcting the issue.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
