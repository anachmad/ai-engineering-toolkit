import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = (ROOT / 'skills/software-engineering-playbook/templates/sad-template.md').read_text()


def run(doc):
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / 'sad.md'
        path.write_text(doc)
        cmd = [sys.executable, str(ROOT / 'playbook'), 'validate-artifact', '--artifact', 'sad', '--standard-version', '1', '--profile', 'standard', '--path', str(path)]
        return subprocess.run(cmd, capture_output=True, text=True)


class SADTests(unittest.TestCase):
    def test_template_and_missing_structure(self):
        report = json.loads(run(TEMPLATE).stdout)
        self.assertEqual(report['outcome'], 'WARN')
        self.assertFalse(report['release_authorized'])
        self.assertFalse(report['profile_applicability_enforced'])
        self.assertEqual(run(TEMPLATE.replace('## System Context', '## Other')).returncode, 1)
        self.assertEqual(run(TEMPLATE.replace('| Owner | TBD |', '')).returncode, 1)

    def test_decision_status_and_missing_fields(self):
        section = '## Architecture Decisions & Trade-offs'
        before, after = TEMPLATE.split(section, 1)
        placeholder = '| TBD | TBD | TBD | TBD | TBD |'
        def doc(row):
            return before + section + after.replace(placeholder, row, 1)
        self.assertEqual(run(doc('| ADR-001 | Context | Choice | Trade-off | Proposed |')).returncode, 0)
        self.assertEqual(run(doc('| ADR-001 | Context | Choice | Trade-off | Done |')).returncode, 1)
        self.assertEqual(run(doc('| ADR-001 | | Choice | Trade-off | Proposed |')).returncode, 1)
        result = json.loads(run(doc('| ADR-001 | Context | Choice | Trade-off | Accepted |')).stdout)
        self.assertTrue(any('not verified' in f['message'] for f in result['findings']))

    def test_not_applicable_needs_reason(self):
        self.assertEqual(run(TEMPLATE.replace('## System Context\n\nTBD', '## System Context\n\nNot applicable')).returncode, 1)
        self.assertEqual(run(TEMPLATE.replace('## System Context\n\nTBD', '## System Context\n\nNot applicable — standalone')).returncode, 0)

    def test_existing_scaffolds_remain_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp:
            cmd = [sys.executable, str(ROOT / 'playbook'), 'init', '--path', tmp, '--profile', 'lean', '--name', 'Demo']
            self.assertEqual(subprocess.run(cmd, capture_output=True).returncode, 0)
            path = Path(tmp) / 'docs/02-architecture/architecture.md'
            self.assertNotEqual(path.read_text(), TEMPLATE)
            path.write_text('Existing architecture')
            self.assertEqual(subprocess.run(cmd, capture_output=True).returncode, 0)
            self.assertEqual(path.read_text(), 'Existing architecture')


if __name__ == '__main__':
    unittest.main()
