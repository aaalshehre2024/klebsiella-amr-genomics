# Audit data dictionary

All tables are UTF-8; raw values retain Kleborate flags and spelling. Counts are file-level unless stated otherwise.

| Table/field | Meaning |
|---|---|
| upload_registry.upload_id | One supplied archive event P01–P34, not a biological cohort |
| canonical_package_id | First byte-identical payload retained for parsing |
| sha256 | Hash of original uploaded archive bytes |
| declared_identifier | Filename/project label, not independently verified PDS membership |
| main_records | Rows in the explicitly selected full main table |
| archive_status | Whether ZIP central directory/member CRC checks succeeded |
| input_unique_strains | Distinct full filename stems in the selected input manifest |
| input_without_main | Input stems missing a full main row; not automatic biological exclusion |
| log_only_records | Abbreviated stdout rows, stored separately from full main evidence |
| hamr_records | Detailed annotation observations, not isolates or inferred gene copy numbers |
| assembly_accession | Leading versioned GCA/GCF identifier; prefixes and versions preserved |
| source_member/source_record | ZIP member and parsed data-record provenance |
| unique_assembly_profiles | Provisional accession-level nonconflicting profiles, not final unique isolates |
| source_packages | All canonical packages supporting a repeated record |
| main_profile_variations.order_only | Difference confined to missing-locus-gene token ordering |
| gca_gcf_pairing_candidates | Same numeric accession/version candidates; must be verified, not auto-merged |
| exact distinct hAMR row | Equality of all original 32 fields; deduplicated derivative only |

Unavailable full or detailed output is missing evidence. A stored row-count zero is not a statement of zero organisms, genes or resistance. The original input/output fields and all quality flags are retained; no clinical phenotype is inferred. No data dictionary entry converts a PDG group into a PDS cluster.
