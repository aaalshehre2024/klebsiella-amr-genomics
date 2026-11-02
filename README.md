# Klebsiella AMR genomics

Audit-first research workspace for a database-derived *Klebsiella pneumoniae* study intended for **Antibiotics** (MDPI).

**Status: development / cohort reconciliation. Not a publication-ready dataset or accepted paper.**

## Current intake

The combined 2 November 2026 audit covers 34 uploads: 28 distinct archive payloads after folding six byte-identical reuploads. Twenty-seven distinct archives are readable; 26 provide full main tables and 25 detailed hAMRonization files. There are 18,384 package-level main observations and 16,980 distinct leading assembly accession.version identifiers. These are not yet verified unique biological isolates. The 503 log-only records remain separate.

Read [the combined audit](audits/2026-11-02_combined/AUDIT_REPORT.md) and [submission readiness](docs/SUBMISSION_READINESS.md). The first-tranche audit remains archived; its counts are not additive to the combined audit.

## Start locally

Use Python 3.10 or later. The audit uses only the standard library and does not rerun Kleborate.

```bash
python3 scripts/test_project.py
python3 scripts/reconcile_uploads.py --input-dir /path/to/selected_result_zips --manifest metadata/uploads_34.json --output-dir local_outputs/combined_audit_001
```

The manifest refers to the exact 34 supplied result ZIP filenames and SHA-256 hashes. Byte-identical reuploads are logged but parsed once. A changed ZIP is a new audit input and requires a new versioned manifest; do not edit a checksum to suppress a mismatch. Existing output directories are never overwritten. Results archives are not genome-download archives.

## Evidence rules

A ZIP or local batch is not an independent biological collection. PDG and PDS labels are not interchangeable. Preserve accession versions and verify metadata–assembly–PDT–tree linkage. Keep newer and older collection snapshots separate until a documented analysis decision is made. Do not interpret missing files, technical failures, or absent log fields as biological negatives. Do not make population-prevalence, transmission, plasmid co-location, or clinical validation claims from annotation tables alone.

## Files and release status

`metadata/` contains frozen upload selections and a collection-manifest template. `scripts/` and `tests/` contain the audit/recovery code and tests. `audits/2026-11-02_combined/` contains compact provenance and findings. `docs/` contains the dictionary, recovery guide and release requirements. `release_data/` is reserved for approved manuscript evidence.

The complete provisional working tables are supplied in the companion audit bundle. Original archives, local filesystem logs and unreviewed large tables are not automatically published here. No final numerical Results should be drafted until the eligibility and denominator gates are resolved.

## Citation and permissions

CITATION.cff describes this development repository, not a published article. Licensing, contributor approval and a version-specific repository DOI remain author decisions. Public visibility is not a declaration that third-party data can be relicensed. See docs/LICENSING_STATUS.md.
