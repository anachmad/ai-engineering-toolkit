import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import playbook.__main__ as playbook

ROOT = Path(__file__).resolve().parent.parent


class PolicyValidationTests(unittest.TestCase):
    def test_valid_policy_loads(self):
        profiles, prompts = playbook.load_policy()
        self.assertEqual(profiles['default_profile'], 'standard')
        self.assertIn('docs/04-quality/threat-model.md', prompts['documents'])

    def test_rejects_invalid_policy_before_scaffolding(self):
        cases = (
            ('profiles.yaml', lambda p: p.update(default_profile='unknown')),
            ('profiles.yaml', lambda p: p['profiles']['lean']['artifacts'].append('../escape')),
            ('profiles.yaml', lambda p: p['profiles']['lean']['artifacts'].append('docs/no-prompt.md')),
            ('quality-gates.yaml', lambda p: p['profiles']['standard'].pop('release')),
            ('quality-gates.yaml', lambda p: p['profiles']['lean'].update(security='')),
            ('document-prompts.yaml', lambda p: p['documents'].update({'docs/02-architecture/architecture.md': []})),
        )
        for filename, change in cases:
            with self.subTest(filename=filename), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                shutil.copytree(ROOT / 'standards', root / 'standards')
                path = root / 'standards' / filename
                policy = json.loads(path.read_text())
                change(policy)
                path.write_text(json.dumps(policy))
                with patch.object(playbook, 'ROOT', root), self.assertRaises(ValueError):
                    playbook.load_policy()

    def test_invalid_manifest_is_rejected_and_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            result = subprocess.run([sys.executable, '-m', 'playbook', 'init', '--path', tmp, '--profile', 'lean', '--name', 'Example'], cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            manifest_path = project / '.engineering/project.yaml'
            manifest = json.loads(manifest_path.read_text())
            manifest['status'] = 'unrecognized'
            content = json.dumps(manifest)
            manifest_path.write_text(content)
            for command in (['audit', '--path', tmp], ['init', '--path', tmp, '--profile', 'lean', '--name', 'Example']):
                result = subprocess.run([sys.executable, '-m', 'playbook', *command], cwd=ROOT, capture_output=True, text=True)
                self.assertEqual(result.returncode, 2, result.stdout)
                self.assertEqual(manifest_path.read_text(), content)

    def test_generated_documents_have_relevant_prompts(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run([sys.executable, '-m', 'playbook', 'init', '--path', tmp, '--profile', 'business-critical', '--name', 'Example'], cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            project = Path(tmp)
            threat = (project / 'docs/04-quality/threat-model.md').read_text()
            recovery = (project / 'docs/05-operations/recovery.md').read_text()
            self.assertIn('trust boundaries', threat)
            self.assertIn('Restore test', recovery)
            self.assertIn('TBD.', threat)
            self.assertNotIn('{{', threat)


if __name__ == '__main__':
    unittest.main()
