# Combined intake audit: 34 uploads, 28 distinct archive payloads

Audit date: 2 November 2026. **Development audit only; publication cohort NOT approved.**

## Scope and source preservation

The previous 19 uploads and the 15 current uploads were evaluated together. The six repeated M_K1–M_K6 files are byte-identical to P02–P07, including the damaged M_K5 archive. They are retained as upload events P24–P29 but are not parsed twice. Nine checksum-distinct packages are newly added. Original ZIP bytes remain unchanged. Package identifiers designate processing packages, not independent SNP clusters. No earlier result archives outside this explicit 34-upload manifest were appended.

## Reconciled file-level totals

| Measure | Count |
|---|---:|
| Upload events across the two tranches | 34 |
| New upload events | 15 |
| Byte-identical reuploads, counted once | 6 |
| Distinct archive payloads | 28 |
| Readable distinct archives passing CRC checks | 27 |
| Unreadable distinct archive | 1 |
| Packages with selected full main output | 26 |
| Packages with selected detailed hAMRonization output | 25 |
| Full main-table observations | 18,384 |
| Distinct leading GCA/GCF accession.version identifiers | 16,980 |
| Extra main observations due to repeated accessions | 1,404 |
| Separate abbreviated log-only records | 503 |
| Raw detailed hAMRonization observations | 302,695 |
| Exactly distinct hAMRonization rows | 275,207 |
| Distinct accession.version identifiers in detailed hAMR | 16,551 |
| Named input assemblies unresolved after technical errors | 57 |

**16,980 is not yet the final count of biological isolates.** GCA/GCF correspondence, source cohort membership, overlapping snapshots and downstream eligibility remain to be resolved. hAMR rows represent annotation observations, not independent isolates or inferred gene copies. The 57 technical unresolved inputs exclude the 503 log-only records, the three unidentified M_K1 omissions, the damaged M_K5 evidence, and the upstream M_K2 archive issue.

## Newly added checksum-distinct packages

| Package | Declared label | Unique listed inputs | Full main records | Inputs without full main |
|---|---|---:|---:|---:|
| P20 | A_K3 / PDS000269692.3 | 728 | 727 | 1 |
| P21 | D_496 | 301 | 301 | 0 |
| P22 | E_310 | 285 | 285 | 0 |
| P23 | G_267 | 222 | 222 | 0 |
| P30 | 1256 / PDS000267523.7 | 1228 | 1228 | 0 |
| P31 | 1239 / PDS000269670.2 | 1158 | 1158 | 0 |
| P32 | A_K2 / PDS000269692.3 | 970 | 970 | 0 |
| P33 | A_1716 | 1155 | 1152 | 3 |
| P34 | A_K1 / PDS000269692.3 | 929 | 877 | 52 |

New full main observations: 6,920. These are not all new unique assemblies: overlap is explicitly reconciled.

## Technical failures must not be recoded as biological exclusions

**A_K1 / P34:** 877 full results from 929 inputs. All 52 missing inputs have species-check failure messages and a corresponding file-open problem. In `remaining_logs/final_remaining.log`, `ERROR: could not open unzipped/GCF_... for reading` precedes the failed checks. Original FASTA paths contain a space immediately after the GCF directory name. This is an unresolved technical/path-handling problem, not evidence that 52 genomes are non-Klebsiella. Exact recovery paths are preserved in `recovery/P34_unresolved_fasta_paths.txt`.

**A_K3 / P20:** 727 full results from 728 inputs. `GCA_033193795.1` is missing. `batch_logs/batch_003.log` includes a shell syntax error involving `(` and an input directory named `GCA_033193575.1 (1)`. The failure remains technical/unresolved.

**A_1716 / P33:** 1,152 full results from 1,155 unique input stems (1,160 listed paths). The three missing accessions are `GCA_051112405.1`, `GCA_055007225.1`, and `GCA_055006825.1`. Shell syntax errors precede species-check failures. These must not be retained as confirmed taxonomic exclusions merely because earlier summaries called them excluded.

**548 / P14:** the earlier `GCA_054407865.1` technical failure and missing hAMRonization file remain unresolved.

## Evidence still missing

**M_K5 / P06, reuploaded as P28:** the new file has exactly the same SHA-256 and 196,536-byte length as the earlier damaged upload. A non-destructive local-header inspection found a truncated first hAMRonization member; no complete main output can be recovered from this payload. Recreate and test the ZIP on the original computer. The original Kleborate run may still be intact.

**610 / P17:** only 503 abbreviated log records are supplied. Recover the full main and detailed hAMR tables. Do not impute missing locus-level information from the logs.

**M_K1 / P02, reuploaded as P24:** the README still reports 846 inputs and 843 outputs, but the three omitted identifiers and their reasons are not supplied.

**M_K2 / P03, reuploaded as P25:** the QC list still flags `GCA_021968515.1.zip`. All 917 extracted-input names match main output, but this does not resolve the upstream download/integrity issue.

## Overlap and snapshot reconciliation

P03–P07 share 149 accessions; P04–P05 share nine. The new D_496 and G_267 packages share nine. P31 (1239) overlaps P02 by two, P04 by ten, and P05 by one. P11 (`PDS000267523.12`) and P30 (`PDS000267523.7`) share 1,224 accessions: four are present only in the supplied older .7 output and 27 only in the .12 output. These are different versioned collections, not two independent cohorts to sum, and the larger output does not automatically supersede every earlier record.

There are 458 accession profiles with raw text variation; all variation is confined to order of semicolon-delimited missing-locus-gene lists. Under the documented narrow list-order comparison, no substantive main-profile conflict was detected. Raw rows and duplicate tokens are preserved. Ten same-number GCA/GCF pairs are flagged as linkage candidates and are not automatically merged.

A_K1/A_K2/A_K3 jointly contain 2,574 distinct full-output accessions without mutual overlap. Their declared `PDS000269692.3` membership remains to be checked against frozen metadata. The O_K1/O_K2/O_K3 union remains 2,429 distinct accessions.

## Output selection and evidence-specific denominators

The unrelated 548 table inside P19 remains quarantined. G_267 pre-update backup outputs are not appended to its updated table. The explicit output-selection manifest records these choices. No biological values were corrected or filled from external information. All selected main records report Klebsiella pneumoniae and strong species match; all supplied detailed hAMR rows report Kleborate 3.2.4 and CARD 3.2.9. Those are exported labels, not a complete dependency or reference-data audit.

## Repository readiness

Code, synthetic tests, package/source checksums, output-selection rules, recovery manifests, a data dictionary, citation metadata and a submission-readiness checklist are prepared. The complete working data and original-source provenance are distributed in the audit bundle, not represented as an approved public data release. No license, DOI, ethics determination, or final scientific cohort is invented.

The next gate is recovery or explicitly justified handling of missing evidence, followed by the versioned collection–assembly–PDT crosswalk and verified metadata–Newick links for the expanded cohort. Previously supplied historical metadata must not be silently substituted for newer collection versions.

## Tests and reproducibility

Thirteen synthetic unit/integration tests passed on Python 3.13.5 in the audit container. They test file handling, duplicate folding, versioned identifiers, table schema checks, conflict withholding, missing-input guards and safe-path staging. They do not establish scientific validity. The audit is standard-library Python; Excel workbook generation is a separate presentation step. See `TEST_REPORT.txt`, `scripts/` and the exact input manifests.

## Interpretation references (not used to alter uploaded results)

NCBI identifier and clustering documentation: https://www.ncbi.nlm.nih.gov/pathogens/pathogens_help/
MDPI research-data guidance: https://www.mdpi.com/ethics
