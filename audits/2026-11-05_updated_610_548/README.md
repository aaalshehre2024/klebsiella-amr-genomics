# Full Kleborate and hAMRonization profiles for 610 and 548

Both source ZIPs supplied on 5 November 2026 contain a 117-column main table and a 32-column detailed hAMRonization table. Every versioned assembly accession in each collection’s 3 November input manifest appears once in the new main table and at least once in its detailed AMR table. These archives replace the previous source selections for these same inputs.

| Collection | Main coverage | Assemblies in detailed AMR | Supplied AMR rows | Exact-distinct AMR rows | Data |
|---|---:|---:|---:|---:|---|
| 610 · PDS000052355.137 | 503/503 | 503/503 | 13,826 | 8,939 | [Full profile](610/) · [Browse AMR](610/browse_amr/) · [Workbook](610/610_profile.xlsx) |
| 548 · PDS000041740.207 | 430/430 | 430/430 | 9,652 | 6,430 | [Full profile](548/) · [Browse AMR](548/browse_amr/) · [Workbook](548/548_profile.xlsx) |

Both tables in each collection are exact copies of the native final files in the selected ZIP. The separately named exact-distinct derivative removes rows that agree across all 32 columns. Each assembly contributes once to an assembly-level profile. Multiple annotation records may belong to one assembly. Both detailed tables report Kleborate 3.2.4 and CARD 3.2.9. Their `Predicted_phenotype` field contains a dash throughout.

## Changes since the previous selection

**610.** The earlier 503 strain names and all 3,521 previously reported non-identifier values agree with the corresponding new main-table values. The selected archive includes six abbreviated batch logs and the full merged main and AMR tables. The merged hAMRonization table is verified against the original input identifiers. Independent reconstruction of the upstream merge would require the individual batch AMR files.

**548.** The five sets of batch tables reproduce both merged tables byte for byte. The accession missing from the earlier main table, `GCA_054407865.1`, now has a full main record and 24 detailed AMR rows (13 exact-distinct). It is called ST307, KL102 and OL2α.2. Across the 429 earlier main records, 35 missing-locus-gene fields in 34 assemblies differ only in list order after matching on versioned accession. The source inventory includes a previous results ZIP without a genome FASTA, and two FASTA paths for the restored accession. All 430 unique inputs are accounted for.

The two current manifests share no exact versioned assembly accessions. Study-wide isolate counts and NCBI cluster or tree membership require reconciliation with the other packages and frozen source metadata. [Remaining work before manuscript Results](PAPER_READINESS.md)

## Files and reproducibility

- Use the collection folders above for the native tables, individual accession profiles, gene/variant summaries, and observed joint ST–K–O–carbapenemase profiles.
- The [source register](source_register.tsv) identifies the input ZIPs and the source member for each native table. [SHA256SUMS.txt](SHA256SUMS.txt) covers the published files in this update.
- The [earlier audit](../2026-11-03_selected_610_548/) documents the evidence available on 3 November. The [technical case ledger](technical_input_status.tsv) tracks how this update changes the 57 named cases from the combined audit.

To rebuild the TSVs, run the following commands from this directory in a repository checkout. Supply the two original input ZIPs. Each output argument should point to a new directory. The earlier reference directories supply the published accession manifests and comparison tables.

```bash
python3 scripts/audit_610_update.py "/path/to/PDS000052355_137_610_F_FINAL_kleborate_results.zip" ../2026-11-03_selected_610_548/610 /tmp/nov5_610
python3 scripts/build_548_profile.py "/path/to/548_PDS000041740.207_F_run_20261104_212002_RvReFw_FINAL_kleborate_results.zip" ../2026-11-03_selected_610_548/548 /tmp/nov5_548
for folder in /tmp/nov5_610 /tmp/nov5_548; do
  python3 scripts/summarize_profiles.py "$folder"
  python3 scripts/browse_hamr.py "$folder"
done
```
