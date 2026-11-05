# Collection 548 · PDS000041740.207

**Historical source selection of 3 November.** The [updated 5 November profiles](../../2026-11-05_updated_610_548/548/) contain full main and detailed AMR outputs for all selected inputs. The counts below describe the original files in this folder.

Of **430 listed assemblies**, **429** have a full main-table record. Use the main table for the reported AMR markers, virulence loci and K/O typing, retaining the QC and confidence fields when selecting assemblies. The five batch logs corroborate the same 429 records. The selected ZIP lacks detailed hAMRonization output.

The input manifest retains `GCA_054407865.1` as technically unresolved. It appears twice in the raw FASTA paths and once in the unique input list. Its batch log records a shell syntax error before the species-check failure.

| File | Contents |
|---|---|
| [Main assembly results](main_results.tsv) | All 117 original fields for 429 assemblies with the versioned accession and source-table line |
| [Batch log results](log_results.tsv) | The eight fields shared with the main table for the same 429 assemblies |
| [Input manifest](input_manifest.tsv) | One entry for each of the 430 listed assemblies and its result status |
| [Input path evidence](input_path_evidence.tsv) | All 431 raw FASTA paths, including the two paths for the unresolved assembly |
| [Diagnostic lines](diagnostic_lines.tsv) | Three diagnostic messages and their original log lines |
| [Source member checksums](source_members.tsv) | Archive members with sizes and SHA-256 checksums |
| [Audit summary](audit.json) | Source ZIP identity, record counts and output availability |
| [Excel workbook](PDS000041740_207_548.xlsx) | Collection overview and selected fields across all 430 input records |
| [Research data ZIP](PDS000041740_207_548_Research_Data.zip) | Workbook, full tables, checksums and extraction script |
