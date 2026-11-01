import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent.parent


class PortabilityTests(unittest.TestCase):
    def test_adapters_resolve_from_other_project(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            for host, discovery in [('codex', '.agents'), ('claude', '.claude')]:
                link = project / discovery / 'skills' / 'software-engineering-playbook'
                link.parent.mkdir(parents=True)
                link.symlink_to(ROOT / 'adapters' / host / 'software-engineering-playbook', target_is_directory=True)
                adapter = (link / 'SKILL.md').resolve(strict=True)
                toolkit = adapter.parent.parent.parent.parent
                self.assertEqual(toolkit, ROOT)
                self.assertTrue((toolkit / 'skills/software-engineering-playbook/SKILL.md').is_file())
                self.assertTrue((toolkit / 'standards/profiles.yaml').is_file())

    def test_scaffolder_runs_outside_toolkit(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / 'project'
            result = subprocess.run([sys.executable, str(ROOT / 'playbook'), 'init', '--path', str(project), '--profile', 'lean', '--name', 'Portable'], cwd=tmp, text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            manifest = json.loads((project / '.engineering/project.yaml').read_text())
            self.assertEqual(manifest['standards_path'], str(ROOT / 'standards'))
            result = subprocess.run([sys.executable, str(ROOT / 'playbook'), 'audit', '--path', str(project)], cwd=tmp, text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == '__main__':
    unittest.main()
