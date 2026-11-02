# Verified recovery of 610; 548 detailed output remains missing

Audit amendment: 2 November 2026. **Output-level recovery audit, not a finalized biological cohort.**

## Source and integrity

Recovery source: `RECOVERED_610_548_20261102_231741_SJEjh7.zip`.

SHA-256: `f160245940d5cfa953741751ebe10d7d49f6bfd3e109a6c97d3dd9d65516dbfb`.

The ZIP passes member CRC testing. All 59 entries in the supplied SHA256SUMS.txt match the archived files. Every file listed in the recovery source manifest is present. Integrity checks establish that these copies match the supplied checksums; they do not independently validate the biology.

Comparison sources are the original P14 (548), P17 (610), and P19 (709) result archives and the previously supplied combined 34-upload audit bundle. Exact source filenames and checksums are in the companion bundle's `audit/source_archives.csv`. Directory labels are not used as proof of collection identity.

## 610 / PDS000052355.137: full output recovered

| Measure | Verified value |
|---|---:|
| Main batch tables recovered | 6 |
| Detailed hAMRonization batch tables recovered | 6 |
| Original unique listed inputs | 503 |
| Full main records / distinct versioned accessions | 503 / 503 |
| Main-table columns | 117 |
| hAMRonization columns | 32 |
| Original inputs missing a main record | 0 |
| Accessions represented in detailed hAMRonization | 503 |
| Raw hAMRonization observations | 13,826 |
| Exactly distinct 32-column hAMRonization rows | 8,939 |
| Exact repeated hAMRonization rows beyond first occurrences | 4,887 |

The recovered 610 input list is byte-identical to the original P17 input list. Every input accession is represented exactly once in the full main tables, with no extra main-output accession. All seven comparable summary fields agree with the earlier log-only evidence for every record (3,521 comparisons; zero disagreements). All recovered main rows report K. pneumoniae with strong species match; the detailed rows label Kleborate 3.2.4 and CARD 3.2.9. These remain software-reported annotations.

The six main tables are concatenated without altering any biological calls. Raw detailed rows are retained, and a separately named derivative removes only exactly identical 32-column rows. Neither the raw nor deduplicated row count is a count of unique resistance genes, genomic copies, or biological isolates. This recovery requires no new Kleborate run for these 503 listed inputs. It does not establish coverage of all 610 records implied by the collection label.

## 548 / PDS000041740.207: candidate batches are 709 evidence

The existing 429-row 548 main table is byte-identical to the previously supplied P14 table. The original P14 input manifest contains 430 versioned accessions. The unresolved accession remains `GCA_054407865.1`; no repaired output for it is supplied.

The five original batch directories and four remaining-batch directories under the recovery ZIP's `548/` directory contain 703 main records in total. Their exact main-row set matches the existing 709 table. All nine candidate detailed batch files match those same 703 709 accessions and contain **zero** accessions from the existing 429-row 548 main table. Their 21,333 raw detailed rows reduce to the same 10,825 exact rows already present in the 709 final detailed table. They are not new 548 evidence and are not added again to the combined dataset.

The current `548/all_available_fasta_paths_unique.txt` is also byte-identical to the original 709 703-input manifest, not the original 548 430-input manifest. Thus both current batch contents and input-list membership are mixed with 709 evidence. Overwriting/reuse is a possible explanation, but the precise history is not established by the files.

**548 detailed-output recovery remains unresolved.** The number of recovered 548 hAMRonization rows is zero, meaning missing evidence, not absence of resistance determinants. Candidate files are quarantined from 548 analytical use; the uploaded ZIP is retained unchanged. The original 548 input manifest is restored from P14 into a separate reference file; no file in the user's Ubuntu directory was changed.

## Updated working-data counts

The 503 full 610 records upgrade the earlier P17 log-only evidence; they are not a new biological collection. None of their versioned accessions overlap the prior 16,980 full-output accessions.

| Measure | Before recovery | After recovery |
|---|---:|---:|
| Main package-level observations | 18,384 | 18,887 |
| Distinct versioned full-output assembly accessions | 16,980 | 17,483 |
| Detailed raw hAMRonization observations | 302,695 | 316,521 |
| Exactly distinct hAMRonization rows | 275,207 | 284,146 |
| Accessions represented in detailed hAMRonization | 16,551 | 17,054 |
| Remaining records supported only by abbreviated logs | 503 | 0 |

The previously documented 57 named technical unresolved inputs are unchanged. M_K5, the 548 detailed-output gap, M_K1 omitted identifiers, M_K2 upstream archive issue, cohort snapshot decisions, GCA/GCF correspondence and metadata/tree linkage still require resolution. No final isolate denominator, prevalence estimate, or manuscript result is approved by this amendment.

## Reproducible derivatives

The companion `Klebsiella_610_548_Verified_Recovery_and_Updated_Data.zip` contains the following. `recovered_610/` contains the complete merged 610 main table, raw detailed table, exact-row-deduplicated detailed table, and matching original input list. `reference_548/` contains the original 430-input manifest, existing main table, unresolved FASTA path and accessions whose detailed output remains absent. `audit/` contains candidate-level membership decisions, checksum verification, source archive hashes and log comparisons. `combined_tables/` contains new versioned derivatives of the previous combined tables. The superseded 610 log-only rows are retained separately for provenance, not counted as extra records.

The companion `verify_recovery.py` uses only the Python standard library, validates table widths and identifiers, and refuses to overwrite an output directory. Seven synthetic unit tests passed locally under Python 3.13.5. The four generated combined tables were read back to verify row counts and widths. No biological values were inferred, replaced, or corrected from outside sources. Large working tables and original archives are not published by this documentation amendment.

## Next action

Do not rerun 610 or rename the 709 AMR files to 548. Search for a genuine older 548 detailed-output backup using the original 548 accession list. If no matching backup can be recovered, a clean rerun of the original 430 available 548 assemblies, in a new directory with safe FASTA paths and the recorded software/database environment, is the route to restoring complete main-plus-detailed output. The current 703-entry list must not be used for that rerun.
