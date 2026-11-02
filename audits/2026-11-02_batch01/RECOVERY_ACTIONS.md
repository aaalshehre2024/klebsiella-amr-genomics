# Recovery actions: first 19 packages

No complete collection needs a blanket rerun. Recover existing full outputs first. Preserve the original uploaded archives and add corrected packages as new versions with new hashes.

| Priority | Package | Evidence needed |
|---|---|---|
| Critical | P06 / M_K5 | Recreate the complete result ZIP from the original Ubuntu run; test it with `unzip -tq`; re-upload it with full main/hAMR tables, input list and logs. The uploaded file is unreadable. |
| Critical | P17 / 610 | Recover the complete main Kleborate and hAMRonization tables, preferably including batch output directories. The current package has 503 log-only records. |
| Critical | P14 / 548 | Recover hAMRonization. Copy GCA_054407865.1 FASTA to a path without spaces/parentheses, rerun to a new output directory, and review the new log. A shell syntax error is not evidence of taxonomic exclusion. |
| High | P03 / M_K2 | Resolve upstream archive GCA_021968515.1.zip listed in bad_zip_files.txt, or document why it remains unavailable. Matching 917 extracted inputs to 917 outputs does not resolve the failed download. |
| High | P02 / M_K1 | Supply the original 846-input manifest, omitted three accession identifiers, reasons and logs. The clean export contains 843 full outputs only. |
| High | All | Supply frozen NCBI metadata exports, PDS/PDT/assembly/BioSample mappings, selection criteria and matching Newick files with exact versions and dates. |

## Already handled in this audit

The unrelated 429-row 548 main table copied into P19 was excluded from P19's selected data and retained in provenance. The original files were not deleted. The 158 repeated accession observations were recorded, with a separate accession-deduplicated derivative. Source marker flags were not stripped or reinterpreted.

## Keep unresolved evidence explicit

Do not mark incomplete packages as zero biological findings. Do not substitute log summaries for missing K/O or locus-level data. Do not combine technical batch labels into separate biological collections, and do not infer source snapshot dates from ZIP file timestamps.
