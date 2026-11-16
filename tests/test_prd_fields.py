import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = (ROOT / 'skills/software-engineering-playbook/templates/prd-template.md').read_text()
PLACEHOLDER = '| TBD | TBD | TBD | TBD | TBD | TBD | TBD |'
VALID = '| PR-001 | A user can submit a request. | BR-001 | Must | User | A valid request is acknowledged. | Draft |'


def check(row, version='2'):
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / 'prd.md'
        path.write_text(TEMPLATE.replace(PLACEHOLDER, row))
        cmd = [sys.executable, str(ROOT / 'playbook'), 'validate-artifact', '--artifact', 'prd', '--standard-version', version, '--profile', 'standard', '--path', str(path)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode, json.loads(result.stdout)


class PrdFieldsTests(unittest.TestCase):
    def test_valid_and_tbd_are_warnings_not_approval(self):
        for row in (VALID, PLACEHOLDER, VALID.replace('Must', 'TBD')):
            with self.subTest(row=row):
                code, report = check(row)
                self.assertEqual(code, 0)
                self.assertEqual(report['outcome'], 'WARN')
                self.assertFalse(report['release_authorized'])
                self.assertEqual(report['human_approval'], 'NOT_VERIFIED')
        self.assertTrue(any('not verified' in x['message'] for x in check(VALID)[1]['findings']))

    def test_reject_bad_rows_and_duplicate_ids(self):
        cases = [VALID.replace('PR-001', 'PR-01'), VALID + '\n' + VALID,
                 VALID.replace('Must', 'Urgent'), VALID.replace('Draft', 'Done'),
                 VALID.replace('A user can submit a request.', ''), VALID.replace('| User |', '|'),
                 VALID.replace('PR-001', 'TBD')]
        for row in cases:
            with self.subTest(row=row):
                code, report = check(row)
                self.assertEqual(code, 1)
                self.assertEqual(report['outcome'], 'FAIL')

    def test_broken_table_and_legacy_v1(self):
        self.assertEqual(check(VALID.replace('PR-001', 'PR-01'), version='1')[0], 0)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'prd.md'
            path.write_text(TEMPLATE.replace('| ID | Description |', '| ID | Missing |'))
            cmd = [sys.executable, str(ROOT / 'playbook'), 'validate-artifact', '--artifact', 'prd', '--standard-version', '2', '--profile', 'standard', '--path', str(path)]
            self.assertEqual(subprocess.run(cmd, capture_output=True).returncode, 1)

    def test_external_source_and_escaped_pipe(self):
        row = VALID.replace('BR-001', 'Approved workshop record').replace('A user can submit a request.', r'A user can submit a request \| inquiry.')
        code, report = check(row)
        self.assertEqual(code, 0)
        self.assertTrue(any('Source' in x['message'] and 'not verified' in x['message'] for x in report['findings']))


if __name__ == '__main__':
    unittest.main()
