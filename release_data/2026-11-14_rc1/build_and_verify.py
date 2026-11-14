#!/usr/bin/env python3
"""Build a deterministic K. pneumoniae candidate and verify downloaded bytes.

Integrity verification is separate from rerunning the scientific analyses.
This program uses only the Python standard library and makes no network calls.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import tempfile
import zipfile


RELEASE_DIR = Path("release_data/2026-11-14_rc1")
EVIDENCE_NAME = "Kp_Updated_Results_Evidence_2026-11-08.zip"
EVIDENCE_SHA = "52020b53cf3de9074a4409267a18d13212bb994aafd0045378a5bd9595f42214"
EVIDENCE_SIZE = 16970397
SUPPLEMENT_NAME = "Kp_Antibiotics_Supplementary_Data.zip"
SUPPLEMENT_MEMBER = "Inputs/Kp_Antibiotics_Previous_Supplement.zip"
SUPPLEMENT_SHA = "506ef83f08865843a54266a6460f973fbac308065aa6bc6645d3d8611114fffb"
SUPPLEMENT_SIZE = 6790246
MANIFEST_NAME = "SHA256SUMS.txt"
REQUIRED_METADATA = (
    "INPUT_MANIFEST.json", "release_scope.json", "manuscript_identity.json",
    "scientific_verification.json", "README_RELEASE.txt", "build_and_verify.py",
)
OPTIONAL_METADATA = (
    "reproduction_report.json", "manuscript_scope_check.txt",
    "latest_figure/Figure_1_latest_extracted_from_manuscript.jpeg",
    "latest_figure/PROVENANCE.json",
)
HEX_SHA = re.compile(r"^[0-9a-f]{64}$")
MAX_UNCOMPRESSED = 2 * 1024 ** 3


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def safe_name(name: str, directory: bool = False) -> str:
    if not isinstance(name, str) or not name or "\\" in name or "\x00" in name:
        raise ValueError(f"Unsafe path: {name!r}")
    if directory:
        name = name.rstrip("/")
    parts = name.split("/")
    if any(p in ("", ".", "..") or ":" in p for p in parts):
        raise ValueError(f"Unsafe path: {name!r}")
    if PurePosixPath(name).is_absolute():
        raise ValueError(f"Absolute path: {name!r}")
    return name


def contained_file(root: Path, relative: str) -> Path:
    safe_name(relative)
    candidate = root / relative
    resolved = candidate.resolve(strict=True)
    if not resolved.is_relative_to(root.resolve()):
        raise ValueError(f"Path escapes repository: {relative}")
    if candidate.is_symlink() or not resolved.is_file():
        raise ValueError(f"Expected ordinary file: {relative}")
    return resolved


def json_object(data: bytes, name: str) -> dict:
    obj = json.loads(data.decode("utf-8"))
    if not isinstance(obj, dict):
        raise ValueError(f"Expected JSON object: {name}")
    return obj


def sha_expectation(value: str) -> str:
    if not isinstance(value, str) or not HEX_SHA.fullmatch(value):
        raise ValueError("Expected a lower-case 64-character SHA-256")
    return value


def checked_zip(z: zipfile.ZipFile) -> dict[str, zipfile.ZipInfo]:
    files = {}
    names = set()
    total_size = 0
    for item in z.infolist():
        canonical = safe_name(item.filename, item.is_dir())
        if canonical in names:
            raise ValueError(f"Duplicate ZIP path: {canonical}")
        names.add(canonical)
        mode = item.external_attr >> 16
        kind = stat.S_IFMT(mode)
        if kind not in (0, stat.S_IFREG, stat.S_IFDIR) or stat.S_ISLNK(mode):
            raise ValueError(f"Unsupported ZIP file type: {item.filename}")
        if item.flag_bits & 1:
            raise ValueError(f"Encrypted ZIP member: {item.filename}")
        total_size += item.file_size
        if total_size > MAX_UNCOMPRESSED:
            raise ValueError("ZIP exceeds allowed uncompressed size")
        if not item.is_dir():
            files[item.filename] = item
    for name in files:
        parent = PurePosixPath(name).parent
        while str(parent) != ".":
            if str(parent) in files:
                raise ValueError(f"File/directory path conflict: {name}")
            parent = parent.parent
    bad = z.testzip()
    if bad is not None:
        raise ValueError(f"ZIP CRC failure: {bad}")
    return files


def checked_manifest_zip(path: Path) -> dict:
    with zipfile.ZipFile(path) as z:
        files = checked_zip(z)
        if MANIFEST_NAME not in files:
            raise ValueError(f"Missing {MANIFEST_NAME} in {path.name}")
        expected = {}
        for lineno, line in enumerate(z.read(MANIFEST_NAME).decode("utf-8").splitlines(), 1):
            if not line.strip():
                continue
            if len(line) < 67 or line[64:66] not in ("  ", " *"):
                raise ValueError(f"Malformed checksum line {lineno} in {path.name}")
            digest, name = sha_expectation(line[:64]), safe_name(line[66:])
            if name == MANIFEST_NAME or name in expected:
                raise ValueError(f"Duplicate/self-referencing checksum: {name}")
            expected[name] = digest
        payload_names = set(files) - {MANIFEST_NAME}
        if set(expected) != payload_names:
            missing = sorted(payload_names - set(expected))
            extra = sorted(set(expected) - payload_names)
            raise ValueError(f"Checksum coverage mismatch in {path.name}: missing={missing}, extra={extra}")
        for name, digest in expected.items():
            h = hashlib.sha256()
            with z.open(name) as source:
                for data in iter(lambda: source.read(1024 * 1024), b""):
                    h.update(data)
            if h.hexdigest() != digest:
                raise ValueError(f"Checksum mismatch in {path.name}: {name}")
    return {"archive": path.name, "sha256": sha256_file(path),
            "size_bytes": path.stat().st_size, "files_verified": len(expected),
            "manifest_exact_coverage": True, "zip_crc": "PASS", "status": "PASS"}


def put_file(path: Path, data: bytes) -> None:
    """Never silently replace a conflicting retained build or report."""
    if path.exists():
        if not path.is_file() or path.read_bytes() != data:
            raise FileExistsError(f"Existing output differs: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as target:
        target.write(data)


def write_json(path: Path, obj: dict) -> None:
    put_file(path, (json.dumps(obj, indent=2, ensure_ascii=False, sort_keys=True) + "\n").encode())


def reassemble(root: Path, manifest: dict, output: Path) -> Path:
    if manifest.get("schema_version") != 1:
        raise ValueError("Unsupported input manifest schema_version")
    archive = manifest["archive"]
    if archive.get("name") != EVIDENCE_NAME or archive.get("sha256") != EVIDENCE_SHA or archive.get("size_bytes") != EVIDENCE_SIZE:
        raise ValueError("Input manifest does not identify the frozen evidence archive")
    parts = archive.get("chunks")
    if not isinstance(parts, list) or not parts:
        raise ValueError("No ordered archive chunks in manifest")
    output.mkdir(parents=True, exist_ok=True)
    target = output / EVIDENCE_NAME
    seen = set()
    h = hashlib.sha256()
    size = 0
    with tempfile.TemporaryFile() as combined:
        for part in parts:
            relative = part["path"]
            if relative in seen:
                raise ValueError(f"Duplicate chunk path: {relative}")
            seen.add(relative)
            data = contained_file(root, relative).read_bytes()
            if len(data) != part["size_bytes"] or sha256_bytes(data) != sha_expectation(part["sha256"]):
                raise ValueError(f"Chunk integrity failure: {relative}")
            combined.write(data)
            h.update(data)
            size += len(data)
        if size != EVIDENCE_SIZE or h.hexdigest() != EVIDENCE_SHA:
            raise ValueError("Reassembled evidence archive identity mismatch")
        combined.seek(0)
        put_file(target, combined.read())
    return target


def deterministic_zip(destination: Path, contents: dict[str, bytes]) -> None:
    with tempfile.NamedTemporaryFile(dir=destination.parent, suffix=".zip", delete=False) as temporary:
        temporary_path = Path(temporary.name)
    try:
        with zipfile.ZipFile(temporary_path, "w", compression=zipfile.ZIP_STORED) as z:
            for name in sorted(contents):
                safe_name(name)
                item = zipfile.ZipInfo(name, date_time=(2026, 11, 14, 0, 0, 0))
                item.create_system = 3
                item.external_attr = (stat.S_IFREG | 0o644) << 16
                item.compress_type = zipfile.ZIP_STORED
                z.writestr(item, contents[name])
        put_file(destination, temporary_path.read_bytes())
    finally:
        temporary_path.unlink(missing_ok=True)


def build(args: argparse.Namespace) -> dict:
    root, output = args.repo_root.resolve(), args.output.resolve()
    release = root / RELEASE_DIR
    metadata = {}
    for name in REQUIRED_METADATA:
        metadata[name] = contained_file(root, (RELEASE_DIR / name).as_posix()).read_bytes()
    for name in OPTIONAL_METADATA:
        if (release / name).exists():
            metadata[name] = contained_file(root, (RELEASE_DIR / name).as_posix()).read_bytes()
    for name, data in metadata.items():
        if name.endswith(".json"):
            json_object(data, name)
    manifest = json_object(metadata["INPUT_MANIFEST.json"], "INPUT_MANIFEST.json")
    evidence = reassemble(root, manifest, output)
    evidence_result = checked_manifest_zip(evidence)
    with zipfile.ZipFile(evidence) as z:
        supplement_data = z.read(SUPPLEMENT_MEMBER)
    if len(supplement_data) != SUPPLEMENT_SIZE or sha256_bytes(supplement_data) != SUPPLEMENT_SHA:
        raise ValueError("Nested supplementary archive identity mismatch")
    supplement = output / SUPPLEMENT_NAME
    put_file(supplement, supplement_data)
    supplement_result = checked_manifest_zip(supplement)
    payload = {EVIDENCE_NAME: evidence.read_bytes(), SUPPLEMENT_NAME: supplement_data, **metadata}
    payload[MANIFEST_NAME] = "".join(
        f"{sha256_bytes(data)}  {name}\n" for name, data in sorted(payload.items())
    ).encode("utf-8")
    master_name = safe_name(manifest.get("master_archive_name", "Kp_Manuscript_Release_Candidate_2026-11-14.zip"))
    if "/" in master_name or not master_name.endswith(".zip") or master_name in payload:
        raise ValueError("master_archive_name must be a new ZIP basename")
    destination = output / master_name
    deterministic_zip(destination, payload)
    master_result = checked_manifest_zip(destination)
    put_file(output / (master_name + ".sha256"), f"{master_result['sha256']}  {master_name}\n".encode())
    result = {"status": "PASS", "operation": "build", "master": master_result,
              "inner_archives": [evidence_result, supplement_result],
              "scientific_analysis_rerun_by_this_builder": False,
              "scientific_scope": "See scientific_verification.json; building and checksums do not rerun analyses."}
    write_json(output / "BUILD_VERIFICATION.json", result)
    return result


def equal_files(a: Path, b: Path) -> bool:
    if a.stat().st_size != b.stat().st_size:
        return False
    with a.open("rb") as left, b.open("rb") as right:
        while True:
            first, second = left.read(1024 * 1024), right.read(1024 * 1024)
            if first != second:
                return False
            if not first:
                return True


def verify(args: argparse.Namespace) -> dict:
    expected = sha_expectation(args.expected_sha256)
    archive = args.archive.resolve(strict=True)
    actual = sha256_file(archive)
    if actual != expected:
        raise ValueError("Downloaded archive SHA-256 does not match retained build expectation")
    if args.expected_file and archive.samefile(args.expected_file.resolve(strict=True)):
        raise ValueError("Use separate retained and downloaded files for byte comparison")
    if args.expected_file and not equal_files(archive, args.expected_file.resolve(strict=True)):
        raise ValueError("Downloaded archive differs byte-for-byte from retained build")
    outer_result = checked_manifest_zip(archive)
    with zipfile.ZipFile(archive) as z:
        members = set(z.namelist())
        required = set(REQUIRED_METADATA) | {EVIDENCE_NAME, SUPPLEMENT_NAME, MANIFEST_NAME}
        if not required <= members or members - required - set(OPTIONAL_METADATA):
            raise ValueError("Unexpected or missing master-archive entries")
        scope = json_object(z.read("release_scope.json"), "release_scope.json")
        science = json_object(z.read("scientific_verification.json"), "scientific_verification.json")
        json_object(z.read("manuscript_identity.json"), "manuscript_identity.json")
        inner_results = []
        with tempfile.TemporaryDirectory(prefix="kp-download-check-") as temp:
            for name, expected_sha, expected_size in (
                (EVIDENCE_NAME, EVIDENCE_SHA, EVIDENCE_SIZE),
                (SUPPLEMENT_NAME, SUPPLEMENT_SHA, SUPPLEMENT_SIZE),
            ):
                data = z.read(name)
                if sha256_bytes(data) != expected_sha or len(data) != expected_size:
                    raise ValueError(f"Frozen archive identity mismatch: {name}")
                target = Path(temp) / name
                target.write_bytes(data)
                inner_results.append(checked_manifest_zip(target))
            with zipfile.ZipFile(Path(temp) / EVIDENCE_NAME) as evidence:
                if sha256_bytes(evidence.read(SUPPLEMENT_MEMBER)) != SUPPLEMENT_SHA:
                    raise ValueError("Evidence's nested supplement does not match standalone supplement")
    result = {"status": "PASS", "operation": "verify", "archive": outer_result,
              "expected_sha256": expected,
              "retained_build_byte_comparison": "PASS" if args.expected_file else "NOT_REQUESTED",
              "inner_archives": inner_results, "release_scope": scope,
              "scientific_verification_record": science,
              "scientific_analysis_rerun_by_this_verifier": False,
              "scientific_scope": "This verifier proves archive integrity. Scientific rerun evidence is recorded separately; it does not establish full manuscript reproducibility."}
    write_json(args.report, result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    builder = sub.add_parser("build", help="Reassemble frozen inputs and build deterministic master ZIP")
    builder.add_argument("--repo-root", type=Path, required=True)
    builder.add_argument("--output", type=Path, required=True)
    builder.set_defaults(func=build)
    checker = sub.add_parser("verify", help="Verify a separately downloaded master ZIP")
    checker.add_argument("--archive", type=Path, required=True)
    checker.add_argument("--expected-sha256", required=True)
    checker.add_argument("--expected-file", type=Path)
    checker.add_argument("--report", type=Path, required=True)
    checker.set_defaults(func=verify)
    args = parser.parse_args()
    try:
        result = args.func(args)
    except (OSError, ValueError, KeyError, TypeError, zipfile.BadZipFile) as error:
        parser.exit(1, f"FAIL: {error}\n")
    print(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
