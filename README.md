# Klebsiella AMR genomics

Research workspace for a database-derived analysis of selected *Klebsiella pneumoniae* genomic collections, intended for submission to *Antibiotics*.

## Current status: first 19-package audit

The first-tranche audit dated 2 November 2026 covers exactly 19 uploaded result packages. Eighteen archives are readable; 17 contain selected full main outputs and 16 contain selected hAMRonization outputs. The selected main tables contain 11,464 package-level observations and 11,306 distinct leading GCA/GCF accession.version identifiers after accounting for 158 repeated-accession observations. A further 503 records are available only as abbreviated logs and are kept separate.

**These are provisional file-audit counts, not a final biological-isolate denominator or a publication-ready dataset.** One M_K5 archive is unreadable. The 610 package lacks full outputs, and the 548 package lacks detailed output and has a technical failure requiring review.

## Start here

- [Audit findings and package inventory](audits/2026-11-02_batch01/AUDIT_REPORT.md)
- [Machine-readable audit summary](audits/2026-11-02_batch01/audit_summary.json)
- [Uploaded archive SHA-256 provenance](audits/2026-11-02_batch01/input_archives_sha256.csv)
- [Recovery priorities](audits/2026-11-02_batch01/RECOVERY_ACTIONS.md)
- [Post-audit analysis and manuscript plan](manuscript/ANALYSIS_PLAN.md)

The current public repository contains audit/provenance documentation and the manuscript plan. Original result ZIPs and unrestricted logs have not been uploaded here. The accompanying downloadable audit bundle contains the detailed working tables, explicit package-selection manifest, reproducible audit script and six synthetic tests. A reviewed code/data release remains pending.

## Analytical boundaries

A result ZIP is a processing package, not necessarily a distinct SNP-cluster collection. Establish biological cohorts from frozen metadata, versioned PDS/PDT/assembly identifiers and verified tree linkage. PDG labels and local batch names do not establish PDS membership.

Missing output is not a negative biological finding. A failed command is not a confirmed taxonomic exclusion. Genomic annotation alone does not establish clinical resistance, hypervirulence, plasmid co-location, transmission or population prevalence. All marker flags and source provenance must remain traceable.

## Workflow

Preserve input hashes; resolve output availability and collection membership; reconcile overlapping accessions and paired assemblies; freeze feature-interpretation rules; generate analysis tables and figures from reviewed records; then archive the version supporting the manuscript.

## Licensing and citation

Licensing, contributor metadata and the eventual archival release remain to be finalized by the authors. No publication DOI or acceptance status is asserted.
