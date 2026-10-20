import tempfile
import unittest
from pathlib import Path
from rules_loader import load_rule, load_academic_taxonomy
from validate_rules import validate

class ResourceTests(unittest.TestCase):
    def test_all_resource_contracts(self):
        self.assertEqual(validate()['status'], 'PASS')

    def test_metadata_does_not_enter_vocabulary(self):
        self.assertNotIn('__prompt__', load_rule('rules/synonyms.json'))
        self.assertTrue(all(isinstance(x,str) for x in load_rule('rules/protected_terms.json')))

    def test_duplicate_keys_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)/'bad.json'
            p.write_text('{"same": 1, "same": 2}')
            with self.assertRaisesRegex(ValueError, 'Duplicate JSON key'):
                load_rule(p)

    def test_recursive_loader_and_provenance(self):
        records = load_academic_taxonomy()
        self.assertEqual(len({r['discipline'] for r in records}),5)
        self.assertTrue(all(r['source_file'].endswith('.json') for r in records))

if __name__ == '__main__':
    unittest.main()
