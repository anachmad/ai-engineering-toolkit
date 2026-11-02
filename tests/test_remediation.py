import json
import hashlib
import contextlib
import io
from types import SimpleNamespace
from unittest.mock import patch

import playbook.__main__ as playbook
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent.parent


def run(*args):
    return subprocess.run([sys.executable, '-B', '-m', 'playbook', *map(str, args)], cwd=ROOT, text=True, capture_output=True)


class RemediationTests(unittest.TestCase):
    def test_ancestor_symlink_is_reported_and_resolved(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            real = root / 'real'
            real.mkdir()
            (root / 'alias').symlink_to(real, target_is_directory=True)
            target = root / 'alias' / 'project'
            result = run('init', '--path', target, '--profile', 'lean', '--name', 'Sample')
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn(f'effective project path: {real / "project"}', result.stdout)

    def test_nonfile_conflict_fails_before_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'README.md').mkdir()
            result = run('init', '--path', root, '--profile', 'lean', '--name', 'Sample')
            self.assertEqual(result.returncode, 2)
            self.assertIn('README.md', result.stderr)
            self.assertFalse((root / '.engineering').exists())

    def test_ui_change_is_reviewed_and_apply_preserves_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(run('init', '--path', root, '--profile', 'standard', '--name', 'Sample').returncode, 0)
            manifest = root / '.engineering/project.yaml'
            before = manifest.read_bytes()
            proposal = run('set-ui', '--path', root, '--ui', 'yes')
            self.assertEqual(proposal.returncode, 0, proposal.stderr)
            self.assertEqual(manifest.read_bytes(), before)
            self.assertIn('unknown', proposal.stdout)
            self.assertFalse((root / 'docs/01-requirements/ui-ux.md').exists())
            applied = run('set-ui', '--path', root, '--ui', 'yes', '--apply', '--expected-sha256', hashlib.sha256(manifest.read_bytes()).hexdigest())
            self.assertEqual(applied.returncode, 0, applied.stderr)
            updated = json.loads(manifest.read_text())
            self.assertEqual(updated['ui'], 'yes')
            self.assertEqual(updated['name'], 'Sample')
            self.assertTrue((root / 'docs/01-requirements/ui-ux.md').is_file())
            self.assertEqual(run('audit', '--path', root).returncode, 0)

    def test_ui_existing_document_and_unknown_fields_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(run('init', '--path', root, '--profile', 'lean', '--name', 'Sample').returncode, 0)
            path = root / '.engineering/project.yaml'
            data = json.loads(path.read_text())
            data['custom_field'] = {'keep': True}
            path.write_text(json.dumps(data))
            ui = root / 'docs/01-requirements/ui-ux.md'
            ui.write_text('Status: approved\nExisting UI\n')
            self.assertEqual(run('set-ui', '--path', root, '--ui', 'yes', '--apply', '--expected-sha256', hashlib.sha256(path.read_bytes()).hexdigest()).returncode, 0)
            self.assertEqual(ui.read_text(), 'Status: approved\nExisting UI\n')
            self.assertEqual(json.loads(path.read_text())['custom_field'], {'keep': True})
            self.assertEqual(run('set-ui', '--path', root, '--ui', 'yes', '--apply', '--expected-sha256', hashlib.sha256(path.read_bytes()).hexdigest()).returncode, 0)
            self.assertEqual(run('set-ui', '--path', root, '--ui', 'no', '--apply', '--expected-sha256', hashlib.sha256(path.read_bytes()).hexdigest()).returncode, 0)
            self.assertTrue(ui.exists())
            self.assertEqual(json.loads(path.read_text())['ui'], 'no')

    def test_ui_apply_rejects_stale_or_missing_preview_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(run('init', '--path', root, '--profile', 'lean', '--name', 'Sample').returncode, 0)
            manifest = root / '.engineering/project.yaml'
            before = manifest.read_bytes()
            for expected in ([], ['--expected-sha256', '0' * 64]):
                result = run('set-ui', '--path', root, '--ui', 'yes', '--apply', *expected)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(manifest.read_bytes(), before)
                self.assertFalse((root / 'docs/01-requirements/ui-ux.md').exists())

    def test_ui_interrupted_manifest_replace_preserves_original(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(run('init', '--path', root, '--profile', 'lean', '--name', 'Sample').returncode, 0)
            manifest = root / '.engineering/project.yaml'
            before = manifest.read_bytes()
            policy, prompts = playbook.load_policy()
            args = SimpleNamespace(path=str(root), ui='yes', apply=True, expected_sha256=hashlib.sha256(before).hexdigest())
            with patch.object(playbook.os, 'replace', side_effect=OSError('simulated interruption')):
                with self.assertRaises(OSError), contextlib.redirect_stdout(io.StringIO()):
                    playbook.set_ui(args, policy, prompts)
            self.assertEqual(manifest.read_bytes(), before)
            self.assertTrue((root / 'docs/01-requirements/ui-ux.md').is_file())
            self.assertEqual(sorted(p.name for p in manifest.parent.iterdir()), ['project.yaml'])

    def test_unsupported_manifest_version_is_not_migrated(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(run('init', '--path', root, '--profile', 'lean', '--name', 'Sample').returncode, 0)
            path = root / '.engineering/project.yaml'
            data = json.loads(path.read_text())
            data['schema_version'] = 2
            content = json.dumps(data)
            path.write_text(content)
            self.assertEqual(run('audit', '--path', root).returncode, 2)
            self.assertEqual(path.read_text(), content)

    def test_missing_or_divergent_standards_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(run('init', '--path', root, '--profile', 'lean', '--name', 'Sample').returncode, 0)
            path = root / '.engineering/project.yaml'
            data = json.loads(path.read_text())
            data['standards_path'] = str(root / 'missing')
            path.write_text(json.dumps(data))
            result = run('audit', '--path', root)
            self.assertEqual(result.returncode, 2)
            self.assertIn('standards', result.stderr.lower())
            different = root / 'other-standards'
            different.mkdir()
            data['standards_path'] = str(different)
            path.write_text(json.dumps(data))
            result = run('audit', '--path', root)
            self.assertEqual(result.returncode, 2)
            self.assertIn('differs', result.stderr.lower())


if __name__ == '__main__':
    unittest.main()
