from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent.parent


def init(project, profile):
    return subprocess.run([sys.executable, '-m', 'playbook', 'init', '--path', str(project), '--profile', profile, '--name', 'Example'], cwd=ROOT, text=True, capture_output=True)


class ReferenceScaffoldTests(unittest.TestCase):
    def test_each_profile_has_reference_guide(self):
        for profile in ('lean', 'standard', 'business-critical'):
            with self.subTest(profile=profile), tempfile.TemporaryDirectory() as tmp:
                result = init(tmp, profile)
                self.assertEqual(result.returncode, 0, result.stderr)
                guide = Path(tmp) / 'docs/08-reference/README.md'
                self.assertTrue(guide.is_file())
                self.assertIn('Authoritative project requirements', guide.read_text())

    def test_existing_reference_material_is_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp) / 'docs/08-reference'
            directory.mkdir(parents=True)
            guide = directory / 'README.md'
            source = directory / 'source.md'
            guide.write_text('Existing guide')
            source.write_text('Existing source')
            result = init(tmp, 'standard')
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('preserved: docs/08-reference/README.md', result.stdout)
            self.assertEqual(guide.read_text(), 'Existing guide')
            self.assertEqual(source.read_text(), 'Existing source')


if __name__ == '__main__':
    unittest.main()
