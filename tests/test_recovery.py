import tempfile,unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from stage_failed_inputs import stage
class RecoveryTests(unittest.TestCase):
    def test_space_in_source_path_is_preserved(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t);s=p/'unzipped'/'GCF_123456789.1 ';s.mkdir(parents=True)
            f=s/'GCA_123456789.1_genomic.fna';f.write_bytes(b'>x\nACTG\n')
            paths=p/'paths.txt';paths.write_text(str(f.relative_to(p))+'\n')
            self.assertEqual(stage(p,paths,p/'safe'),0)
            self.assertEqual((p/'safe'/f.name).read_bytes(),f.read_bytes())
    def test_missing_source_does_not_run(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t);paths=p/'paths.txt';paths.write_text('absent.fna\n')
            self.assertEqual(stage(p,paths,p/'safe'),2)
            self.assertEqual((p/'safe/ready_fasta_paths.txt').read_text(),'')
