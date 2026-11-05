#!/usr/bin/env python3
"""Rebuild the public, accession-linked profile from the exact November 548 result ZIP.

Usage: python3 build_548_profile.py NEW_ZIP OLD_548_PROFILE_DIR NEW_OUTPUT_DIR
The old profile directory provides the 3 Nov input_manifest.tsv and main_results.tsv.
"""
import argparse
import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path, PurePosixPath
from zipfile import ZipFile

SRC_SHA = "cddb0889eb1f1787ea2d76404024da73c4b38a729c70d69aee0ef8ab8a579723"
REF_SHA = "cea0dc02108ccdc6f6a56b76ae7e0b3d340e3dbc2e7338e8677cf48178e1d4a3"
OLD_MAIN_SHA = "b81b9b38873db636db8210c78c675d05c12d275b988f760daaa654497df6cf5a"
MAIN = "klebsiella_pneumo_complex_output.txt"
AMR = "klebsiella_pneumo_complex_hAMRonization_output.txt"
RESTORED = "GCA_054407865.1"
ID = re.compile(r"GC[AF]_[0-9]+\.[0-9]+")
PROFILE = ("species ST K_locus K_locus_confidence O_locus O_type O_locus_confidence "
           "Bla_Carb_acquired Bla_ESBL_acquired resistance_score virulence_score Yersiniabactin "
           "Colibactin Aerobactin Salmochelin RmpADC rmpA2 num_resistance_classes "
           "num_resistance_genes QC_warnings").split()

def digest(data):
    return hashlib.sha256(data).hexdigest()

def require(ok, message):
    if not ok:
        raise ValueError(message)

def table(raw):
    lines = raw.decode("utf-8").splitlines()
    h = lines[0].split("\t")
    require(len(set(h)) == len(h) and all(h), "Malformed header")
    rows = [line.split("\t") for line in lines[1:]]
    require(all(len(r) == len(h) for r in rows), "Row width mismatch")
    return h, [dict(zip(h, r)) for r in rows]

def emit(path, header, rows):
    with path.open("w", encoding="utf-8", newline="") as out:
        writer = csv.writer(out, delimiter="\t", lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)

