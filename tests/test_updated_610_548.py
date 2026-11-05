"""Regression checks for the versioned 5 November 2026 public data."""
import csv
import hashlib
import re
import unittest
from collections import Counter
from pathlib import Path


AUDIT = Path(__file__).resolve().parents[1] / "audits" / "2026-11-05_updated_610_548"
PRIOR = AUDIT.parent / "2026-11-03_selected_610_548"
ACCESSION = re.compile(r"^(GC[AF]_\d+\.\d+)(?:_|$)")


def records(path):
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


class UpdatedProfiles(unittest.TestCase):
    def test_native_and_derived_coverage(self):
        for row in records(AUDIT / "source_register.tsv"):
            label = row["collection"]
            with self.subTest(collection=label):
                folder = AUDIT / label
                prior = records(PRIOR / label / "input_manifest.tsv")
                ids = {r["assembly_accession"] for r in prior}
                main = folder / "main_results.tsv"
                hamr = folder / "hamronization.tsv"
                self.assertEqual(hashlib.sha256(main.read_bytes()).hexdigest(), row["main_sha256"])
                self.assertEqual(hashlib.sha256(hamr.read_bytes()).hexdigest(), row["hamr_sha256"])
                main_rows = records(main)
                hamr_rows = records(hamr)
                self.assertEqual(len(main_rows[0]), 117)
                self.assertEqual(len(hamr_rows[0]), 32)
                self.assertEqual(Counter(ACCESSION.match(r["strain"])[1] for r in main_rows), Counter(ids))
                counts = Counter(ACCESSION.match(r["Input_file_name"])[1] for r in hamr_rows)
                self.assertEqual(set(counts), ids)
                profiles = records(folder / "accession_profile.tsv")
                self.assertEqual({r["assembly_accession"]: int(r["hamr_raw_rows"]) for r in profiles},
                                 dict(counts))
                self.assertEqual(sum(counts.values()), int(row["supplied_hamr_rows"]))
                unique = records(folder / "hamronization_exact_unique.tsv")
                self.assertEqual([tuple(r.values()) for r in unique],
                                 list(dict.fromkeys(tuple(r.values()) for r in hamr_rows)))
                self.assertEqual(len(unique), int(row["exact_distinct_hamr_rows"]))
                self.assertEqual(sum(int(r["assemblies"]) for r in records(folder / "observed_joint_profiles.tsv")),
                                 len(ids))

    def test_browser_parts_preserve_all_native_bytes(self):
        for label in ("610", "548"):
            folder = AUDIT / label
            with self.subTest(collection=label):
                original = (folder / "hamronization.tsv").read_bytes()
                header = original.split(b"\n", 1)[0] + b"\n"
                combined = bytearray(header)
                for part in sorted((folder / "browse_amr").glob("part_*.tsv")):
                    content = part.read_bytes()
                    self.assertTrue(content.startswith(header))
                    combined.extend(content[len(header):])
                self.assertEqual(bytes(combined), original)

    def test_recovery_ledger_and_restored_assembly(self):
        ledger = records(AUDIT / "technical_input_status.tsv")
        self.assertEqual(len({r["assembly_accession"] for r in ledger}), 57)
        pending = [r for r in ledger if r["disposition"] == "awaiting_verified_outcome"]
        self.assertEqual(Counter(r["package_id"] for r in pending), {"P34": 52, "P20": 1, "P33": 3})
        restored = [r for r in ledger if r["disposition"] == "resolved_by_548_rerun"]
        self.assertEqual([r["assembly_accession"] for r in restored], ["GCA_054407865.1"])
        row, = (r for r in records(AUDIT / "548" / "accession_profile.tsv")
                if r["assembly_accession"] == "GCA_054407865.1")
        self.assertEqual((row["ST"], row["hamr_raw_rows"], row["hamr_exact_unique_rows"]),
                         ("ST307", "24", "13"))


if __name__ == "__main__":
    unittest.main()
