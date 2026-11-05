"""Verify and extract the selected 610 update against the November 3 input manifest and logs."""
import argparse
import csv
import hashlib
import io
import json
import re
from collections import Counter
from pathlib import Path, PurePosixPath
from zipfile import ZipFile

ARCHIVE_HASH = "e53fc526598b0cdc873f78d1a620d2bff245881356d3e434fa09beb1cb716f6b"
PRIOR_MANIFEST_HASH = "a3c54bf6cec53c849bfa615d82ae7d223f6f54b4c344f908daed2b8fa108f7ae"
LOG_COLS = ["strain", "species", "N50", "ST", "virulence_score", "resistance_score",
            "num_resistance_classes", "num_resistance_genes"]
PROFILE = ["species", "species_match", "ST", "K_locus", "K_type", "K_locus_confidence",
           "K_locus_problems", "O_locus", "O_type", "O_locus_confidence", "O_locus_problems",
           "Bla_Carb_acquired", "Bla_ESBL_acquired", "Yersiniabactin", "Colibactin", "Aerobactin",
           "Salmochelin", "RmpADC", "rmpA2", "resistance_score", "virulence_score",
           "num_resistance_genes", "num_resistance_classes", "N50", "QC_warnings"]
PREFIX = "final_full_results/PDS000052355_137_610_FINAL_"
MAIN = PREFIX + "klebsiella_pneumo_complex_output.txt"
HAMR = PREFIX + "hAMRonization_output.txt"


def check(value, msg):
    if not value:
        raise ValueError(msg)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def accession(strain):
    m = re.match(r"^(GC[AF]_\d+\.\d+)(?:_|$)", strain)
    check(m, "Missing versioned assembly accession: " + strain)
    return m.group(1)


def table(data, member):
    fields, *body = [line.split("\t") for line in data.decode().splitlines()]
    check(all(fields) and len(set(fields)) == len(fields), f"Invalid header: {member}")
    check(all(len(r) == len(fields) for r in body), f"Wrong row width: {member}")
    return fields, [dict(zip(fields, r)) for r in body]


def by_strain(rows):
    result = {r["strain"]: r for r in rows}
    check(len(result) == len(rows), "Repeated strain")
    return result


def write_table(path, header, rows):
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)


