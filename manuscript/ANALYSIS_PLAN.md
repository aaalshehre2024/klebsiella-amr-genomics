# Manuscript analysis and writing plan

Status: proposed analyses following inspection of the first 19 result packages. This is not a claim of preregistration or of completed downstream analyses.

## Cohort first

Treat packages, technical batches, versioned NCBI collections, assembly accessions and biological isolates as separate entities. Complete an accession-to-PDS/PDT/BioSample crosswalk and record source query, selection rationale, exact export/download dates and tree version. M_K batches and PDG labels cannot define independent SNP clusters. Keep primary verified metadata/tree collections separate from exploratory expanded collections. Preserve version differences such as PDS000267523.7 versus .12; do not silently replace an older snapshot.

Recover the unreadable M_K5 package, full 610 outputs and missing 548 hAMRonization. Review the 548 technical failure, M_K2 upstream archive failure and M_K1 unexplained omissions. Missing evidence is not gene absence, and a shell error is not a taxonomic exclusion.

## Table 1: cohort flow and evidence availability

For each verified collection, report source-record count, eligible assembly identifiers, downloadable FASTAs, full main outputs, detailed hAMRonization availability, technical unresolved inputs, documented biological exclusions if established, and metadata/tree linkage. State all denominators. The first-tranche count of 11,306 accession.version identifiers is not yet the final unique-isolate total.

## Table 2 and Figure 2: joint lineage–surface-antigen–carbapenemase profiles

Summarize actual same-assembly combinations of ST, K locus, O type and carbapenemase family after fixing typing-confidence and uncertainty rules. Do not combine separate marginal modes into an unobserved joint profile. Report missing and uncertain typing explicitly. Prioritize comparisons within the same ST; lineage dominance in a selected SNP cluster is expected and is not the principal novelty.

## Figure 3: resistance architecture

Use accepted exported main-table carbapenemase calls as the primary annotation layer and hAMRonization for detailed traceability. Preserve exact alleles, truncation/uncertainty flags and alternative families. Freeze OXA-48-like membership; not every OXA annotation is an OXA-48-like carbapenemase. Count each marker once per assembly for frequencies and retain raw hit counts separately. Identical repeated rows are not independent copy-number evidence. Keep the study's custom architecture categories distinct from the Kleborate resistance score.

## Figure 4: resistance–virulence co-detection

Analyze full same-assembly outputs with explicit completeness and uncertainty rules. Preserve ybt, clb, iuc, iro and rmp-related calls separately. A nonempty field may encode an interrupted or uncertain call. Define conservative and inclusive co-detection analyses transparently. Do not equate a genomic profile with experimentally demonstrated hypervirulence, clinical severity, expression, or plasmid co-localization. Rule changes made after seeing data must be labeled exploratory.

## Figure 5: verified tree mapping

Use an exact accession-to-tip crosswalk for the frozen PDS/tree version. Do not map expanded assemblies to old trees by folder name. Report unmatched records. Separate cluster trees are not a single global phylogeny. Describe within-collection structuring without inferring direct transmission or independent acquisition events. Formal association testing is optional and requires appropriate treatment of phylogenetic dependence.

## Essential sensitivity checks

Recalculate pooled results after accession deduplication and verified GCA/GCF/BioSample linkage. Compare complete-output collections with eligible main-output-only collections. Compare conservative with inclusive call handling. Compare the frozen primary cohort with the exploratory extension. Quantify assembly availability and missingness by collection and, where source metadata permit, geography, source and date. Avoid population-prevalence claims from convenience samples.

## Writing order

Write the study-design and provenance sections during recovery. Draft numeric Results only from approved tables, in this order: cohort flow; joint genomic profiles; resistance architecture; co-detection; verified tree mapping; sensitivity findings. Revise the Introduction to the final scope and write the Abstract last. Every numerical claim must link to a source table, denominator, script version and release.

## Publication release

No final scientific dataset is released yet. The current repository contains audit/provenance documentation and the writing plan. The downloadable audit bundle contains detailed working tables, code, explicit package selections and tests. Upload the reviewed code/data release only after the listed issues and data-sharing decisions are resolved. Do not invent a DOI, acceptance status, exact sampling period or institutional determination.
