import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / 'skills/software-engineering-playbook/templates'


def run(*args):
    return subprocess.run([sys.executable, '-m', 'playbook', *map(str, args)], cwd=ROOT, text=True, capture_output=True)


class SadScaffoldingTests(unittest.TestCase):
    def test_each_profile_and_selected_standard_modes(self):
        for profile, mode, template in [('lean', None, 'sad-concise-template.md'), ('business-critical', None, 'sad-template.md'), ('standard', 'concise', 'sad-concise-template.md'), ('standard', 'full', 'sad-template.md')]:
            with self.subTest(profile=profile, mode=mode), tempfile.TemporaryDirectory() as tmp:
                args = ['init', '--path', tmp, '--profile', profile, '--name', 'Test']
                if mode:
                    args += ['--sad-mode', mode]
                result = run(*args)
                self.assertEqual(result.returncode, 0, result.stderr)
                architecture = Path(tmp) / 'docs/02-architecture/architecture.md'
                self.assertEqual(architecture.read_text(), (TEMPLATES / template).read_text())
                manifest = json.loads((Path(tmp) / '.engineering/project.yaml').read_text())
                if mode:
                    self.assertEqual(manifest['sad_mode'], mode)
                self.assertEqual(run(*args).returncode, 0)

    def test_explicit_profile_modes_are_idempotent(self):
        for profile, mode in [('lean', 'concise'), ('business-critical', 'full')]:
            with self.subTest(profile=profile), tempfile.TemporaryDirectory() as tmp:
                args = ['init', '--path', tmp, '--profile', profile, '--name', 'Test', '--sad-mode', mode]
                self.assertEqual(run(*args).returncode, 0)
                result = run(*args)
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_standard_mode_review_then_safe_selection(self):
        with tempfile.TemporaryDirectory() as tmp:
            args = ['init', '--path', tmp, '--profile', 'standard', '--name', 'Test']
            result = run(*args)
            self.assertEqual(result.returncode, 0)
            self.assertIn('REVIEW_REQUIRED', result.stdout)
            path = Path(tmp) / 'docs/02-architecture/architecture.md'
            self.assertFalse(path.exists())
            self.assertEqual(run('audit', '--path', tmp).returncode, 1)
            manifest = Path(tmp) / '.engineering/project.yaml'
            original = manifest.read_bytes()
            self.assertEqual(run('set-sad-mode', '--path', tmp, '--sad-mode', 'full').returncode, 0)
            self.assertEqual(manifest.read_bytes(), original)
            self.assertEqual(run('set-sad-mode', '--path', tmp, '--sad-mode', 'full', '--apply').returncode, 2)
            digest = hashlib.sha256(original).hexdigest()
            self.assertEqual(run('set-sad-mode', '--path', tmp, '--sad-mode', 'full', '--apply', '--expected-sha256', digest).returncode, 0)
            self.assertEqual(run(*args).returncode, 0)
            self.assertEqual(path.read_text(), (TEMPLATES / 'sad-template.md').read_text())
            self.assertEqual(run('audit', '--path', tmp).returncode, 0)

    def test_existing_and_conflicting_modes_are_safe(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'docs/02-architecture/architecture.md'
            path.parent.mkdir(parents=True)
            path.write_text('Approved original')
            self.assertEqual(run('init', '--path', tmp, '--profile', 'standard', '--name', 'Test', '--sad-mode', 'full').returncode, 0)
            self.assertEqual(path.read_text(), 'Approved original')
            self.assertEqual(run('init', '--path', tmp, '--profile', 'standard', '--name', 'Test', '--sad-mode', 'concise').returncode, 2)
            self.assertEqual(path.read_text(), 'Approved original')
        for profile, mode in [('lean', 'full'), ('business-critical', 'concise')]:
            with tempfile.TemporaryDirectory() as tmp:
                self.assertEqual(run('init', '--path', tmp, '--profile', profile, '--name', 'Test', '--sad-mode', mode).returncode, 2)
                self.assertFalse((Path(tmp) / '.engineering/project.yaml').exists())


if __name__ == '__main__':
    unittest.main()