def audit(source, previous, out):
    check(digest(source.read_bytes()) == ARCHIVE_HASH, "Unrecognized 610 upload")
    manifest = previous / "input_manifest.tsv"
    check(digest(manifest.read_bytes()) == PRIOR_MANIFEST_HASH, "Wrong previous manifest")
    _, prev_input = table(manifest.read_bytes(), manifest.name)
    prev_names = {r["assembly_accession"]:r["fasta_filename"] for r in prev_input}
    _, prev_log_rows = table((previous / "log_results.tsv").read_bytes(), "previous log")
    prev_log = by_strain(prev_log_rows)
    with ZipFile(source) as z:
        check(z.testzip() is None, "ZIP CRC failure")
        info = [i for i in z.infolist() if not i.is_dir()]
        check(len({i.filename for i in info}) == len(info), "Duplicate ZIP member name")
        inventory = [(i.filename, i.file_size, digest(z.read(i))) for i in sorted(info, key=lambda x:x.filename)]
        main_bytes, hamr_bytes = z.read(MAIN), z.read(HAMR)
        mcols, main = table(main_bytes, MAIN)
        hcols, hamr = table(hamr_bytes, HAMR)
        main_by_name = by_strain(main)
        batch = {}
        log_members = [i.filename for i in info if i.filename.endswith(".log")]
        for name in sorted(log_members):
            header, rows = table(z.read(name), name)
            check(header == LOG_COLS, "Unexpected log fields")
            for n, row in enumerate(rows, 2):
                s = row["strain"]
                check(s not in batch and s in main_by_name and s in prev_log, "Invalid batch strain: "+s)
                check(all(row[k] == main_by_name[s][k] == prev_log[s][k] for k in LOG_COLS),
                      "Main, new logs and historical logs disagree for " + s)
                batch[s] = (name,n)
        check(set(batch) == set(main_by_name) == set(prev_log), "Strain set drift")
        original_paths = z.read("all_available_fasta_paths.txt").decode().splitlines()
        paths = z.read("all_available_fasta_paths_unique.txt").decode().splitlines()
        check(paths == original_paths and len(set(paths)) == len(paths), "Input path list disagreement")
        archive_map = dict(line.split("\t") for line in z.read("qc/archive_folders.tsv").decode().splitlines())
        archives = z.read("zip_paths_clean.txt").decode().splitlines()
        check(len(archive_map) == len(paths) and set(archives) == set(archive_map.values()), "Source ZIP map drift")
        needles = ["final_full_results/excluded_or_skipped_assemblies.txt",
                   "qc/zip_folders_no_fasta.txt", "qc/bad_zip_files.txt"]
        check(all(not z.read(n).strip() for n in needles), "Nonempty source QC file")
    selected = {}
    for i, path in enumerate(paths, 1):
        p = PurePosixPath(path)
        stem = p.stem
        aid = accession(stem)
        outer = PurePosixPath(archive_map[str(PurePosixPath(*p.parts[:2]))]).stem
        check(aid not in selected and stem in main_by_name and p.name == prev_names.get(aid),
              "FASTA/main/historical membership mismatch")
        selected[aid] = (i,stem,outer)
    check(len(selected) == len(main) == len(prev_names) == 503 and set(selected) == set(prev_names), "Input count drift")
    hnames = Counter(r["Input_file_name"] for r in hamr)
    check(set(hnames) == set(main_by_name), "Unmatched AMR input_file_name")
    distinct = set()
    distinct_per = Counter()
    unique_lines = []
    for line, row in zip(hamr_bytes.splitlines(keepends=True)[1:], hamr):
        signature = tuple(row.values())
        if signature not in distinct:
            distinct.add(signature)
            distinct_per[row["Input_file_name"]] += 1
            unique_lines.append(line)
    check(len(mcols) == 117 and len(hcols) == 32, "Unexpected schema")
    check(len(hamr) == 13826 and len(distinct) == 8939, "Expected hAMR counts differ")
    check(all("/mnt/" not in value and "OneDrive" not in value for rows in [hamr,main] for r in rows for value in r.values()),"Workstation path in result table")
    out.mkdir(parents=True,exist_ok=True)
    (out / "main_results.tsv").write_bytes(main_bytes)
    (out / "hamronization.tsv").write_bytes(hamr_bytes)
    (out / "hamronization_exact_unique.tsv").write_bytes(hamr_bytes.splitlines(keepends=True)[0]+b"".join(unique_lines))
    write_table(out / "source_members.tsv",["member","size_bytes","sha256"],inventory)
    main_lines = {r["strain"]:i for i,r in enumerate(main,2)}
    cols = ["assembly_accession","previous_evidence","batch","strain","selected_manifest_line","source_archive_label","main_source_line",
            "log_member","log_line","hamr_raw_rows","hamr_exact_unique_rows"]
    rows = ([aid,"abbreviated_log_only",PurePosixPath(batch[s][0]).stem,s,i,outer,main_lines[s],*batch[s],hnames[s],distinct_per[s],
             *(main_by_name[s][k] for k in PROFILE)] for aid,(i,s,outer) in selected.items())
    write_table(out / "accession_profile.tsv",cols+PROFILE,rows)
    summary = {
        "collection_label":"610", "package_pds_label":"PDS000052355.137",
        "source_filename":source.name,"source_sha256":ARCHIVE_HASH,"source_crc":"passed",
        "published_2026_11_03_manifest_sha256":PRIOR_MANIFEST_HASH,"non_directory_members":len(inventory),
        "listed_input_accessions":len(selected),"main_source_columns":len(mcols),"main_rows":len(main),
        "detailed_amr_source_columns":len(hcols),"detailed_amr_rows_as_supplied":len(hamr),
        "exact_distinct_amr_rows":len(distinct),"amr_exact_repeat_observations":len(hamr)-len(distinct),
        "assemblies_with_main_and_detailed_amr":len(hnames),"missing_main_accessions":[],"missing_amr_accessions":[],
        "prior_main_rows":0,"prior_log_rows":len(prev_log),"prior_strain_and_accession_sets_match":True,
        "old_vs_new_log_and_main_shared_non_id_cells_compared":len(main)*(len(LOG_COLS)-1),
        "old_vs_new_shared_field_conflicts":0,"new_batch_logs":len(log_members),"new_log_rows":len(batch),
        "full_main_source_member":MAIN, "full_hamr_source_member":HAMR,
        "native_table_sha256":{"main_results.tsv":digest(main_bytes),"hamronization.tsv":digest(hamr_bytes)},
        "hAMR_origin":"Merged hAMRonization table as supplied. Batch-level hAMRonization files are absent; upstream merge not independently reconstructible from this archive.",
        "source_archive_outer_label_discrepancies":{aid:v[2] for aid,v in selected.items() if v[2]!=aid},
        "hAMR_reported_software_and_database":{k:dict(sorted(Counter(r[k] for r in hamr).items())) for k in
            ["Software_name","Software_version","Reference_database_name","Reference_database_version"]},
        "source_qc_files_empty":needles,"raw_main_field_distributions":{k:dict(sorted(Counter(r[k] for r in main).items())) for k in
            ["species","species_match","ST","QC_warnings","resistance_score","virulence_score","K_locus_confidence","O_locus_confidence"]},
        "non_dash_Bla_Carb_acquired_assemblies":sum(r["Bla_Carb_acquired"] not in ("","-") for r in main)
    }
    (out/"summary.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    print(f"610: {len(main)} main, {len(hamr)} detailed AMR, {len(hnames)} covered, {len(distinct)} exact-unique.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_zip",type=Path)
    parser.add_argument("previous_610_dir",type=Path)
    parser.add_argument("out_dir",type=Path)
    a=parser.parse_args()
    audit(a.source_zip, a.previous_610_dir, a.out_dir)
