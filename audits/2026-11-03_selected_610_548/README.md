# Selected research sources for 610 and 548

The study author designated one ZIP per package on 3 November 2026. Use the SHA-256 values in the [source register](source_register.tsv) to identify these inputs. Each extract is built independently from its own archive. The PDS and collection labels follow the source package. Independent validation of membership against a frozen NCBI export or tree requires additional evidence.

## 610 (PDS000052355.137)

All 503 versioned assembly accessions in the selected FASTA manifest match a row in one of six batch logs. Each row has the strain identifier and seven reported values: species, N50, ST, virulence score, resistance score, resistance-class count and resistance-gene count. This source supports analysis of those fields. Individual resistance determinants, individual virulence loci, K/O types and typing-confidence fields are unavailable. Detailed hAMRonization output is unavailable.

One outer source folder uses GCF_036905415.1, while the selected FASTA basename and its logged strain begin with GCA_036905415.1. The extract keeps both labels and uses the versioned FASTA accession for linkage inside this package.

## 548 (PDS000041740.207)

The archive lists 431 raw FASTA paths for 430 distinct versioned assembly accessions. Two paths refer to GCA_054407865.1. The main Kleborate table contains 429 distinct rows across 117 original fields. All 429 match the input manifest and the five batch logs agree on the strain and seven shared values. Use the main table for assembly-level summaries, including the reported marker, QC and locus-confidence fields. The logs provide a cross-check on the same assemblies. Detailed hAMRonization output is unavailable.

GCA_054407865.1 occurs in the package's skipped-input file. A shell syntax error appears before the species-check failure in batch_002.log. Retain this accession in the input denominator of 430 with technical outcome unresolved. It contributes no result to the 429-row main table. Across the 430 selected paths, 26 outer folder accessions differ from the FASTA accession by the GCA/GCF prefix. Keep both labels for provenance.

## Rebuild each extract

Run the [standard-library Python script](../../scripts/build_selected_kleborate.py) once per selected archive from the repository root. The second argument is a new or empty output directory. The script checks the ZIP hash and integrity, the accession and strain joins, and agreement between available source tables. It reads the original Kleborate outputs directly.

```bash
python3 scripts/build_selected_kleborate.py 'PDS000052355_137_610_FINAL_kleborate_results(2).zip' local_outputs/selected_610
python3 scripts/build_selected_kleborate.py 'PDS000041740_207_548_FINAL_kleborate_results(2).zip' local_outputs/selected_548
```

The research extracts preserve source strings, including ST variants, repeated marker names and call qualifiers. Gene and class counts in the logs are software-reported summary values. A missing table is an availability status. The two extracts establish package-specific coverage only.
