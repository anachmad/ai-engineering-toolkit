import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / 'skills/software-engineering-playbook/templates/prd-template.md'
CONTRACT = json.loads((ROOT / 'standards/prd-v1.json').read_text())


def validate(path):
    return subprocess.run([sys.executable, str(ROOT / 'playbook'), 'validate-artifact', '--artifact', 'prd', '--standard-version', '1', '--profile', 'standard', '--path', str(path)], capture_output=True, text=True)


class PrdStructureTests(unittest.TestCase):
    def test_template_and_standard_match_approved_headings(self):
        self.assertEqual([x[3:] for x in TEMPLATE.read_text().splitlines() if x.startswith('## ')], CONTRACT['sections'])
        standard = (ROOT / 'skills/software-engineering-playbook/references/prd-standard.md').read_text()
        self.assertEqual([x[3:] for x in standard.splitlines() if x.startswith('## ')][:-1], CONTRACT['sections'])
        result = validate(TEMPLATE)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report['outcome'], 'WARN')
        self.assertEqual(report['validation_scope'], 'section structure only')
        self.assertFalse(report['release_authorized'])

    def test_invalid_structure_and_fenced_headings(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'prd.md'
            original = TEMPLATE.read_text()
            for text in (original.replace('## Executive Summary', '## Other'), original.replace('## Executive Summary\n\nTBD', '## Executive Summary\n\n')):
                path.write_text(text)
                self.assertEqual(validate(path).returncode, 1)
            path.write_text(original.replace('## Executive Summary\n\nTBD', '## Executive Summary\n\n```markdown\n## Ignore\n```\n\nTBD'))
            self.assertEqual(validate(path).returncode, 0)

    def test_standard_scaffold_preserves_existing_prd(self):
        with tempfile.TemporaryDirectory() as tmp:
            command = [sys.executable, str(ROOT / 'playbook'), 'init', '--path', tmp, '--profile', 'standard', '--name', 'Example']
            self.assertEqual(subprocess.run(command, capture_output=True).returncode, 0)
            path = Path(tmp) / 'docs/01-requirements/product-requirements.md'
            self.assertEqual(path.read_text(), TEMPLATE.read_text())
            path.write_text('existing')
            self.assertEqual(subprocess.run(command, capture_output=True).returncode, 0)
            self.assertEqual(path.read_text(), 'existing')


if __name__ == '__main__':
    unittest.main()
