# Klebsiella AMR genomics

Audit-first research workspace for a database-derived *Klebsiella pneumoniae* study intended for **Antibiotics** (MDPI).

**Status: development / cohort reconciliation. Not a publication-ready dataset or accepted paper.**

## Selected sources for 610 and 548

On 3 November 2026 the study author selected one result ZIP for each of these two collections. Use each independently for research. The counts refer to versioned assembly accessions in that ZIP's own FASTA list.

| Package label | Listed assemblies | Records available for analysis | Detailed hAMRonization table |
|---|---:|---|---|
| 610 (PDS000052355.137) | 503 | 503 eight-field batch-log records. Use the reported species, N50, ST, scores and counts. The selected ZIP lacks a full main table. | Unavailable |
| 548 (PDS000041740.207) | 430 | 429 full main-table records. The five logs corroborate the same records. One input, GCA_054407865.1, has an unresolved technical failure. | Unavailable |

Use the selected 610 logs for analyses of the fields they contain. Restrict named AMR determinants and K/O and virulence locus analyses to sources that actually report those fields. For 548, apply the relevant typing-confidence and QC rules to its full table.

The [source register](audits/2026-11-03_selected_610_548/source_register.tsv) identifies the selected files by SHA-256. The [research-use notes](audits/2026-11-03_selected_610_548/README.md) give the evidence available for each analysis. The [2 November recovery audit](audits/2026-11-02_recovery_610_548/RECOVERY_REPORT.md) and [combined intake audit](audits/2026-11-02_combined/AUDIT_REPORT.md) describe earlier source selections. Their pooled totals do not carry forward to this selection. Study-wide denominators require separate reconciliation. See [submission readiness](docs/SUBMISSION_READINESS.md).

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

The complete provisional working tables are supplied in the companion audit/recovery bundles. Original archives, local filesystem logs and unreviewed large tables are not automatically published here. No final numerical Results should be drafted until the eligibility and denominator gates are resolved.

## Citation and permissions

CITATION.cff describes this development repository, not a published article. Licensing, contributor approval and a version-specific repository DOI remain author decisions. Public visibility is not a declaration that third-party data can be relicensed. See docs/LICENSING_STATUS.md.
