import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / 'examples/brd-example.md'


def call(*args):
    return subprocess.run([sys.executable, str(ROOT / 'playbook'), 'validate-artifact', *args], cwd=ROOT, text=True, capture_output=True)


def args(path=EXAMPLE, version='1', profile='standard', kind='brd'):
    return ['--artifact', kind, '--standard-version', version, '--profile', profile, '--path', str(path)]


class ArtifactFrameworkTests(unittest.TestCase):
    def test_registry_paths_and_pending_contracts(self):
        registry = json.loads((ROOT / 'standards/artifacts-v1.json').read_text())
        self.assertEqual(registry['artifacts']['brd']['status'], 'approved')
        for key in ('contract', 'standard', 'template', 'example'):
            self.assertTrue((ROOT / registry['artifacts']['brd']['versions']['1'][key]).is_file())
        self.assertTrue(all(v['status'] == 'proposed' for k, v in registry['artifacts'].items() if k not in ('brd', 'prd')))

    def test_profiles_report_warning_without_approval(self):
        for profile in ('lean', 'standard', 'business-critical'):
            with self.subTest(profile=profile):
                result = call(*args(profile=profile))
                self.assertEqual(result.returncode, 0, result.stderr)
                report = json.loads(result.stdout)
                self.assertEqual(report['outcome'], 'WARN')
                self.assertFalse(report['profile_applicability_enforced'])
                self.assertEqual(report['human_approval'], 'NOT_VERIFIED')
                self.assertFalse(report['release_authorized'])

    def test_failure_and_version_approval_boundary(self):
        with tempfile.TemporaryDirectory() as tmp:
            invalid = Path(tmp) / 'invalid.md'
            invalid.write_text(EXAMPLE.read_text().replace('## Document Information', '## Incorrect'))
            result = call(*args(path=invalid))
            self.assertEqual(result.returncode, 1)
            self.assertEqual(json.loads(result.stdout)['outcome'], 'FAIL')
        for options in (args(version='99'), args(kind='srs'), args(kind='unknown'), args(profile='lite')):
            self.assertEqual(call(*options).returncode, 2)

    def test_shared_snapshot_has_validator_and_reference(self):
        with tempfile.TemporaryDirectory() as tmp:
            shared = subprocess.run([sys.executable, str(ROOT / 'playbook'), 'share', '--path', tmp], capture_output=True, text=True)
            self.assertEqual(shared.returncode, 0, shared.stderr)
            toolkit = Path(tmp) / '.engineering/toolkit'
            self.assertTrue((toolkit / 'skills/software-engineering-playbook/references/documentation-validation.md').is_file())
            result = subprocess.run([sys.executable, str(toolkit / 'playbook'), 'validate-artifact', *args()], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)['outcome'], 'WARN')


if __name__ == '__main__':
    unittest.main()
