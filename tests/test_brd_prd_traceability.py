import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BRD = (ROOT / 'examples/brd-example.md').read_text().replace('BR-001', 'BR-01')
PRD = (ROOT / 'skills/software-engineering-playbook/templates/prd-template.md').read_text()
PLACEHOLDER = '| TBD | TBD | TBD | TBD | TBD | TBD | TBD |'
FORMATS = ROOT / 'examples/filio-pilot-id-formats.json'


def run(prd, brd=None, formats=FORMATS):
    with tempfile.TemporaryDirectory() as tmp:
        project = Path(tmp)
        p = project / 'prd.md'
        p.write_text(prd)
        cmd = [sys.executable, str(ROOT / 'playbook'), 'validate-artifact', '--artifact', 'prd', '--standard-version', '3', '--profile', 'business-critical', '--path', str(p), '--id-formats', str(formats)]
        if brd is not None:
            b = project / 'brd.md'
            b.write_text(brd)
            cmd.extend(['--brd-source', str(b)])
        return subprocess.run(cmd, capture_output=True, text=True)


def prd_with(source):
    return PRD.replace(PLACEHOLDER, f'| F-A01 | Submit request | {source} | Must | User | Acknowledged | Draft |')


class TraceabilityTests(unittest.TestCase):
    def test_existing_and_absent_sources(self):
        found = run(prd_with('BR-01'), BRD)
        self.assertEqual(found.returncode, 0, found.stderr)
        report = json.loads(found.stdout)
        self.assertEqual(report['brd_source_check']['status'], 'CHECKED_ID_EXISTENCE')
        self.assertFalse(report['release_authorized'])
        self.assertFalse(any('BR source' in f['message'] for f in report['findings']))
        missing = run(prd_with('BR-02'), BRD)
        self.assertEqual(missing.returncode, 1)
        self.assertTrue(any('BR-02 not found' in f['message'] for f in json.loads(missing.stdout)['findings']))

    def test_mixed_external_missing_format_and_no_brd(self):
        mixed = json.loads(run(prd_with('BR-01, Workshop record'), BRD).stdout)
        self.assertTrue(any('Workshop record' in f['message'] and 'not verified' in f['message'] for f in mixed['findings']))
        self.assertEqual(run(prd_with('BR-001'), BRD).returncode, 1)
        unchecked = json.loads(run(prd_with('BR-01')).stdout)
        self.assertEqual(unchecked['brd_source_check']['status'], 'NOT_RUN')
        self.assertTrue(any('BR-01' in f['message'] and 'not verified' in f['message'] for f in unchecked['findings']))

    def test_bad_source_brd_fails_closed(self):
        for document in (BRD.replace('## Business Requirements', '## Other'), BRD.replace('| BR-01 |', '| BR-01 |\n| BR-01 |', 1)):
            with self.subTest(document=document):
                result = run(prd_with('BR-01'), document)
                self.assertEqual(result.returncode, 2)
                self.assertNotIn('CHECKED_ID_EXISTENCE', result.stdout)


if __name__ == '__main__':
    unittest.main()
