import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent.parent


def run(*args):
    return subprocess.run([sys.executable, '-m', 'playbook', *map(str, args)], cwd=ROOT, capture_output=True, text=True)


class Phase1AcceptanceTests(unittest.TestCase):
    def test_critical_scaffold_introduces_controls_as_drafts(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            result = run('init', '--path', project, '--profile', 'business-critical', '--name', 'Example')
            self.assertEqual(result.returncode, 0, result.stderr)
            expectations = {
                'docs/00-governance/approvals.md': ('Independent review', 'separate release approval'),
                'docs/04-quality/traceability.md': ('Requirement IDs', 'critical tests'),
                'docs/04-quality/threat-model.md': ('threats and abuse cases', 'independent review'),
                'docs/05-operations/recovery.md': ('Recovery objectives', 'Restore test results'),
            }
            for name, phrases in expectations.items():
                with self.subTest(path=name):
                    content = (project / name).read_text()
                    self.assertIn('Status: draft', content)
                    self.assertIn('TBD.', content)
                    for phrase in phrases:
                        self.assertIn(phrase, content)
            gates = json.loads((ROOT / 'standards/quality-gates.yaml').read_text())['profiles']['business-critical']
            self.assertIn('independent review', gates['code'])
            self.assertIn('Separate business and technical approval', gates['release'])

    def test_existing_approved_file_is_preserved_for_each_profile(self):
        for profile in ('lean', 'standard', 'business-critical'):
            with self.subTest(profile=profile), tempfile.TemporaryDirectory() as tmp:
                project = Path(tmp)
                existing = project / 'docs/02-architecture/architecture.md'
                existing.parent.mkdir(parents=True)
                content = b'# Existing architecture\nStatus: approved\n'
                existing.write_bytes(content)
                result = run('audit', '--path', project, '--profile', profile)
                self.assertEqual(result.returncode, 1)
                self.assertEqual(existing.read_bytes(), content)
                result = run('init', '--path', project, '--profile', profile, '--name', 'Example')
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(existing.read_bytes(), content)


if __name__ == '__main__':
    unittest.main()
