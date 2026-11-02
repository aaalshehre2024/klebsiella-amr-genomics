import contextlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

SPEC = importlib.util.spec_from_file_location('audit_submission', Path(__file__).resolve().parents[1] / 'scripts' / 'audit_submission.py')
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

class AuditTests(unittest.TestCase):
    def test_versioned_accessions_preserved(self):
        self.assertEqual(MODULE.accession('GCA_001234567.2_assembly'), 'GCA_001234567.2')
        self.assertNotEqual(MODULE.accession('GCA_001234567.2'), MODULE.accession('GCF_001234567.2'))
        self.assertNotEqual(MODULE.accession('GCA_001234567.1'), MODULE.accession('GCA_001234567.2'))
    def test_leading_accession_not_embedded_alias(self):
        self.assertEqual(MODULE.accession('GCA_963900295.1_ena-yuan-GCF_902508075.1_genomic'), 'GCA_963900295.1')
    def test_fasta_path_normalization(self):
        self.assertEqual(MODULE.strain_name('/tmp/folder (1)/GCA_001234567.2_genomic.fna.gz'), 'GCA_001234567.2_genomic')
    def test_tsv_validation(self):
        with self.assertRaises(ValueError): MODULE.parse_tsv('strain\tST\na\n')
        with self.assertRaises(ValueError): MODULE.parse_tsv('strain\tST\nstrain\tST\n')
        with self.assertRaises(ValueError): MODULE.parse_tsv('strain\tstrain\na\tb\n')
    def test_list_order_only(self):
        a={'strain':'x','K_Missing_expected_genes':'A;B','ST':'ST11'}
        b={'strain':'x','K_Missing_expected_genes':'B;A','ST':'ST11'}
        self.assertEqual(MODULE.comparable(a),MODULE.comparable(b))
        b['ST']='ST15'; self.assertNotEqual(MODULE.comparable(a),MODULE.comparable(b))
        b=dict(a); b['K_Missing_expected_genes']='A;A;B'
        self.assertNotEqual(MODULE.comparable(a),MODULE.comparable(b))
    def test_archive_integration_and_overwrite_guard(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            hdr=['strain','species','species_match','ST','K_locus','O_type','resistance_score','virulence_score','QC_warnings']
            vals=['GCA_001234567.2_x','Klebsiella pneumoniae','strong','ST11','KL64','O2','2','1','-']
            text='\t'.join(hdr)+'\n'+'\t'.join(vals)+'\n'
            specs=[]
            for i in range(2):
                name=f'package_{i}.zip'
                with zipfile.ZipFile(root/name,'w') as z:
                    z.writestr('main.txt',text)
                    z.writestr('input.txt','/tmp/GCA_001234567.2_x.fna\n')
                    if i==1: z.writestr('foreign_klebsiella_pneumo_complex_output.txt',text)
                specs.append(dict(package_id=f'P{i}', filename=name,label=name,
                    declared_database_identifier='PDS000000001.1',main_member='main.txt',hamr_member='',input_member='input.txt'))
            (root/'broken.zip').write_bytes(b'PK\x03\x04broken')
            specs.append(dict(package_id='P2',filename='broken.zip',label='broken',declared_database_identifier='PDG000000001.1',main_member='',hamr_member=''))
            manifest=root/'manifest.json'; manifest.write_text(json.dumps(specs))
            with contextlib.redirect_stdout(io.StringIO()): result=MODULE.audit(root,manifest,root/'audit')
            self.assertEqual(result['readable_archives'],2)
            self.assertEqual(result['unreadable_archives'],1)
            self.assertEqual(result['main_package_records'],2)
            self.assertEqual(result['distinct_versioned_assembly_accessions'],1)
            self.assertEqual(result['duplicate_main_observations'],1)
            self.assertEqual(result['excluded_extra_main_members'],1)
            self.assertEqual(result['packages_with_selected_hamr'],0)
            with self.assertRaises(FileExistsError): MODULE.audit(root,manifest,root/'audit')

if __name__=='__main__': unittest.main()
