import json
import hashlib
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent.parent


def run(toolkit, cwd, *args):
    return subprocess.run([sys.executable, str(toolkit / 'playbook'), *map(str, args)], cwd=cwd, text=True, capture_output=True)


class SharedProjectTests(unittest.TestCase):
    def test_shared_project_can_move_and_scaffold(self):
        with tempfile.TemporaryDirectory() as tmp:
            old = Path(tmp) / 'original'
            old.mkdir()
            result = run(ROOT, tmp, 'share', '--path', old)
            self.assertEqual(result.returncode, 0, result.stderr)
            moved = Path(tmp) / 'moved'
            shutil.move(old, moved)
            toolkit = moved / '.engineering/toolkit'
            provenance = json.loads((toolkit / 'provenance.json').read_text())
            path = 'standards/profiles.yaml'
            self.assertEqual(provenance['files'][path], hashlib.sha256((toolkit / path).read_bytes()).hexdigest())
            for host, folder in [('codex', '.agents'), ('claude', '.claude')]:
                link = moved / folder / 'skills/software-engineering-playbook'
                self.assertEqual(link.resolve(), toolkit / 'adapters' / host / 'software-engineering-playbook')
                self.assertFalse(Path(link.readlink()).is_absolute())
            result = run(toolkit, moved, 'init', '--path', moved, '--profile', 'standard', '--name', 'Shared example')
            self.assertEqual(result.returncode, 0, result.stderr)
            manifest = json.loads((moved / '.engineering/project.yaml').read_text())
            self.assertEqual(manifest['standards_path'], '.engineering/toolkit/standards')
            moved_again = Path(tmp) / 'moved-again'
            shutil.move(moved, moved_again)
            result = run(moved_again / '.engineering/toolkit', moved_again, 'audit', '--path', moved_again)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((moved_again / manifest['standards_path']).is_dir())

    def test_existing_skill_is_preserved_and_no_toolkit_created(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            skill = project / '.claude/skills/software-engineering-playbook/SKILL.md'
            skill.parent.mkdir(parents=True)
            skill.write_text('existing skill')
            result = run(ROOT, tmp, 'share', '--path', project)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(skill.read_text(), 'existing skill')
            self.assertFalse((project / '.engineering/toolkit').exists())
            self.assertFalse((project / '.agents').exists())

    def test_repeated_share_preserves_project_toolkit(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            self.assertEqual(run(ROOT, tmp, 'share', '--path', project).returncode, 0)
            marker = project / '.engineering/toolkit/standards/documentation-standard.md'
            contents = marker.read_bytes()
            self.assertEqual(run(ROOT, tmp, 'share', '--path', project).returncode, 2)
            self.assertEqual(marker.read_bytes(), contents)


if __name__ == '__main__':
    unittest.main()
