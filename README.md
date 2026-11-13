# Klebsiella AMR genomics

Audit-first research workspace for a database-derived *Klebsiella pneumoniae* study intended for **Antibiotics** (MDPI).

**Status: development / cohort reconciliation. Not a publication-ready dataset or accepted paper.**

## Current research profiles for 610 and 548

The 5 November 2026 source update supplies a full 117-field Kleborate profile and detailed 32-field hAMRonization annotations for every listed assembly in both collections.

| Collection | Main coverage | Assemblies with detailed AMR | Raw / exact-distinct AMR rows | Browse |
|---|---:|---:|---:|---|
| 610 · PDS000052355.137 | 503/503 | 503/503 | 13,826 / 8,939 | [Assembly profiles](audits/2026-11-05_updated_610_548/610/) · [AMR records](audits/2026-11-05_updated_610_548/610/browse_amr/) |
| 548 · PDS000041740.207 | 430/430 | 430/430 | 9,652 / 6,430 | [Assembly profiles](audits/2026-11-05_updated_610_548/548/) · [AMR records](audits/2026-11-05_updated_610_548/548/browse_amr/) |

The 548 rerun resolves `GCA_054407865.1` (ST307, 24 raw AMR records). The [updated audit](audits/2026-11-05_updated_610_548/), [source checksums](audits/2026-11-05_updated_610_548/source_register.tsv), and [remaining manuscript decisions](audits/2026-11-05_updated_610_548/PAPER_READINESS.md) document the current selection. Both output tables in each collection report genomic annotations. Exact assembly accessions, quality flags and repeat records are retained.

The [3 November audit](audits/2026-11-03_selected_610_548/), the [2 November recovery amendment](audits/2026-11-02_recovery_610_548/RECOVERY_REPORT.md) and the [combined intake audit](audits/2026-11-02_combined/AUDIT_REPORT.md) remain available for historical comparisons. Their study-wide counts refer to their respective source selections.

## Reproduce the original intake audit locally

Use Python 3.10 or later. The audit uses only the standard library and does not rerun Kleborate.

```bash
python3 scripts/test_project.py
python3 scripts/reconcile_uploads.py --input-dir /path/to/selected_result_zips --manifest metadata/uploads_34.json --output-dir local_outputs/combined_audit_001
```

This command reproduces the original 34-upload intake, not the later recovery amendment. The recovery-verification script, its tests and updated working tables are supplied in the companion recovery bundle documented in the amendment summary.

The manifest refers to the exact 34 supplied result ZIP filenames and SHA-256 hashes. Byte-identical reuploads are logged but parsed once. A changed ZIP is a new audit input and requires a new versioned manifest; do not edit a checksum to suppress a mismatch. Existing output directories are never overwritten. Results archives are not genome-download archives.

## Evidence rules

A ZIP or local batch is not an independent biological collection. PDG and PDS labels are not interchangeable. Preserve accession versions and verify metadata–assembly–PDT–tree linkage. Keep newer and older collection snapshots separate until a documented analysis decision is made. Do not interpret missing files, technical failures, or absent log fields as biological negatives. Do not make population-prevalence, transmission, plasmid co-location, or clinical validation claims from annotation tables alone.

## Files and release status

`metadata/` contains frozen upload selections and a collection-manifest template. `scripts/` and `tests/` contain the original intake audit/recovery code and tests. `audits/` contains versioned compact provenance and findings. `docs/` contains the dictionary, recovery guide and release requirements. `release_data/` is reserved for approved manuscript evidence.

The checked tables for the selected 610 and 548 sources are available in the audit folders above. Earlier provisional working tables are supplied in the companion audit/recovery bundles. Original archives, local filesystem logs and unreviewed large tables are not automatically published here. No final numerical Results should be drafted until the eligibility and denominator gates are resolved.

## Citation and permissions

CITATION.cff describes this development repository, not a published article. Licensing, contributor approval and a version-specific repository DOI remain author decisions. Public visibility is not a declaration that third-party data can be relicensed. See docs/LICENSING_STATUS.md.

## Existing source data: 13 November 2026 inventory

The [inventoried source snapshot](source_data/2026-11-13_existing_analysis/README.md)
preserves 77 source files, including 17 candidate current TSV exports,
saved result archives, and candidate tree files. Original relative paths,
SHA-256 hashes, file sizes, and archive-integrity findings are recorded.

This source import supports inspection and subsequent analysis. Scientific
reproduction and current manuscript quantities remain unverified. See the
snapshot's SOURCE_STATUS.json and ZIP_INTEGRITY.csv for the validation scope.
