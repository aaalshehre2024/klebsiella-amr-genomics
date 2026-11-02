# First-tranche audit: 19 Kleborate result packages

Audit date: 2 November 2026. **Provisional working audit, not a publication-ready cohort.**

## Scope and provenance

This audit covers only the 19 newly uploaded ZIPs. Earlier packages and master totals were not silently appended. Package IDs P01–P19 denote processing packages, not independent biological collections. Original archives were not edited. The downloadable audit bundle retains member hashes, explicit output selections, input reconciliation, full source-provenance tables, deduplicated derivatives, code and tests.

## File-level findings

| Measure | Count |
|---|---:|
| Uploaded packages | 19 |
| Readable archives passing member CRC checks | 18 |
| Unreadable archive | 1 |
| Packages with selected full main output | 17 |
| Packages with selected hAMRonization output | 16 |
| Selected main-table observations | 11,464 |
| Distinct leading GCA/GCF accession.version identifiers | 11,306 |
| Extra observations from repeated accessions | 158 |
| Separate log-only observations | 503 |
| hAMRonization rows before exact-row deduplication | 188,811 |
| Exact distinct hAMRonization rows | 184,366 |
| Distinct accessions represented in detailed hAMRonization | 10,877 |

**11,306 is not yet a count of unique biological isolates.** GCA/GCF correspondence and source collection membership require further verification. Detailed rows are annotation hits/variants, not independent isolates or gene-copy counts.

## Package inventory

| ID | Declared package label | Main rows | hAMR rows | Qualification |
|---|---|---:|---:|---|
| P01 | 815 / PDS000235927.11 | 612 | 10,132 | 612 listed inputs matched |
| P02 | M_K1 / PDS000270847.3 | 843 | 15,802 | README claims 846 inputs and 3 omissions; omitted IDs absent |
| P03 | M_K2 / PDS000270847.3 | 917 | 15,446 | 917 listed inputs matched; upstream ZIP issue |
| P04 | M_K3 / PDG000000012.2539 | 993 | 16,551 | PDS membership unverified |
| P05 | M_K4 / PDG000000012.2539 | 994 | 16,579 | PDS membership unverified |
| P06 | M_K5 / PDG000000012.2539 | Unavailable | Unavailable | Uploaded ZIP unreadable |
| P07 | M_K6 / PDG000000012.2539 | 418 | 7,695 | Overlaps M_K2; PDS membership unverified |
| P08 | O_K1 / PDS000015678.325 | 933 | 14,260 | 933 listed inputs matched |
| P09 | O_K2 / PDS000015678.325 | 916 | 14,718 | 916 listed inputs matched |
| P10 | O_K3 / PDS000015678.325 | 580 | 9,184 | 580 listed inputs matched |
| P11 | 1261 / PDS000267523.12 | 1,251 | 23,098 | Keep version .12 distinct from earlier .7 |
| P12 | 500 / PDS000012112.257 | 398 | 5,699 | 398 listed inputs matched |
| P13 | 489 / PDS000040355.81 | 215 | 3,583 | 215 listed inputs matched |
| P14 | 548 / PDS000041740.207 | 429 | Unavailable | 430 inputs; one technical failure; detailed output absent |
| P15 | 481 / PDS000045379.67 | 235 | 3,377 | 235 listed inputs matched |
| P16 | 805 / PDS000052089.288 | 770 | 16,826 | 770 listed inputs matched |
| P17 | 610 / PDS000052355.137 | Unavailable | Unavailable | 503 abbreviated log records only |
| P18 | 404 / PDS000060581.86 | 257 | 5,036 | 257 listed inputs matched |
| P19 | 709 / PDS000123673.216 | 703 | 10,825 | Foreign 548 table quarantined |

## Required recovery and integrity decisions

### P06: M_K5

The 196,536-byte upload begins with ZIP local headers but has no readable end-of-central-directory record. Recreate and test the result archive from the original Ubuntu run, then upload it again. This does not establish that the underlying Kleborate run failed, and it must not be recorded as zero analyzed genomes.

### P17: 610

The archive contains 503 input names and 503 abbreviated log records, but neither full main nor hAMRonization output. Log-only evidence is preserved separately; missing locus-level fields are not imputed. Recover the original full output tables.

### P14: 548

The missing main-output accession is GCA_054407865.1. In batch_logs/batch_002.log, a shell syntax error involving '(' precedes the species-check failure. This is an unresolved technical failure, NOT a confirmed non-Klebsiella exclusion. Repair the input path and rerun this assembly before a biological decision. Recover the missing detailed hAMRonization output as well.

### P03: M_K2

The upstream QC list names GCA_021968515.1.zip as failing archive checking. All 917 listed extracted FASTAs match main output, but that does not resolve a download failure outside the extracted-input denominator. Recover or document the unavailable source archive.

### P02: M_K1

README_QC reports 846 input files, 843 analyzed records and three not included. The full input manifest, omitted identifiers and reasons are missing. The hAMRonization file also contains 1,813 exact repeated rows beyond first occurrences. Original rows remain retained; the exact-row-deduplicated derivative does not interpret these repeats as copy-number evidence.

### P19: mixed package

An extra 429-row PDS000041740_207_548 main table is byte-identical to P14. It is explicitly excluded from P19's selected data. Its member hash remains in the audit. Only the correctly named 703-row PDS000123673_216_709 main table is counted for P19.

## Overlap and profile reconciliation

M_K2 (P03) and M_K6 (P07) share 149 accession.version identifiers. M_K3 (P04) and M_K4 (P05) share nine. Two repeated profiles differ only in the order of semicolon-separated K_Missing_expected_genes tokens. Their token multisets agree; raw copies are retained. No substantive main-profile differences remain under that narrowly defined comparison rule.

Four same-number GCA/GCF accession-version pairs and three strain names containing an embedded alternative accession are flagged for source-level review. The leading accession is used provisionally. Neither embedded alternatives nor GCA/GCF pairs are automatically merged.

The O_K1/O_K2/O_K3 package union contains 2,429 distinct full-output accessions, with no overlap among those three packages. Their common PDS label remains filename-derived until the frozen metadata confirms membership.

## Boundaries on interpretation

All selected main-table observations report Klebsiella pneumoniae with strong species match. All supplied hAMRonization rows label Kleborate 3.2.4 and CARD 3.2.9. These are exported software labels, not independent biological validation or a complete environment/database audit.

No frozen NCBI metadata exports or Newick trees are present in the current 19 ZIPs. NCBI uses PDG for organism groups and PDS for SNP clusters; do not interpret 19 processing packages as 19 SNP clusters. Original snapshot and later assembly-download dates must be recorded separately. ZIP timestamps are not biological sampling dates.

## Reproducible processing

The companion standard-library script validates archives and TSV widths, records SHA-256 checksums, applies an explicit output-selection manifest, checks input-output identities, preserves missing-evidence tiers, and reports overlap. Only list ordering in K_Missing_expected_genes and O_Missing_expected_genes is normalized for comparison; duplicated tokens and other calls are retained. A derivative collapses only exactly identical 32-column hAMRonization rows. Six synthetic unit/integration tests passed. These tests do not establish scientific validity or cohort eligibility.

## Documentation

NCBI identifier definitions: https://www.ncbi.nlm.nih.gov/pathogens/pathogens_help/

Kleborate output documentation: https://kleborate.readthedocs.io/en/latest/Usage.html

See manuscript/ANALYSIS_PLAN.md for the planned post-audit analyses. No final manuscript findings or release DOI are asserted.
