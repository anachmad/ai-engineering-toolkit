import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRS = (ROOT / 'skills/software-engineering-playbook/templates/srs-template.md').read_text()
PRD = (ROOT / 'skills/software-engineering-playbook/templates/prd-template.md').read_text()
PLACE = '| TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD |'
VALID = '| FR-001 | Submit a request | PR-001 | Must | Signed in | Confirmation shown | N/A — no special handling | Test | Draft |'


def run(text, extra=()):
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / 'srs.md'
        path.write_text(text)
        return subprocess.run([sys.executable, str(ROOT / 'playbook'), 'validate-artifact', '--artifact', 'srs', '--standard-version', '1', '--profile', 'standard', '--path', str(path), *map(str, extra)], capture_output=True, text=True)


class SRSTests(unittest.TestCase):
    def test_template_and_structure(self):
        report = json.loads(run(SRS).stdout)
        self.assertEqual(report['outcome'], 'WARN')
        self.assertFalse(report['release_authorized'])
        self.assertEqual(run(SRS.replace('## Introduction', '## Wrong')).returncode, 1)
        self.assertEqual(run(SRS.replace('| Title | TBD |', '')).returncode, 1)

    def test_fields_and_duplicates(self):
        for row in (VALID.replace('FR-001', 'FR-01'), VALID.replace('Must', 'Urgent'), VALID.replace('Test', 'Guess'), VALID.replace('Draft', 'Done'), VALID.replace('N/A — no special handling', 'N/A'), VALID.replace('Submit a request', 'N/A — reason'), VALID + '\n' + VALID):
            with self.subTest(row=row):
                self.assertEqual(run(SRS.replace(PLACE, row, 1)).returncode, 1)
        self.assertEqual(run(SRS.replace(PLACE, VALID, 1)).returncode, 0)

    def test_project_format_priority_and_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            formats = tmp / 'formats.json'
            formats.write_text(json.dumps({'schema_version': 1, 'formats': {'FR': [{'prefix': 'F-A', 'digits': 2}]}}))
            priorities = tmp / 'priority.json'
            priorities.write_text(json.dumps(['P0', 'P1']))
            prd = tmp / 'prd.md'
            prd.write_text(PRD.replace('| TBD | TBD | TBD | TBD | TBD | TBD | TBD |', '| PR-001 | Need | BR-001 | Must | User | Done | Draft |'))
            doc = SRS.replace(PLACE, VALID.replace('FR-001', 'F-A01').replace('Must', 'P0'), 1)
            flags = ['--id-formats', formats, '--srs-priorities', priorities, '--prd-source', prd]
            result = run(doc, flags)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)['prd_source_check']['status'], 'CHECKED_ID_EXISTENCE')
            self.assertEqual(run(doc.replace('PR-001', 'PR-999'), flags).returncode, 1)
            self.assertEqual(run(doc, ['--id-formats', formats]).returncode, 1)
            prd.write_text('invalid')
            self.assertEqual(run(doc, flags).returncode, 2)

    def test_scaffold_preserves_existing(self):
        with tempfile.TemporaryDirectory() as tmp:
            cmd = [sys.executable, str(ROOT / 'playbook'), 'init', '--path', tmp, '--profile', 'standard', '--name', 'Demo']
            self.assertEqual(subprocess.run(cmd, capture_output=True).returncode, 0)
            path = Path(tmp) / 'docs/01-requirements/system-requirements.md'
            self.assertEqual(path.read_text(), SRS)
            path.write_text('Existing SRS')
            self.assertEqual(subprocess.run(cmd, capture_output=True).returncode, 0)
            self.assertEqual(path.read_text(), 'Existing SRS')


if __name__ == '__main__':
    unittest.main()
