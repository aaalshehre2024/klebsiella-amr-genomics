# Collection 548 · PDS000041740.207

All 430 original assembly accessions have one full main record and detailed AMR output. The 9,652 supplied hAMRonization records reduce to 6,430 exact-distinct rows. The previously unresolved GCA_054407865.1 contributes one main record and 24 raw (13 exact-distinct) detailed AMR rows.

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
| [Excel profile workbook](548_profile.xlsx) | Coverage, accession profiles, all 117 native main fields, joint profiles and field counts |
| [Download the research package](548_research_data.zip) | Workbook, full data and supporting documentation |
| [Verification summary](summary.json) · [Source members](source_members.tsv) | Counts, source-file details, and integrity checks |
| [Changes to historical rows](prior_comparison.tsv) | Reordered missing-locus-gene lists on the 429 shared main-table accessions |

The main table calls 423 of 430 assemblies exact ST307. Among assemblies jointly labelled exact ST307, typeable KL102 and typeable OL2α.2, 225 have a dash in Bla_Carb_acquired, 128 have KPC as the sole unflagged family and 52 have NDM as the sole unflagged family. Other combinations appear in the full joint table.

For family summaries, each unflagged family in `Bla_Carb_acquired` counts once per assembly. Allele tokens ending in `*`, `?` or `^` are tabulated separately. A dash denotes no call reported in this field. OXA is a broad family label in these descriptive summaries. Return to the allele field to distinguish its subfamilies. The gene/variant table preserves the native text, so drug-class capitalization variants remain separate. All observations describe genomic annotations for this selected collection.

[Source ZIP and native table checksums](../source_register.tsv) · [Manuscript readiness](../PAPER_READINESS.md)
