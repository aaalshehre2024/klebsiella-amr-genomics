#!/usr/bin/env python3
"""Build browser-sized record tables and an assembly-aware gene/variation summary.

Usage: python3 scripts/browse_hamr.py 610
"""

import argparse
import csv
import re
from collections import Counter, defaultdict
from pathlib import Path


LIMIT = 390 * 1024
KEY = ("Gene_symbol", "Mutation", "Genetic_variation_type", "Drug_class")
ACCESSION = re.compile(r"^(GC[AF]_[0-9]+\.[0-9]+)(?:_|$)")


def build(folder):
    source = (folder / "hamronization.tsv").read_bytes()
    header, *lines = source.splitlines(keepends=True)
    columns = header.decode("utf-8-sig").rstrip("\r\n").split("\t")
    if len(columns) != 32 or columns[0] != "Input_file_name" or not lines:
        raise ValueError("Expected the 32-column hAMRonization table with at least one record")
    key_columns = [columns.index(field) for field in KEY]
    groups = {}
    rows_by_key = Counter()
    assemblies_by_key = defaultdict(set)
    previous = None
    for line in lines:
        fields = line.decode("utf-8").rstrip("\r\n").split("\t")
        if len(fields) != len(columns) or not (match := ACCESSION.match(fields[0])):
            raise ValueError(f"Malformed record with input name {fields[0]!r}")
        accession = match[1]
        if previous != accession:
            if accession in groups:
                raise ValueError(f"Nonconsecutive records for {accession}")
            groups[accession] = []
            previous = accession
        groups[accession].append(line)
        key = tuple(fields[i] for i in key_columns)
        rows_by_key[key] += 1
        assemblies_by_key[key].add(accession)

    parts = []
    size = len(header)
    for accession, records in groups.items():
        group_size = sum(map(len, records))
        if len(header) + group_size > LIMIT:
            raise ValueError(f"Single assembly exceeds the part size limit: {accession}")
        if not parts or size + group_size > LIMIT:
            parts.append([])
            size = len(header)
        parts[-1].append(accession)
        size += group_size

    out = folder / "browse_amr"
    out.mkdir(exist_ok=True)
    names = []
    first = 1
    index = []
    readme = [
        f"# Collection {folder.name} hAMRonization records", "",
        f"{len(lines):,} source records cover {len(groups):,} assemblies. Each part includes all 32 native columns, "
        "retains the source row order and includes exact duplicate rows. All records for an assembly are in one part.",
        "", "Look up an accession in the [assembly index](assembly_index.tsv), then open the linked part below. "
        "Source row numbers start at the first data row after the header.", "",
        "| Part | Source rows | First accession | Last accession | Assemblies | Records |",
        "| --- | --- | --- | --- | ---: | ---: |",
    ]
    reconstructed = bytearray(header)
    for number, accessions in enumerate(parts, 1):
        name = f"part_{number:03}.tsv"
        names.append(name)
        path = out / name
        data = b"".join(line for accession in accessions for line in groups[accession])
        path.write_bytes(header + data)
        with path.open("rb") as part:
            if part.readline() != header:
                raise ValueError(f"Header mismatch in {name}")
            reconstructed.extend(part.read())
        n = sum(len(groups[a]) for a in accessions)
        readme.append(f"| [{number}]({name}) | {first:,}–{first+n-1:,} | {accessions[0]} | {accessions[-1]} | {len(accessions)} | {n:,} |")
        for accession in accessions:
            count = len(groups[accession])
            index.append((accession, name, first, first+count-1, count))
            first += count
    if reconstructed != source:
        raise ValueError("Concatenating part data did not reproduce hamronization.tsv")
    for old in out.glob("part_[0-9][0-9][0-9].tsv"):
        if old.name not in names:
            old.unlink()

    with (out / "assembly_index.tsv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter="\t", lineterminator="\n")
        writer.writerow(("accession", "part", "first_source_row", "last_source_row", "raw_records"))
        writer.writerows(sorted(index))
    with (folder / "gene_variation_counts.tsv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter="\t", lineterminator="\n")
        writer.writerow((*KEY, "raw_records", "unique_assemblies"))
        for key in sorted(rows_by_key, key=lambda k: (-len(assemblies_by_key[k]), -rows_by_key[k], k)):
            writer.writerow((*key, rows_by_key[key], len(assemblies_by_key[key])))
    readme.extend(["", "The gene and variation summary groups the exact reported gene symbol, mutation, variation type "
                   "and drug class, preserving case, qualifiers and source values. Raw record counts retain duplicates. "
                   "Each distinct assembly counts once per combination and can contribute to multiple combinations. "
                   "[Gene and variation summary](../gene_variation_counts.tsv)", "",
                   "To download the complete original table, open the file and select **Download raw file**. "
                   "[Full hAMRonization table](../hamronization.tsv)", ""])
    (out / "README.md").write_text("\n".join(readme), encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("collection_folder", type=Path)
    build(parser.parse_args().collection_folder)
