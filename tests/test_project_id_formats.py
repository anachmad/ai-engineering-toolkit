import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORMATS = ROOT / 'examples/filio-pilot-id-formats.json'
PRD = (ROOT / 'skills/software-engineering-playbook/templates/prd-template.md').read_text()
BRD = (ROOT / 'examples/brd-example.md').read_text()


def run(kind, version, document, formats=FORMATS):
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / 'document.md'
        path.write_text(document)
        command = [sys.executable, str(ROOT / 'playbook'), 'validate-artifact', '--artifact', kind, '--standard-version', version, '--profile', 'standard', '--path', str(path)]
        if formats is not None:
            command += ['--id-formats', str(formats)]
        return subprocess.run(command, capture_output=True, text=True)


class ProjectIdTests(unittest.TestCase):
    def test_prd_legacy_and_defaults(self):
        line = '| F-A01 | Submit request | BR-01 | Must | User | Acknowledged | Draft |'
        text = PRD.replace('| TBD | TBD | TBD | TBD | TBD | TBD | TBD |', line)
        result = run('prd', '3', text)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['outcome'], 'WARN')
        self.assertEqual(run('prd', '3', text, None).returncode, 1)
        self.assertEqual(run('prd', '3', text.replace(line, line + '\n' + line)).returncode, 1)
        self.assertEqual(run('prd', '3', text.replace('F-A01', 'F-Z01')).returncode, 1)
        self.assertEqual(run('prd', '2', text).returncode, 2)

    def test_brd_links_use_configured_format(self):
        text = BRD.replace('BR-001', 'BR-01')
        result = run('brd', '2', text)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(run('brd', '2', text, None).returncode, 1)
        self.assertEqual(run('brd', '2', text.replace('| BO-001 | BR-01 | KPI-001 |', '| BO-001 | BR-02 | KPI-001 |')).returncode, 1)
        self.assertEqual(run('brd', '1', text).returncode, 2)

    def test_invalid_config_and_real_format_not_proof_of_whole_document(self):
        with tempfile.TemporaryDirectory() as tmp:
            config = Path(tmp) / 'invalid.json'
            for content in ({'schema_version': 1, 'formats': {'PR': [{'prefix': '.*', 'digits': 2}]}}, {'schema_version': 1, 'formats': {'PR': [{'prefix': 'F-A', 'digits': True}]}}):
                config.write_text(json.dumps(content))
                self.assertEqual(run('prd', '3', PRD, config).returncode, 2)
        pilot = Path('/home/andik/project/filio-pilot/Filio_PRD_v2-1.md')
        if pilot.exists():
            self.assertEqual(run('prd', '3', pilot.read_text()).returncode, 1)


if __name__ == '__main__':
    unittest.main()
