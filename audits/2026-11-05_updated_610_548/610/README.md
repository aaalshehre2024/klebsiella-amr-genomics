# Collection 610 · PDS000052355.137

All 503 original assembly accessions have one full main record and detailed AMR output. The 13,826 supplied hAMRonization records reduce to 8,939 exact-distinct rows. The seven non-identifier values from each of the 503 historical logs agree with the new main table.

| File | Contents |
|---|---|
| [Accession profiles](accession_profile.tsv) | One row per versioned assembly, selected reported calls, source linkage and detailed-AMR row counts |
| [Complete main table](main_results.tsv) | All 117 native fields |
| [Browse individual AMR records](browse_amr/) | Smaller linked files with all 32 fields and an accession lookup |
| [Complete detailed AMR table](hamronization.tsv) | All source annotation rows in their supplied order |
| [Exact-distinct AMR table](hamronization_exact_unique.tsv) | One copy of each distinct combination of all 32 fields |
| [Reported gene and variant counts](gene_variation_counts.tsv) | Exact gene, mutation, variation-type and drug-class combinations, with source-row and distinct-assembly counts |
| [Observed joint profiles](observed_joint_profiles.tsv) | Same-assembly ST, K/O locus and typeability, and unflagged acquired-carbapenemase families |
| [Field counts](profile_counts.tsv) | Exact STs, K/O loci and typeability, scores, QC, and reported or flagged carbapenemase calls |
| [Excel profile workbook](610_profile.xlsx) | Coverage, accession profiles, all 117 native main fields, joint profiles and field counts |
| [Download the research package](610_research_data.zip) | Workbook, full data and supporting documentation |
| [Verification summary](summary.json) · [Source members](source_members.tsv) | Counts, source-file details, and integrity checks |

The main table calls 495 of 503 assemblies exact ST258. In 390 assemblies, exact ST258, typeable KL107, typeable OL2α.2 and KPC as the sole unflagged acquired carbapenemase family occur together. Forty-nine O-locus calls are Untypeable. Retain that field when deciding eligibility for serotype analyses.

For family summaries, each unflagged family in `Bla_Carb_acquired` counts once per assembly. Allele tokens ending in `*`, `?` or `^` are tabulated separately. A dash denotes no call reported in this field. OXA is a broad family label in these descriptive summaries. Return to the allele field to distinguish its subfamilies. The gene/variant table preserves the native text, so drug-class capitalization variants remain separate. All observations describe genomic annotations for this selected collection.

[Source ZIP and native table checksums](../source_register.tsv) · [Manuscript readiness](../PAPER_READINESS.md)
