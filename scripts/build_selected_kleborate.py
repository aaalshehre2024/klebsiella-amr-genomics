#!/usr/bin/env python3
"""Build an accession-level extract from one of two checksummed Kleborate ZIPs."""
import argparse
import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path, PurePosixPath
from zipfile import ZipFile

SOURCES = {
    "3fdfd66498b31b12b103b09726572800692cbd07ae747d6b4ce8e98d28fe9dab":
        ("610", "PDS000052355.137", 503, 0),
    "e37a999cc08118b0fdf1ff9d298f9884cb9979f7be9f5c3a8d97ec2000ac2389":
        ("548", "PDS000041740.207", 430, 429),
}
LOG_FIELDS = ("strain species N50 ST virulence_score resistance_score "
              "num_resistance_classes num_resistance_genes").split()
RESULT_METADATA = ["assembly_accession", "source_member", "source_line"]
ACCESSION = re.compile(r"^(GC[AF]_[0-9]+\.[0-9]+)(?=[^0-9]|$)")
MANIFEST = "all_available_fasta_paths_unique.txt"
RAW_PATHS = "all_available_fasta_paths.txt"
ARCHIVES = "zip_paths_clean.txt"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def accession(name):
    match = ACCESSION.match(name)
    require(match, f"No leading versioned assembly accession in {name}")
    return match.group(1)


def write_table(path, headers, rows):
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=headers, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def index_results(rows):
    indexed = {r["assembly_accession"]: r for r in rows}
    require(len(indexed) == len(rows), "Repeated accession in a source of result rows")
    return indexed


def get_tables(zipfile, members):
    rows, diagnostics = [], []
    fields = None
    for member in members:
        saw_header = False
        for n, line in enumerate(zipfile.read(member).decode("utf-8").splitlines(), 1):
            values = line.split("\t")
            if values[0] == "strain":
                require(not saw_header, f"Repeated header: {member}:{n}")
                require(fields is None or fields == values, f"Inconsistent header: {member}:{n}")
                fields = values
                saw_header = True
            elif ACCESSION.match(values[0]):
                require(saw_header and len(values) == len(fields), f"Malformed row: {member}:{n}")
                row = dict(zip(fields, values))
                row.update(assembly_accession=accession(row["strain"]), source_member=member, source_line=n)
                rows.append(row)
            else:
                diagnostics.append(dict(source_member=member, source_line=n, source_text=line))
        require(saw_header, f"Missing header: {member}")
    return fields, rows, diagnostics


