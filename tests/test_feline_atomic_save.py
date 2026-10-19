import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/cad'))
from feline_atomic_save import save_json


class AtomicSave(unittest.TestCase):
    def test_transient_lock_preserves_previous_receipt_and_retries(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'receipt.json';save_json(path,dict(old=True))
            replace=Path.replace;calls=[]
            def locked(source,destination):
                calls.append(1)
                if len(calls)<3:
                    self.assertEqual(json.loads(path.read_text()),dict(old=True))
                    raise PermissionError(13,'Access is denied')
                return replace(source,destination)
            with patch.object(Path,'replace',locked):save_json(path,dict(new=True),delay=0)
            self.assertEqual(len(calls),3)
            self.assertEqual(json.loads(path.read_text()),dict(new=True))

    def test_persistent_lock_is_reported_and_previous_receipt_kept(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'receipt.json';save_json(path,dict(old=True))
            with patch.object(Path,'replace',side_effect=PermissionError(13,'Access is denied')):
                with self.assertRaises(PermissionError):save_json(path,dict(new=True),attempts=2,delay=0)
            self.assertEqual(json.loads(path.read_text()),dict(old=True))
            self.assertEqual(json.loads(path.with_suffix('.writing.json').read_text()),dict(new=True))


if __name__=='__main__':unittest.main()
