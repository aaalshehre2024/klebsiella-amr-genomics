#!/usr/bin/env python3
"""Summarize one collection's main_results.tsv, counting each assembly once.

Usage: python3 scripts/summarize_profiles.py 610

Locus calls and confidence are separate Kleborate fields. Keep exact ST labels
(including -1LV), both typeability categories, and all QC categories. For the
family profile, use only plain allele names from Bla_Carb_acquired. Count the
same family once per assembly. Keep tokens with terminal *, ^ or ? outside
that profile and tabulate them separately. A dash denotes no reported call
and [blank] denotes a missing field. These summaries describe genomic calls.
"""

import argparse
import csv
import re
from collections import Counter
from pathlib import Path


LOCUS_FIELDS = ("ST", "K_locus", "K_locus_confidence", "O_locus", "O_locus_confidence")
SOURCE_FIELDS = LOCUS_FIELDS + ("resistance_score", "virulence_score", "QC_warnings", "Bla_Carb_acquired")
FAMILY = "unflagged_Bla_Carb_acquired_families"
FLAGGED = "flagged_Bla_Carb_acquired_tokens"
ASSEMBLY = re.compile(r"^(GC[AF]_[0-9]+\.[0-9]+)(?:_|$)")
ALLELE = re.compile(r"([A-Za-z][A-Za-z0-9]*)-[0-9]+([*?^]*)")


def family_profile(raw):
    if raw in ("-", "[blank]"):
        return raw, raw
    families = set()
    flagged = set()
    for token in raw.split(";"):
        match = ALLELE.fullmatch(token)
        if match is None:
            raise ValueError(f"Unrecognized Bla_Carb_acquired token {token!r}")
        if match[2]:
            flagged.add(token)
        else:
            families.add(match[1])
    return ("+".join(sorted(families)) or "[flagged only]",
            ";".join(sorted(flagged)) or "-")


def ordered(counter):
    return sorted(counter.items(), key=lambda item: (-item[1], item[0]))


def summarize(folder):
    fields = SOURCE_FIELDS + (FAMILY, FLAGGED)
    counts = {field: Counter() for field in fields}
    joint = Counter()
    seen = set()
    with (folder / "main_results.tsv").open(encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source, delimiter="\t")
        missing = set(("strain",) + SOURCE_FIELDS) - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Missing required columns: {sorted(missing)}")
        for row in reader:
            if None in row or None in row.values():
                raise ValueError(f"Malformed TSV row at line {reader.line_num}")
            match = ASSEMBLY.match(row["strain"])
            if not match or match[1] in seen:
                raise ValueError(f"Missing or duplicate assembly accession: {row['strain']!r}")
            seen.add(match[1])
            values = {field: row[field] or "[blank]" for field in SOURCE_FIELDS}
            values[FAMILY], values[FLAGGED] = family_profile(values["Bla_Carb_acquired"])
            for field in fields:
                counts[field][values[field]] += 1
            joint[tuple(values[field] for field in LOCUS_FIELDS + (FAMILY,))] += 1

    n = len(seen)
    if n == 0:
        raise ValueError("main_results.tsv contains no assemblies")
    with (folder / "observed_joint_profiles.tsv").open("w", encoding="utf-8", newline="") as output:
        writer = csv.writer(output, delimiter="\t", lineterminator="\n")
        writer.writerow((*LOCUS_FIELDS, FAMILY, "assemblies", "main_table_assemblies"))
        for key, count in ordered(joint):
            writer.writerow((*key, count, n))
    with (folder / "profile_counts.tsv").open("w", encoding="utf-8", newline="") as output:
        writer = csv.writer(output, delimiter="\t", lineterminator="\n")
        writer.writerow(("field", "value", "assemblies", "main_table_assemblies"))
        for field in fields:
            for value, count in ordered(counts[field]):
                writer.writerow((field, value, count, n))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("collection_folder", type=Path, help="folder containing main_results.tsv")
    summarize(parser.parse_args().collection_folder)
