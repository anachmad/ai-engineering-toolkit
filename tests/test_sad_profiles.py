import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONCISE = (ROOT / 'skills/software-engineering-playbook/templates/sad-concise-template.md').read_text()
FULL = (ROOT / 'skills/software-engineering-playbook/templates/sad-template.md').read_text()
BRD = (ROOT / 'examples/brd-example.md').read_text()


class SADProfileTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        (self.base / '.engineering').mkdir()
        self.doc = self.base / 'architecture.md'
        self.doc.write_text(CONCISE)

    def manifest(self, profile='standard', **extra):
        (self.base / '.engineering/project.yaml').write_text(json.dumps({'schema_version': 1, 'profile': profile, **extra}))

    def run_cli(self, profile='standard', project=True, extra=()):
        cmd = [sys.executable, str(ROOT / 'playbook'), 'validate-artifact', '--artifact', 'sad', '--standard-version', '2', '--profile', profile, '--path', str(self.doc)]
        if project:
            cmd += ['--project-root', str(self.base)]
        return subprocess.run(cmd + list(map(str, extra)), capture_output=True, text=True)

    def test_profile_mode_and_backward_compatible_manifest(self):
        self.manifest()
        out = json.loads(self.run_cli().stdout)
        self.assertEqual(out['sad_applicability'], 'REVIEW_REQUIRED')
        self.assertFalse(out['profile_applicability_enforced'])
        self.manifest(sad_mode='concise')
        out = json.loads(self.run_cli().stdout)
        self.assertEqual(out['sad_mode'], 'concise')
        self.assertEqual(out['outcome'], 'WARN')
        self.manifest('lean')
        self.assertEqual(json.loads(self.run_cli('lean').stdout)['sad_mode'], 'concise')
        self.manifest('business-critical', sad_mode='concise')
        self.assertEqual(self.run_cli('business-critical').returncode, 2)
        self.manifest('business-critical')
        self.assertEqual(self.run_cli('business-critical').returncode, 1)
        self.doc.write_text(FULL)
        self.assertEqual(self.run_cli('business-critical').returncode, 0)

    def test_local_missing_external_anchor_escape_and_fence(self):
        self.manifest(sad_mode='concise')
        (self.base / 'requirements.md').write_text('example')
        self.doc.write_text(CONCISE.replace('## System Context\n\nTBD', '## System Context\n\n[local](requirements.md) [anchor](requirements.md#x) [external](https://example.org)\n\n```\n[ignored](missing.md)\n```'))
        report = json.loads(self.run_cli().stdout)
        statuses = [x['status'] for x in report['reference_checks']]
        self.assertIn('CHECKED_FILE_EXISTS', statuses)
        self.assertIn('ANCHOR_NOT_VERIFIED', statuses)
        self.assertIn('NOT_VERIFIED', statuses)
        self.assertFalse(any(x['target'] == 'missing.md' for x in report['reference_checks']))
        self.doc.write_text(CONCISE + '\n[missing](missing.md)\n')
        self.assertEqual(self.run_cli().returncode, 1)
        self.doc.write_text(CONCISE + '\n[out](../outside.md)\n')
        self.assertEqual(self.run_cli().returncode, 1)
        (self.base / 'escape').symlink_to('/tmp', target_is_directory=True)
        self.doc.write_text(CONCISE + '\n[out](escape/anything)\n')
        self.assertEqual(self.run_cli().returncode, 1)

    def test_explicit_sources(self):
        self.manifest(sad_mode='concise')
        (self.base / 'brd.md').write_text(BRD)
        sources = self.base / 'sources.json'
        sources.write_text(json.dumps({'BR': 'brd.md'}))
        self.doc.write_text(CONCISE.replace('## Architecture Goals & Drivers\n\nTBD', '## Architecture Goals & Drivers\n\nBR-001'))
        report = json.loads(self.run_cli(extra=['--sad-id-sources', sources]).stdout)
        self.assertTrue(any(c['status'] == 'CHECKED_ID_EXISTS' for c in report['reference_checks']))
        self.doc.write_text(CONCISE.replace('## Architecture Goals & Drivers\n\nTBD', '## Architecture Goals & Drivers\n\nBR-999'))
        self.assertEqual(self.run_cli(extra=['--sad-id-sources', sources]).returncode, 1)
        sources.write_text(json.dumps({'BR': '../outside.md'}))
        self.assertEqual(self.run_cli(extra=['--sad-id-sources', sources]).returncode, 2)


if __name__ == '__main__':
    unittest.main()