def build(source, dest):
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    require(digest in SOURCES, f"Unrecognized source ZIP SHA-256: {digest}")
    label, pds, n_inputs, n_main = SOURCES[digest]
    with ZipFile(source) as z:
        require(z.testzip() is None, "ZIP integrity check failed")
        members = sorted(n for n in z.namelist() if not n.endswith("/"))
        member_rows = [dict(member=n, size_bytes=z.getinfo(n).file_size,
                            sha256=hashlib.sha256(z.read(n)).hexdigest()) for n in members]
        log_members = [n for n in members if n.startswith("batch_logs/") and n.endswith(".log")]
        main_members = [n for n in members if n.endswith("_complex_output.txt")]
        require(len(main_members) == int(n_main > 0), "Unexpected number of main tables")
        log_fields, log_rows, diagnostics = get_tables(z, log_members)
        require(log_fields == LOG_FIELDS, "Unexpected log fields")
        log_by_id = index_results(log_rows)
        main_fields, main_rows, main_diagnostics = get_tables(z, main_members)
        require(not main_diagnostics and len(main_rows) == n_main, "Unexpected main table content")
        main_by_id = index_results(main_rows)
        if n_main:
            require(set(main_by_id) == set(log_by_id), "Mismatch between main and log accessions")
            for aid, row in main_by_id.items():
                require(all(row[k] == log_by_id[aid][k] for k in LOG_FIELDS),
                        f"Main/log field disagreement: {aid}")

        raw_paths = z.read(RAW_PATHS).decode().splitlines()
        chosen_paths = z.read(MANIFEST).decode().splitlines()
        require(len(set(raw_paths)) == len(raw_paths), "Repeated identical raw path")
        require(set(chosen_paths) <= set(raw_paths), "Selected path absent from original path list")
        chosen_lines = {s: n for n, s in enumerate(chosen_paths, 1)}
        source_paths = z.read(ARCHIVES).decode().splitlines()
        # Retain only archive basenames, omitting the original workstation path.
        archive_index = {}
        for n, path in enumerate(source_paths, 1):
            name = PurePosixPath(path).name
            stem = PurePosixPath(name).stem
            require(stem not in archive_index, f"Repeated source ZIP basename stem: {stem}")
            archive_index[stem] = (n, name)

        path_rows, manifest_rows = [], []
        chosen_ids = set()
        path_counts = Counter(accession(PurePosixPath(s).name) for s in raw_paths)
        used_archive_stems = set()
        for n, raw in enumerate(raw_paths, 1):
            path = PurePosixPath(raw)
            require(path.parts[0] == "unzipped" and not path.is_absolute(), "Non-relative FASTA path")
            aid = accession(path.name)
            outer = path.parts[1]
            # One unpacked directory keeps the '.Zip' extension; both source names are preserved.
            outer_stem = outer[:-4] if outer.lower().endswith(".zip") else outer
            archive_line, archive_name = archive_index[outer_stem]
            used_archive_stems.add(outer_stem)
            outer_id = accession(outer)
            path_rows.append(dict(
                assembly_accession=aid, fasta_relative_path=raw, raw_manifest_line=n,
                selected_manifest_line=chosen_lines.get(raw, ""), source_archive_basename=archive_name,
                archive_list_line=archive_line, outer_label_accession=outer_id,
                outer_label_differs_from_fasta=int(aid != outer_id)))
            if raw not in chosen_lines:
                continue
            require(aid not in chosen_ids, f"Duplicate selected assembly: {aid}")
            chosen_ids.add(aid)
            logged = log_by_id.get(aid, {})
            main = main_by_id.get(aid, {})
            if logged:
                require(path.stem == logged["strain"], f"FASTA basename and reported strain disagree: {aid}")
            status = "full_main" if main else ("abbreviated_log_only" if logged else "technical_unresolved")
            manifest_rows.append(dict(
                assembly_accession=aid, selected_manifest_line=chosen_lines[raw], fasta_filename=path.name,
                selected_outer_label_accession=outer_id, raw_path_count=path_counts[aid],
                record_status=status, main_source_member=main.get("source_member", ""),
                main_source_line=main.get("source_line", ""), log_source_member=logged.get("source_member", ""),
                log_source_line=logged.get("source_line", "")))
        require(used_archive_stems == set(archive_index), "Unmatched source ZIP names")
        require(len(chosen_ids) == n_inputs == len(chosen_paths), "Input denominator mismatch")
        require(set(log_by_id) <= chosen_ids, "Result accession outside selected manifest")
        unresolved = chosen_ids - set(log_by_id)
        skipped_members = [n for n in members if n.endswith("_excluded_or_skipped_fasta_paths.txt")]
        if label == "548":
            require(unresolved == {"GCA_054407865.1"} and len(skipped_members) == 1, "Unexpected unresolved set")
            skipped_paths = z.read(skipped_members[0]).decode().splitlines()
            require(len(skipped_paths) == 1 and skipped_paths[0] in chosen_paths
                    and accession(PurePosixPath(skipped_paths[0]).name) in unresolved,
                    "Skipped path is inconsistent with accession manifest")
            require(any("Syntax error" in d["source_text"] for d in diagnostics)
                    and any(skipped_paths[0] in d["source_text"] for d in diagnostics),
                    "Expected diagnostic evidence is missing")
        else:
            require(not unresolved and not diagnostics and not skipped_members, "Unexpected 610 diagnostics")

    manifest_rows.sort(key=lambda r: r["selected_manifest_line"])
    require(not dest.exists() or (dest.is_dir() and not any(dest.iterdir())), "Choose an empty destination")
    dest.mkdir(parents=True, exist_ok=True)
    write_table(dest / "source_members.tsv", list(member_rows[0]), member_rows)
    write_table(dest / "input_manifest.tsv", list(manifest_rows[0]), manifest_rows)
    write_table(dest / "input_path_evidence.tsv", list(path_rows[0]), path_rows)
    write_table(dest / "log_results.tsv", log_fields + RESULT_METADATA, log_rows)
    if main_rows:
        write_table(dest / "main_results.tsv", main_fields + RESULT_METADATA, main_rows)
    if diagnostics:
        write_table(dest / "diagnostic_lines.tsv", list(diagnostics[0]), diagnostics)
    audit = dict(collection_label=label, package_pds_label=pds, source_sha256=digest,
                 source_filename=source.name, crc_integrity="passed", non_directory_members=len(members),
                 source_archive_paths=len(source_paths), listed_fasta_paths=len(raw_paths),
                 selected_versioned_assembly_accessions=n_inputs, batch_logs=len(log_members),
                 log_rows=len(log_rows), full_main_rows=len(main_rows), main_source_columns=len(main_fields or []),
                 log_source_columns=len(log_fields), hamronization_table_supplied=False,
                 unresolved_accessions=sorted(unresolved), original_fasta_path_member=RAW_PATHS,
                 selected_input_member=MANIFEST, source_archive_list_member=ARCHIVES,
                 skipped_path_members=skipped_members,
                 selected_outer_label_differences=sum(a["selected_manifest_line"] != "" and
                     a["outer_label_differs_from_fasta"] for a in path_rows))
    (dest / "audit.json").write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    print(f"{label}: {len(manifest_rows)} inputs, {len(log_rows)} log rows, {len(main_rows)} main rows")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path, help="One original, checksummed input ZIP")
    parser.add_argument("output", type=Path, help="New or empty folder for the collection-specific extract")
    args = parser.parse_args()
    build(args.archive, args.output)
