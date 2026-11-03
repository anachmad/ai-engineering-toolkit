import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from playbook.brd import validate

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = json.loads((ROOT / 'standards/brd-v1.json').read_text())
EXAMPLE = (ROOT / 'examples/brd-example.md').read_text()
TEMPLATE = (ROOT / 'skills/software-engineering-playbook/templates/brd-template.md').read_text()


def errors(text):
    return [x['message'] for x in validate(text, CONTRACT) if x['level'] == 'ERROR']


class BrdTests(unittest.TestCase):
    def test_template_and_example_have_valid_structure(self):
        self.assertEqual(errors(TEMPLATE), [])
        self.assertEqual(errors(EXAMPLE), [])
        self.assertTrue(any(x['level'] == 'WARN' for x in validate(EXAMPLE, CONTRACT)))

    def test_bad_order_and_missing_section(self):
        self.assertTrue(errors(EXAMPLE.replace('## Executive Summary', '## Other')))
        self.assertTrue(errors(EXAMPLE.replace('## Executive Summary', '### Executive Summary')))

    def test_duplicate_and_bad_ids(self):
        self.assertTrue(any('Duplicate ID' in x for x in errors(EXAMPLE.replace('| BO-001 | Improve request handling. |', '| BO-001 | Improve request handling. |\n| BO-001 | Another objective |'))))
        self.assertTrue(errors(EXAMPLE.replace('| BR-001 | Users need', '| BR-01 | Users need')))

    def test_references_measurement_and_metadata(self):
        self.assertTrue(any('reference' in x for x in errors(EXAMPLE.replace('Users need a way to submit a request. | BO-001', 'Users need a way to submit a request. | BO-999'))))
        self.assertTrue(any('measurement' in x for x in errors(EXAMPLE.replace('Count of completed requests per month; method and source TBD', 'TBD'))))
        self.assertTrue(any('metadata' in x.lower() for x in errors(EXAMPLE.replace('| Owner | TBD |', ''))))
        self.assertTrue(any('subheading' in x for x in errors(EXAMPLE.replace('### Decisions', '### Other'))))

    def test_generation_and_preservation(self):
        with tempfile.TemporaryDirectory() as tmp:
            cmd = [sys.executable, str(ROOT / 'playbook'), 'init', '--path', tmp, '--profile', 'standard', '--name', 'Example']
            self.assertEqual(subprocess.run(cmd, capture_output=True).returncode, 0)
            brd = Path(tmp) / 'docs/01-requirements/business-requirements.md'
            self.assertEqual(brd.read_text(), TEMPLATE)
            brd.write_text('Existing BRD')
            self.assertEqual(subprocess.run(cmd, capture_output=True).returncode, 0)
            self.assertEqual(brd.read_text(), 'Existing BRD')
            brd.write_text(EXAMPLE)
            check = subprocess.run([sys.executable, str(ROOT / 'playbook'), 'validate-brd', '--path', str(brd)], capture_output=True, text=True)
            self.assertEqual(check.returncode, 0, check.stderr)
            self.assertIn('no approval implied', check.stdout)
            brd.write_text('## Invalid')
            self.assertEqual(subprocess.run([sys.executable, '-m', 'playbook', 'validate-brd', '--path', str(brd)], cwd=ROOT, capture_output=True).returncode, 1)

    def test_standard_matches_contract(self):
        standard = (ROOT / 'skills/software-engineering-playbook/references/brd-standard.md').read_text()
        headings = [line[3:] for line in standard.splitlines() if line.startswith('## ')][:-1]
        self.assertEqual(headings, CONTRACT['sections'])


if __name__ == '__main__':
    unittest.main()
