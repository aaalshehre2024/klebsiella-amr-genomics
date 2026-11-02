#!/usr/bin/env python3
"""Audit explicitly selected Kleborate result archives. Python standard library only.
No archive extraction, biological reannotation, or implicit collection merging.
The JSON selection manifest records which output members belong to each package.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import csv
import gzip
import hashlib
import io
import itertools
import json
from pathlib import Path
import re
import zipfile

ACCESSION = re.compile(r"GC[AF]_\d+\.\d+")
LIST_ORDER_FIELDS = {"K_Missing_expected_genes", "O_Missing_expected_genes"}


def accession(value: str) -> str:
    name = value.strip().replace("\\", "/").rsplit("/", 1)[-1]
    leading = ACCESSION.match(name)
    if leading:
        return leading.group()
    matches = set(ACCESSION.findall(value))
    return next(iter(matches)) if len(matches) == 1 else ""


def strain_name(value: str) -> str:
    name = value.strip().replace("\\", "/").rsplit("/", 1)[-1]
    return re.sub(r"\.(fna|fasta|fa)(\.gz)?$", "", name, flags=re.I)


def parse_tsv(text: str):
    rows = [r for r in csv.reader(io.StringIO(text), delimiter="\t") if any(r)]
    if not rows:
        return [], []
    header = rows[0]
    if len(header) != len(set(header)):
        raise ValueError("Repeated column names")
    result = []
    for line, row in enumerate(rows[1:], 2):
        if row == header:
            raise ValueError(f"Repeated header at record {line}")
        if len(row) != len(header):
            raise ValueError(f"Wrong column count at record {line}: {len(row)} != {len(header)}")
        result.append((line, dict(zip(header, row))))
    return header, result


def comparable(row: dict) -> str:
    # Only documented set/list-order variation is normalized for conflict detection.
    # Duplicated tokens, marker flags, alleles, and all other fields are retained.
    copy = dict(row)
    for field in LIST_ORDER_FIELDS:
        if field in copy:
            copy[field] = ";".join(sorted(copy[field].split(";")))
    return json.dumps(copy, sort_keys=True, ensure_ascii=False)


def write_table(path: Path, rows: list[dict], fields=None):
    if fields is None:
        fields = list(dict.fromkeys(k for row in rows for k in row))
    print("Writing", path.name, len(rows), "records", flush=True)
    path.parent.mkdir(parents=True, exist_ok=True)
    opener = gzip.open if path.suffix == ".gz" else open
    sep = "\t" if ".tsv" in path.name else ","
    with opener(path, "wt", newline="", encoding="utf-8", **({"compresslevel": 1} if path.suffix == ".gz" else {})) as handle:
        writer = csv.writer(handle, delimiter=sep)
        writer.writerow(fields)
        writer.writerows(([row.get(key, "") for key in fields] for row in rows))


def audit(input_dir: Path, manifest: Path, output_dir: Path):
    if output_dir.exists():
        raise FileExistsError(f"Refusing to overwrite {output_dir}")
    specs = json.loads(manifest.read_text(encoding="utf-8"))
    if not specs:
        raise ValueError("Empty manifest")
    output_dir.mkdir(parents=True)
    inventory, members, issues, log_evidence, excluded_members = [], [], [], [], []
    reconciled, log_only, main_raw, hamr_raw, distributions = [], [], [], [], []
    raw_by_id, rows_by_package = defaultdict(list), {}
    h_by_profile = defaultdict(set)
    h_examples = {}
    h_header = []
    main_header = []

    def issue(pid, severity, code, detail):
        issues.append(dict(package_id=pid, severity=severity, code=code, detail=detail))

    for spec in specs:
        pid, filename = spec["package_id"], spec["filename"]
        path = input_dir / filename
        item = dict(package_id=pid, label=spec["label"], filename=filename,
                    declared_identifier=spec["declared_database_identifier"],
                    identifier_verified=False, archive_status="NOT_READ",
                    input_manifest_records=None, input_unique_strains=None,
                    main_records=0, main_unique_assemblies=0, log_only_records=0,
                    input_without_main=None, main_not_in_input=None,
                    hamr_records=0, hamr_exact_unique_rows=0, hamr_exact_duplicate_rows=0,
                    hamr_assembly_ids=0, main_without_hamr=None,
                    reported_input_count=spec.get("reported_input_count"),
                    reported_omitted_count=spec.get("reported_omitted_count"),
                    main_member=spec.get("main_member", ""), hamr_member=spec.get("hamr_member", ""))
        inventory.append(item)
        try:
            blob = path.read_bytes()
            item.update(archive_bytes=len(blob), archive_sha256=hashlib.sha256(blob).hexdigest())
            if spec.get("sha256") and spec["sha256"] != item["archive_sha256"]:
                raise ValueError("Archive SHA-256 differs from frozen manifest")
            with zipfile.ZipFile(io.BytesIO(blob)) as archive:
                files = [x for x in archive.infolist() if not x.is_dir()]
                if sum(x.file_size for x in files) > 1_000_000_000:
                    raise ValueError("Archive exceeds audit size limit")
                bad = archive.testzip()
                if bad:
                    raise ValueError(f"CRC failure in {bad}")
                texts = {}
                for info in files:
                    data = archive.read(info)
                    members.append(dict(package_id=pid, member=info.filename, bytes=len(data),
                                        sha256=hashlib.sha256(data).hexdigest(),
                                        zip_member_time="-".join(map(str, info.date_time)),
                                        selected_main=info.filename == item["main_member"],
                                        selected_hamr=info.filename == item["hamr_member"]))
                    texts[info.filename] = data.decode("utf-8-sig")
            item["archive_status"] = "READABLE_CRC_PASS"
        except (OSError, ValueError, zipfile.BadZipFile, UnicodeError) as exc:
            item["archive_status"] = "UNREADABLE_OR_INVALID"
            item["archive_error"] = f"{type(exc).__name__}: {exc}"
            issue(pid, "BLOCKING", "ARCHIVE_UNREADABLE", item["archive_error"])
            continue

        for name in texts:
            if "klebsiella_pneumo_complex_output" in name and name.endswith(".txt") and name != item["main_member"]:
                excluded_members.append(dict(package_id=pid, member=name,
                    reason=spec.get("selection_note") or "Not selected in explicit manifest"))
                issue(pid, "REVIEW", "EXTRA_MAIN_TABLE", name)

        # Main table: logs never stand in for the full table.
        m_rows = []
        if item["main_member"]:
            header, parsed = parse_tsv(texts[item["main_member"]])
            if not main_header:
                main_header = header
            elif header != main_header:
                raise ValueError(f"Main schema mismatch in {pid}")
            for line, row in parsed:
                aid = accession(row.get("strain", ""))
                if not aid:
                    raise ValueError(f"Unresolved assembly identifier in {pid} record {line}")
                if len(set(ACCESSION.findall(row["strain"]))) > 1:
                    issue(pid, "REVIEW", "ADDITIONAL_ACCESSION_IN_ASSEMBLY_NAME", row["strain"] + "; leading accession used, embedded alias not merged")
                wrapped = dict(package_id=pid, source_member=item["main_member"],
                               source_record=line, assembly_accession=aid, **row)
                main_raw.append(wrapped)
                raw_by_id[aid].append((pid, row))
                m_rows.append(row)
        else:
            issue(pid, "BLOCKING", "MAIN_OUTPUT_MISSING", "Do not reconstruct full genomic profiles from batch logs")
            found = {}
            for name, text in texts.items():
                if not name.endswith(".log"):
                    continue
                for line, string in enumerate(text.splitlines(), 1):
                    parts = string.split("\t")
                    if len(parts) == 8 and ACCESSION.match(parts[0]) and parts[2].isdigit():
                        cols = ["strain", "species", "N50", "ST", "virulence_score", "resistance_score",
                                "num_resistance_classes", "num_resistance_genes"]
                        found.setdefault(parts[0], dict(package_id=pid, source_member=name,
                            source_record=line, evidence_tier="LOG_ONLY_NOT_FULL_OUTPUT", **dict(zip(cols, parts))))
            log_only.extend(found.values())
            item["log_only_records"] = len(found)
        rows_by_package[pid] = m_rows
        strains = {r["strain"] for r in m_rows}
        item["main_records"] = len(m_rows)
        item["main_unique_assemblies"] = len({accession(r["strain"]) for r in m_rows})
        if len(m_rows) != item["main_unique_assemblies"]:
            issue(pid, "REVIEW", "MAIN_DUPLICATES", "Multiple main rows per accession; examine provenance")

        # Input lists are compared by complete filename stem, preserving accession versions.
        input_member = spec.get("input_member", "")
        if input_member:
            lines = [x.strip() for x in texts[input_member].splitlines() if x.strip()]
            input_names = {strain_name(x) for x in lines}
            item.update(input_manifest_records=len(lines), input_unique_strains=len(input_names),
                        input_without_main=len(input_names - strains), main_not_in_input=len(strains - input_names))
            for name in sorted(input_names | strains):
                reconciled.append(dict(package_id=pid, strain=name, assembly_accession=accession(name),
                    in_input=name in input_names, in_main=name in strains,
                    status="MATCHED" if name in input_names & strains else
                           "INPUT_WITHOUT_FULL_OUTPUT" if name in input_names else "OUTPUT_NOT_IN_INPUT"))
            if input_names - strains:
                issue(pid, "BLOCKING", "INPUT_WITHOUT_FULL_OUTPUT", str(len(input_names - strains)))
            if strains - input_names:
                issue(pid, "BLOCKING", "OUTPUT_OUTSIDE_INPUT", str(len(strains - input_names)))
        else:
            issue(pid, "REVIEW", "INPUT_MANIFEST_MISSING", "Reported counts cannot replace an accession-level input list")
        if spec.get("reported_omitted_count"):
            issue(pid, "REVIEW", "UNIDENTIFIED_OMITTED_INPUTS", str(spec["reported_omitted_count"]) + " claimed omissions; identifiers/reasons not supplied")

        h_rows = []
        if item["hamr_member"]:
            header, parsed = parse_tsv(texts[item["hamr_member"]])
            if not h_header:
                h_header = header
            elif header != h_header:
                raise ValueError(f"hAMR schema mismatch in {pid}")
            for line, row in parsed:
                hamr_raw.append(dict(package_id=pid, source_member=item["hamr_member"], source_record=line, **row))
                key = tuple(row[x] for x in h_header)
                h_by_profile[key].add(pid)
                h_examples[key] = row
                h_rows.append(row)
            h_ids = {r["Input_file_name"] for r in h_rows}
            h_unique = {tuple(r[x] for x in h_header) for r in h_rows}
            item.update(hamr_records=len(h_rows), hamr_exact_unique_rows=len(h_unique),
                        hamr_exact_duplicate_rows=len(h_rows)-len(h_unique),
                        hamr_assembly_ids=len(h_ids), main_without_hamr=len(strains-h_ids),
                        hamr_unmatched_strains=len(h_ids-strains))
            if item["hamr_exact_duplicate_rows"]:
                issue(pid, "REVIEW", "EXACT_DUPLICATE_HAMR_ROWS", str(item["hamr_exact_duplicate_rows"]) + "; not independent copy-number evidence")
            if h_ids - strains:
                issue(pid, "BLOCKING", "HAMR_OUTSIDE_MAIN", str(len(h_ids-strains)))
        else:
            issue(pid, "REVIEW", "HAMR_OUTPUT_MISSING", "Main-field analyses may remain possible; detailed-hit analyses unavailable")

        # Record technical errors; never declare biological exclusions automatically.
        for name, text in texts.items():
            if name.endswith(".log"):
                for line, string in enumerate(text.splitlines(), 1):
                    if any(token in string for token in ("Syntax error:", "ERROR: could not open", "failed in check", "does not match any specified", "Traceback", "command not found")):
                        code = "SHELL_SYNTAX_ERROR" if "Syntax error:" in string else "FILE_OPEN_ERROR" if "ERROR: could not open" in string else "LOG_FAILURE_OR_SKIP"
                        log_evidence.append(dict(package_id=pid, source_member=name, line=line,
                            code=code, assembly_accession=accession(string),
                            note="Technical cause must be reviewed; this is not a confirmed biological exclusion"))
                        if code in {"SHELL_SYNTAX_ERROR", "FILE_OPEN_ERROR"}:
                            issue(pid, "BLOCKING", code, "Technical error in species-check workflow; inspect and retest input before biological exclusion")
            if name.endswith("bad_zip_files.txt"):
                for string in text.splitlines():
                    if string.strip():
                        issue(pid, "BLOCKING", "UPSTREAM_ARCHIVE_FAILED_CHECK", strain_name(string))
        for field in ("species", "species_match", "ST", "K_locus", "O_type", "resistance_score", "virulence_score", "QC_warnings"):
            for value, n in Counter(r[field] for r in m_rows).most_common():
                distributions.append(dict(package_id=pid, field=field, raw_value=value, n=n, denominator=len(m_rows)))
        item["software_versions_in_hamr"] = ";".join(sorted({r["Software_version"] for r in h_rows}))
        item["database_labels_in_hamr"] = ";".join(sorted({r["Reference_database_name"]+" "+r["Reference_database_version"] for r in h_rows}))
        if spec["declared_database_identifier"].startswith("PDG"):
            issue(pid, "REVIEW", "PDS_MEMBERSHIP_UNVERIFIED", "PDG organism-group label is not a PDS SNP-cluster assignment")

    overlap_rows, overlap_pairs, variations, unique_main, real_conflicts = [], [], [], [], []
    for aid, observations in sorted(raw_by_id.items()):
        packages = sorted({pid for pid, _ in observations})
        exact = {json.dumps(r, sort_keys=True) for _, r in observations}
        canonical = {comparable(r) for _, r in observations}
        if len(packages) > 1:
            overlap_rows.append(dict(assembly_accession=aid, package_ids=";".join(packages), n_packages=len(packages),
                                     exact_profile_variants=len(exact), comparable_profile_variants=len(canonical)))
        if len(exact) > 1:
            fields = [key for key in main_header if len({r[key] for _, r in observations}) > 1]
            variations.append(dict(assembly_accession=aid, package_ids=";".join(packages),
                                  fields=";".join(fields), order_only=len(canonical)==1))
        if len(canonical) > 1:
            real_conflicts.append(aid)
        else:
            # Preserve the first raw profile, not a rewritten biological call.
            unique_main.append(dict(assembly_accession=aid, source_packages=";".join(packages),
                raw_variant_count=len(exact), **observations[0][1]))
    for a, b in itertools.combinations(sorted(rows_by_package), 2):
        common = {accession(x["strain"]) for x in rows_by_package[a]} & {accession(x["strain"]) for x in rows_by_package[b]}
        if common:
            overlap_pairs.append(dict(package_a=a, package_b=b, shared_accessions=len(common)))
    paired = defaultdict(set)
    for aid in raw_by_id:
        paired[aid[4:]].add(aid)
    pairing_candidates = [dict(numeric_version=k, accessions=";".join(sorted(v)),
        action="VERIFY_NCBI_GCA_GCF_LINK; not auto-collapsed") for k,v in paired.items() if len(v)>1]
    unique_h = [dict(source_packages=";".join(sorted(h_by_profile[k])), **h_examples[k]) for k in h_by_profile]
    fields = lambda rows: list(dict.fromkeys(k for row in rows for k in row))
    tables = {
        "package_inventory.csv":inventory, "archive_member_inventory.csv":members,
        "qc_issues.csv":issues, "quarantined_members.csv":excluded_members,
        "input_output_reconciliation.csv":reconciled, "log_evidence.csv":log_evidence,
        "cross_package_overlap.csv":overlap_pairs, "overlapping_assemblies.csv":overlap_rows,
        "main_profile_variations.csv":variations, "gca_gcf_pairing_candidates.csv":pairing_candidates,
        "preliminary_raw_distributions.csv":distributions,
    }
    for name, rows in tables.items():
        write_table(output_dir/name, rows, fields(rows) or ["note"])
    write_table(output_dir/"main_package_records.tsv.gz",main_raw)
    write_table(output_dir/"unique_assembly_profiles.tsv.gz",unique_main)
    write_table(output_dir/"hamronization_package_records.tsv.gz",hamr_raw)
    write_table(output_dir/"hamronization_exact_row_deduplicated.tsv.gz",unique_h)
    write_table(output_dir/"log_only_records.tsv", log_only)
    summary = dict(packages_received=len(specs), readable_archives=sum(x["archive_status"]=="READABLE_CRC_PASS" for x in inventory),
        unreadable_archives=sum(x["archive_status"]!="READABLE_CRC_PASS" for x in inventory),
        packages_with_selected_main=sum(bool(x["main_member"]) and x["archive_status"]=="READABLE_CRC_PASS" for x in inventory),
        packages_with_selected_hamr=sum(bool(x["hamr_member"]) and x["archive_status"]=="READABLE_CRC_PASS" for x in inventory),
        main_package_records=len(main_raw), distinct_versioned_assembly_accessions=len(raw_by_id),
        repeated_accessions=len(overlap_rows), duplicate_main_observations=len(main_raw)-len(raw_by_id),
        raw_profile_variation_accessions=len(variations), substantive_main_profile_conflicts=len(real_conflicts),
        main_records_after_reconciliation=len(unique_main), gca_gcf_link_candidates=len(pairing_candidates),
        log_only_observations=len(log_only), hamr_package_rows=len(hamr_raw),
        hamr_exact_distinct_rows=len(unique_h), hamr_distinct_versioned_accessions=len({accession(r["Input_file_name"]) for r in unique_h}),
        excluded_extra_main_members=len(excluded_members),
        scope="Explicit checksum-distinct package manifest only; no unlisted earlier result archives appended; no final biological cohort established",
        status="PROVISIONAL_AUDIT_NOT_PUBLICATION_READY")
    (output_dir/"audit_summary.json").write_text(json.dumps(summary, indent=2),encoding="utf-8")
    (output_dir/"methods.json").write_text(json.dumps(dict(
        main_key="Exact GCA/GCF accession.version; paired accessions not collapsed",
        selected_outputs="Explicit package_selection.json; nonselected main outputs quarantined",
        list_order_only_fields=sorted(LIST_ORDER_FIELDS),
        missing_main="Logs kept in separate evidence tier; no imputation",
        hamr_dedup="Exact 32-column row equality only; all originals retained in provenance table",
        marker_parsing="Raw marker values preserved; no new resistance/virulence classification performed",
        dates="ZIP member timestamps are archive metadata, not verified download/collection dates",
        input_integrity="Checksums cover uploaded result ZIPs and members, not absent genome FASTAs",
    ),indent=2),encoding="utf-8")
    print(json.dumps(summary,indent=2))
    return summary

if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args=parser.parse_args()
    audit(args.input_dir,args.manifest,args.output_dir)
