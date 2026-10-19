from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import FreeCAD as A
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/cad'))
from feline_persistent_receiver import PinnedWorld


class PersistentWorld(unittest.TestCase):
    def test_no_reload_but_fresh_source_digest_required(self):
        calls=[];world=SimpleNamespace(pins={'source.json':'abc'})
        def load():calls.append(1);return world,{'part':'immutable'}
        cached=PinnedWorld(load)
        first=cached()
        with patch('feline_persistent_receiver.sha',return_value='abc') as digest:
            self.assertIs(cached(),first);self.assertEqual(digest.call_count,1)
        self.assertEqual(len(calls),1)
        with patch('feline_persistent_receiver.sha',return_value='changed'):
            with self.assertRaises(AssertionError):cached()
        self.assertEqual(len(calls),1)


if __name__=='__main__':unittest.main()