def main(archive, prior, dest):
    require(digest(archive.read_bytes()) == SRC_SHA, "Rerun archive checksum mismatch")
    require(digest((prior / "input_manifest.tsv").read_bytes()) == REF_SHA, "Historical manifest checksum mismatch")
    require(digest((prior / "main_results.tsv").read_bytes()) == OLD_MAIN_SHA, "Historical main table checksum mismatch")
    _, hist_manifest = table((prior / "input_manifest.tsv").read_bytes())
    _, hist_main = table((prior / "main_results.tsv").read_bytes())
    old = {r["assembly_accession"]: r for r in hist_main}
    hids = {r["assembly_accession"] for r in hist_manifest}
    require(len(hids) == len(hist_manifest) == 430 and len(old) == len(hist_main) == 429
            and hids - old.keys() == {RESTORED}, "Historical accession set mismatch")
    with ZipFile(archive) as z:
        require(z.testzip() is None and len(set(z.namelist())) == len(z.namelist()), "ZIP integrity failure")
        def lines(name):
            return z.read(name).decode("utf-8").splitlines()
        unique = [PurePosixPath(f).stem for f in lines("qc/unique_fastas.txt")]
        require(len(unique) == 430 and set(unique) == hids, "New and historical inputs differ")
        inventory = [(i.filename, i.file_size, digest(z.read(i))) for i in z.infolist() if not i.is_dir()]
        require(not any(lines(n) for n in ["final/excluded_assemblies.txt", "qc/bad_zips.txt",
                                           "qc/review_fastas.txt"]), "Unresolved input or exclusion list")
        archives = dict(l.split("\t") for l in lines("qc/archives.tsv"))
        raw_paths = {l.split("\t")[1]: l.split("\t")[0] for l in lines("qc/genome_fastas.tsv")}
        normlines = [l.split("\t") for l in lines("qc/input_normalized_sha256.tsv")]
        hashes = {a: h for a,h,_ in normlines}
        require(set(hashes) == hids and len(normlines) == 430
                and all(re.fullmatch("[a-f0-9]{64}", h) and raw_paths[p] == a for a,h,p in normlines),
                "Staged genomic hashes do not reconcile")
        require(len(raw_paths) == 431 and set(raw_paths.values()) == hids, "Raw path count mismatch")
        genome_folders = {str(PurePosixPath(*PurePosixPath(p).parts[:2])) for p in raw_paths}
        require(len(archives) == 432 and set(archives.values()) == set(lines("qc/zips.txt")) and
                {archives[k] for k in archives.keys() - genome_folders} == set(lines("qc/no_genome_zips.txt")),
                "Genome and other archive membership mismatch")
        non_genome = [PurePosixPath(p).name for p in lines("qc/no_genome_zips.txt")]
        require(non_genome == ["PDS000041740_207_548_FINAL_kleborate_results.zip"], "Unexpected unrepresented archive")
        _, dups = table(z.read("qc/duplicates.tsv"))
        require(len(dups) == 1 and dups[0]["accession"] == RESTORED and
                raw_paths[dups[0]["kept_file"]] == raw_paths[dups[0]["duplicate_file"]] == RESTORED,
                "Unexpected duplicate inputs")

        srcmain, srcamr = z.read("final/" + MAIN), z.read("final/" + AMR)
        mh, mrows = table(srcmain)
        ah, arows = table(srcamr)
        keyed = {r["strain"]: r for r in mrows}
        require(len(mh) == 117 and len(ah) == 32 and len(mrows) == len(keyed) and set(keyed) == hids
                and all(ID.fullmatch(a) for a in keyed), "Full main table membership / schema mismatch")
        require(set(r["Input_file_name"] for r in arows) == hids, "Detailed AMR input coverage mismatch")
        batch_by_id, main_lines, hamr_lines = {}, [], []
        log_cell_count = 0
        batch_registry = []
        for bfile in sorted(n for n in z.namelist() if n.startswith("batch_lists/") and not n.endswith("/")):
            b = PurePosixPath(bfile).name
            prefix = "batches/" + b + "/" + PurePosixPath(lines(f"batches/{b}/VERIFIED")[0]).name
            planned = [PurePosixPath(f).stem for f in lines(bfile)]
            require(not batch_by_id.keys() & set(planned) and len(set(planned)) == len(planned)
                    and set(planned) <= hids, "Duplicate/unknown batch member")
            bm = z.read(prefix + "/out/" + MAIN).splitlines(keepends=True)
            ba = z.read(prefix + "/out/" + AMR).splitlines(keepends=True)
            require(bm[0] == srcmain.splitlines(keepends=True)[0] and ba[0] == srcamr.splitlines(keepends=True)[0],
                    "Batch headers differ from final tables")
            require({r.split(b"\t",1)[0].decode() for r in bm[1:]} == set(planned)
                    and {r.split(b"\t",1)[0].decode() for r in ba[1:]} == set(planned),
                    "Batch-result membership mismatch")
            main_lines.extend(bm[1:])
            hamr_lines.extend(ba[1:])
            lh, logs = table(z.read(prefix + "/run.log"))
            require(set(lh) <= set(mh) and len(lh) == 8 and len(logs) == len(planned) and
                    {r["strain"] for r in logs} == set(planned) and
                    all(all(v == keyed[r["strain"]][k] for k,v in r.items()) for r in logs),
                    "Batch/main log mismatch")
            require(not lines(prefix + "/excluded.txt"), "Batch has exclusions")
            log_cell_count += len(logs) * (len(lh) - 1)
            batch_by_id.update({a:b for a in planned})
            batch_registry.append({"batch": b, "inputs": len(planned), "main_rows": len(bm)-1, "hamr_rows": len(ba)-1})
        require(batch_by_id.keys() == hids, "Batches do not cover all declared inputs")
        require(b"".join(main_lines) == srcmain.split(b"\n",1)[1] and b"".join(hamr_lines) == srcamr.split(b"\n",1)[1],
                "Final outputs are not bytewise concatenations of original batch data rows")

    differing = []
    field_changes = Counter()
    for a in sorted(old):
        for k in mh:
            if k == "strain" or old[a][k] == keyed[a][k]:
                continue
            require(k in {"K_Missing_expected_genes","O_Missing_expected_genes"}
                    and sorted(old[a][k].split(";")) == sorted(keyed[a][k].split(";")),
                    f"Non-order-only profile change: {a} {k}")
            differing.append((a, k, old[a][k], keyed[a][k], "same_multiset_reordered"))
            field_changes[k] += 1
    ac = Counter(r["Input_file_name"] for r in arows)
    distinct = list(dict.fromkeys(hamr_lines))
    ac_unique = Counter(r.split(b"\t",1)[0].decode() for r in distinct)
    software = sorted({(r["Software_name"], r["Software_version"], r["Reference_database_name"],
                        r["Reference_database_version"]) for r in arows})
    dest.mkdir(parents=True, exist_ok=True)
    (dest/"main_results.tsv").write_bytes(srcmain)
    (dest/"hamronization.tsv").write_bytes(srcamr)
    (dest/"hamronization_exact_unique.tsv").write_bytes(srcamr.splitlines(keepends=True)[0]+b"".join(distinct))
    emit(dest/"source_members.tsv", ["source_member","size_bytes","sha256"], sorted(inventory))
    emit(dest/"prior_comparison.tsv", ["accession","field","historical_value","rerun_value","comparison"], differing)
    profile_header = ["assembly_accession","previous_evidence","batch","input_sha256","main_source_line",
                      "hamr_raw_rows","hamr_exact_unique_rows", *PROFILE]
    source_line = {r["strain"]:n for n,r in enumerate(mrows, 2)}
    emit(dest/"accession_profile.tsv", profile_header,
         ([a, "full_main" if a in old else "previously_unresolved", batch_by_id[a], hashes[a], source_line[a],
           ac[a], ac_unique[a], *[keyed[a][k] for k in PROFILE]] for a in sorted(keyed)))
    summary = {
        "label": "548", "pds": "PDS000041740.207", "source_archive": archive.name, "source_sha256": SRC_SHA,
        "reference_manifest_sha256":REF_SHA,"historical_main_sha256":OLD_MAIN_SHA,
        "source_crc_verified":True,"staged_unique_accessions":len(unique),"reference_inputs":len(hids),
        "source_archive_entries":len(archives),"genome_archive_entries":len(genome_folders),
        "archive_without_genome_basename":non_genome,"input_fasta_paths":len(raw_paths),
        "duplicate_input_accession": RESTORED,"reported_input_sha256_count":len(hashes),
        "raw_fasta_bytes_in_result_archive":False, "excluded_accessions":[],
        "final_members":{"main":"final/"+MAIN,"hamronization":"final/"+AMR},
        "main_rows":len(mrows),"main_source_columns":len(mh),"hamr_source_columns":len(ah),
        "hamr_rows":len(arows),"hamr_exact_unique_rows":len(distinct),"hamr_covered_accessions":len(ac),
        "raw_and_final_batch_data_rows_byte_identical":True,"batches":batch_registry,
        "batch_log_nonidentifier_values_verified":log_cell_count,
        "historical_overlap_accessions":len(old),"historical_main_nonidentifier_fields_compared":len(mh)-1,
        "historical_strain_label_note":"New strain values are versioned accessions; the historical strain labels include the assembly name. Comparisons use the versioned accession.",
        "historical_order_only_changed_fields":dict(field_changes),
        "historical_order_only_affected_accessions":len({x[0] for x in differing}),"other_historical_profile_differences":0,
        "restored_accession":RESTORED,"restored_main_profile":{k:keyed[RESTORED][k] for k in PROFILE},
        "restored_hamr_rows":ac[RESTORED],"restored_hamr_exact_unique_rows":ac_unique[RESTORED],
        "hAMRonization_software_database_fields":[dict(zip(["software","version","database","database_version"],r)) for r in software],
        "reported_ST_counts":dict(Counter(r["ST"] for r in mrows)),
        "QC_warnings":dict(Counter(r["QC_warnings"] for r in mrows)),
        "K_locus_confidence":dict(Counter(r["K_locus_confidence"] for r in mrows)),
        "O_locus_confidence":dict(Counter(r["O_locus_confidence"] for r in mrows)),
        "descriptive_nonempty_Bla_Carb_acquired":sum(r["Bla_Carb_acquired"] not in {"","-"} for r in mrows),
        "manifest_scope":"Within-archive/Baseline membership is validated. The independent NCBI metadata/PDT/tree linkage remains separate.",
    }
    (dest/"summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n")
    return summary

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ["archive","prior","dest"]:
        parser.add_argument(key, type=Path)
    args = parser.parse_args()
    main(args.archive, args.prior, args.dest)
