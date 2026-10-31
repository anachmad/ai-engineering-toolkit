import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent.parent


def run(*args):
    return subprocess.run([sys.executable, '-m', 'playbook', *map(str, args)], cwd=ROOT, text=True, capture_output=True)


class PlaybookTests(unittest.TestCase):
    def test_profiles_and_idempotence(self):
        for profile in ('lean', 'standard', 'business-critical'):
            with self.subTest(profile=profile), tempfile.TemporaryDirectory() as tmp:
                args = ('init', '--path', tmp, '--profile', profile, '--name', 'Example')
                self.assertEqual(run(*args).returncode, 0)
                project = Path(tmp)
                original = (project / 'README.md').read_bytes()
                self.assertEqual(run(*args).returncode, 0)
                self.assertEqual((project / 'README.md').read_bytes(), original)
                self.assertEqual(run('audit', '--path', tmp).returncode, 0)
                self.assertEqual(json.loads((project / '.engineering/project.yaml').read_text())['profile'], profile)
                if profile == 'business-critical':
                    self.assertTrue((project / 'docs/04-quality/threat-model.md').exists())
                    self.assertTrue((project / 'docs/05-operations/recovery.md').exists())

    def test_preserves_existing_approved_document(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'docs/02-architecture/architecture.md'
            path.parent.mkdir(parents=True)
            path.write_text('Status: approved\nExisting architecture\n')
            result = run('init', '--path', tmp, '--profile', 'standard', '--name', 'Example')
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(path.read_text(), 'Status: approved\nExisting architecture\n')
            self.assertIn('preserved:', result.stdout)

    def test_symlink_rejected_before_writes(self):
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as outside:
            (Path(tmp) / 'docs').symlink_to(outside, target_is_directory=True)
            result = run('init', '--path', tmp, '--profile', 'lean', '--name', 'Example')
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse((Path(tmp) / 'README.md').exists())
            self.assertEqual(list(Path(outside).iterdir()), [])

    def test_missing_and_ui(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(run('init', '--path', tmp, '--profile', 'standard', '--name', 'Example', '--ui').returncode, 0)
            ui = Path(tmp) / 'docs/01-requirements/ui-ux.md'
            self.assertTrue(ui.exists())
            ui.unlink()
            self.assertEqual(run('audit', '--path', tmp).returncode, 1)

    def test_adapters_reference_same_skill_and_standards(self):
        shared = (ROOT / 'skills/software-engineering-playbook/SKILL.md').resolve()
        for host in ('claude', 'codex'):
            adapter = ROOT / 'adapters' / host / 'software-engineering-playbook/SKILL.md'
            self.assertIn('../../../skills/software-engineering-playbook/SKILL.md', adapter.read_text())
            self.assertEqual((adapter.parent / '../../../skills/software-engineering-playbook/SKILL.md').resolve(), shared)
        for name in ('profiles.yaml', 'quality-gates.yaml', 'documentation-standard.md'):
            self.assertIn('standards/' + name, shared.read_text())

    def test_audit_existing_repository_without_manifest_is_read_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            approved = Path(tmp) / 'README.md'
            approved.write_text('Status: approved\n')
            result = run('audit', '--path', tmp, '--profile', 'standard')
            self.assertEqual(result.returncode, 1)
            self.assertIn('missing: .engineering/project.yaml', result.stdout)
            self.assertEqual(approved.read_text(), 'Status: approved\n')
            self.assertEqual([p.name for p in Path(tmp).iterdir()], ['README.md'])

    def test_profile_change_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(run('init', '--path', tmp, '--profile', 'lean', '--name', 'Example').returncode, 0)
            self.assertEqual(run('init', '--path', tmp, '--profile', 'standard', '--name', 'Example').returncode, 2)
            self.assertFalse((Path(tmp) / 'docs/04-quality/traceability.md').exists())


if __name__ == '__main__':
    unittest.main()
