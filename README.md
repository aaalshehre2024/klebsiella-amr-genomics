# Klebsiella AMR genomics

Audit-first research workspace for a database-derived *Klebsiella pneumoniae* study intended for **Antibiotics** (MDPI).

**Status: development / cohort reconciliation. Not a publication-ready dataset or accepted paper.**

## Current intake and recovery status

The original combined 2 November 2026 audit covers 34 uploads: 28 distinct archive payloads after folding six byte-identical reuploads. That historical audit remains unchanged.

**Latest amendment:** the complete 610 recovery archive supplies full main and detailed hAMRonization tables for all 503 original listed inputs. These replace P17's log-only evidence rather than creating another biological collection. The updated working data contain 18,887 package-level main observations and 17,483 distinct leading assembly accession.version identifiers. These are not yet verified unique biological isolates. No records in this intake remain supported only by abbreviated logs.

**548 remains unresolved:** its existing main table contains 429 of 430 original inputs, and its detailed hAMRonization output is still missing. All recovered candidate batch tables under the current 548 directory match 709 results, not the original 548 accession list. The original 430-input 548 manifest is preserved separately in the companion recovery bundle. Do not use the current 703-input list to rerun 548.

Read [the recovery amendment](audits/2026-11-02_recovery_610_548/RECOVERY_REPORT.md), [its machine-readable summary](audits/2026-11-02_recovery_610_548/recovery_summary.json), [the historical combined audit](audits/2026-11-02_combined/AUDIT_REPORT.md), and [submission readiness](docs/SUBMISSION_READINESS.md). Historical audit counts are not additive to the latest counts. The 57 named technical unresolved inputs and other documented recovery/provenance issues remain open.

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
