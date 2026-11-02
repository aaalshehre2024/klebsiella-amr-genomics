import contextlib,hashlib,importlib.util,io,json,sys,tempfile,unittest,zipfile
from pathlib import Path
S=Path(__file__).resolve().parents[1]/'scripts'
sys.path.insert(0,str(S))
from reconcile_uploads import canonicalize
from audit_submission import audit

class ReconcileTests(unittest.TestCase):
    def test_byte_identical_reuploads_fold_only_once(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp); payload=b'same archive bytes'
            specs=[]
            for i in range(2):
                name=f'upload{i}.zip';(p/name).write_bytes(payload)
                specs.append(dict(package_id=f'P{i}',filename=name,sha256=hashlib.sha256(payload).hexdigest()))
            canonical,registry=canonicalize(p,specs)
            self.assertEqual(len(canonical),1)
            self.assertEqual(registry[1]['canonical_package_id'],'P0')
    def test_hash_mismatch_stops(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp);(p/'x.zip').write_bytes(b'x')
            with self.assertRaises(ValueError):canonicalize(p,[dict(package_id='P1',filename='x.zip',sha256='0'*64)])
    def test_distinct_versions_not_deduplicated(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp);specs=[]
            for i in range(2):
                b=f'version{i}'.encode();n=f'{i}.zip';(p/n).write_bytes(b)
                specs.append(dict(package_id=f'P{i}',filename=n,sha256=hashlib.sha256(b).hexdigest()))
            self.assertEqual(len(canonicalize(p,specs)[0]),2)
    def test_conflicting_profiles_are_withheld(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp);specs=[]
            header=['strain','species','species_match','ST','K_locus','O_type','resistance_score','virulence_score','QC_warnings']
            for i,st in enumerate(['ST11','ST15']):
                row=['GCA_123456789.1_x','Klebsiella pneumoniae','strong',st,'KL64','O2','2','1','-']
                with zipfile.ZipFile(p/f'{i}.zip','w') as z:
                    z.writestr('main.txt','\t'.join(header)+'\n'+'\t'.join(row)+'\n')
                    z.writestr('run.log','ERROR: could not open unzipped/unsafe for reading.\n')
                specs.append(dict(package_id=f'P{i}',filename=f'{i}.zip',label=str(i),declared_database_identifier='PDS000000001.1',main_member='main.txt',hamr_member=''))
            m=p/'manifest.json';m.write_text(json.dumps(specs))
            with contextlib.redirect_stdout(io.StringIO()): result=audit(p,m,p/'out')
            self.assertEqual(result['substantive_main_profile_conflicts'],1)
            self.assertEqual(result['main_records_after_reconciliation'],0)
            self.assertIn('FILE_OPEN_ERROR',(p/'out/qc_issues.csv').read_text())
            self.assertNotIn('confirmed_taxonomic_exclusion',result)
    def test_empty_input_is_not_treated_as_completed(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp);m=p/'manifest.json';m.write_text('[]')
            with self.assertRaises(ValueError):audit(p,m,p/'out')

if __name__=='__main__':unittest.main()
