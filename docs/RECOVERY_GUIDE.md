# Targeted recovery guide — preserve original results

Do not rerun every collection. Recover M_K5 and missing output tables first; address the named failed inputs separately. The combined audit bundle includes exact original FASTA paths under recovery/ and a safe staging script. No source genome files are present in the result archives, so reruns must be performed where the original FASTAs exist.

## Missing output tables

Inside Ubuntu, locate existing full tables without changing files:

```bash
find "$HOME/klebsiella_project" -type f \( -name '*klebsiella_pneumo_complex_output.txt' -o -name '*hAMRonization_output.txt' \) -print
```

For M_K5, rebuild a new ZIP from the original complete result directory and test it with `unzip -t`. Renaming or reuploading the same damaged ZIP is not a repair. Preserve old and new archives under different names. The [5 November update](../audits/2026-11-05_updated_610_548/) documents complete main and detailed tables for 610 and 548, and recovery of the missing 548 main result.

## Failed FASTA inputs

The historical lists contain 57 named cases. The current recovery queue covers P34/A_K1 (52), P20/A_K3 (1), and P33/A_1716 (3). P14/548 is resolved. Use the [current ledger](../audits/2026-11-05_updated_610_548/technical_input_status.tsv) to select inputs. Original paths may contain spaces or parentheses. First locate the original run directory containing its unzipped/ folder.

Run the staging script separately for each package, using the actual original project directory and a NEW safe destination:

```bash
python3 scripts/stage_failed_inputs.py --project /home/YOUR_USER/klebsiella_project/ORIGINAL_RUN --paths-file recovery/P34_unresolved_fasta_paths.txt --destination /home/YOUR_USER/klebsiella_recovery/P34_attempt_01
```

The staging script copies readable FASTAs, records original-to-safe paths and uncompressed SHA-256 values, and stops short of running Kleborate. Inspect staging_manifest.csv; every requested input must be STAGED. Do not run an empty ready list. It does not rename or delete originals.

After confirming the original Kleborate version and database environment, run the staged files from their safe directory into a NEW output folder. Use Bash arrays and check the exit status:

```bash
mapfile -t FASTAS < /home/YOUR_USER/klebsiella_recovery/P34_attempt_01/ready_fasta_paths.txt
if [ "${#FASTAS[@]}" -gt 0 ]; then
  kleborate -a "${FASTAS[@]}" -o /home/YOUR_USER/klebsiella_recovery/P34_results_01 -p kpsc --trim_headers > /home/YOUR_USER/klebsiella_recovery/P34_attempt_01/run.log 2>&1
  echo "Kleborate exit status: $?"
fi
```

A zero exit status still requires accession-level reconciliation of the main and detailed output. A species-check message accompanied by execution errors remains technical/unresolved. Preserve repaired outputs as new provenance and audit them before merging. Do not append blindly to old final tables.

## Other outstanding decisions

M_K1 needs the original input accession manifest identifying its three omitted genomes. M_K2 needs resolution of GCA_021968515.1.zip upstream. Keep PDS000267523.7 and .12 separate until frozen metadata establishes the chosen primary snapshot and sensitivity comparison.
