import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = (ROOT / 'skills/software-engineering-playbook/templates/adr-template.md').read_text()


def run(text, extra=()):
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / 'adr.md'
        path.write_text(text)
        cmd = [sys.executable, str(ROOT / 'playbook'), 'validate-artifact', '--artifact', 'adr', '--standard-version', '1', '--profile', 'standard', '--path', str(path), *map(str, extra)]
        return subprocess.run(cmd, text=True, capture_output=True)


class ADRTests(unittest.TestCase):
    def test_template_is_draft_and_does_not_approve(self):
        result = run(TEMPLATE)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report['outcome'], 'WARN')
        self.assertFalse(report['release_authorized'])
        self.assertEqual(report['human_approval'], 'NOT_VERIFIED')
        self.assertEqual(run(TEMPLATE.replace('## Context', '## Wrong')).returncode, 1)

    def test_metadata_formats_dates_status_and_na(self):
        for source, replacement in [('| ID | TBD |', '| ID | ADR-01 |'), ('| Date | TBD |', '| Date | 2026-02-30 |'), ('| Decision status | TBD |', '| Decision status | Done |'), ('| Document status | draft |', '| Document status | accepted |'), ('| Title | TBD |', ''), ('| Supersedes / superseded by | TBD |', '| Supersedes / superseded by | Not applicable |'), ('| Title | TBD |', '| Title | Not applicable — reason |')]:
            with self.subTest(replacement=replacement):
                self.assertEqual(run(TEMPLATE.replace(source, replacement)).returncode, 1)
        valid = TEMPLATE.replace('| ID | TBD |', '| ID | ADR-001 |').replace('| Date | TBD |', '| Date | 2026-11-24 |').replace('| Supersedes / superseded by | TBD |', '| Supersedes / superseded by | Not applicable — first decision |')
        self.assertEqual(run(valid).returncode, 0)
        self.assertEqual(run(valid.replace('| ID | ADR-001 |', '| ID | ADR-001 |\n| ID | ADR-002 |')).returncode, 1)

    def test_not_applicable_formatting_cannot_bypass_rules(self):
        for body in ('- Not applicable', '> Not applicable', '**Not applicable**'):
            with self.subTest(body=body):
                result = run(TEMPLATE.replace('## Context\n\nTBD', '## Context\n\n' + body))
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        result = run(TEMPLATE.replace('| Title | TBD |', '| Title | **Not applicable** |'))
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)

    def test_empty_rendered_section_is_error(self):
        for body in ('<!-- no content -->', '```\n```'):
            with self.subTest(body=body):
                result = run(TEMPLATE.replace('## Context\n\nTBD', '## Context\n\n' + body))
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual(run(TEMPLATE.replace('## Context\n\nTBD', '## Context\n\n```text\nactual content\n```')).returncode, 0)

    def test_sad_only_option_is_rejected_for_adr(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run(TEMPLATE, ['--project-root', tmp, '--sad-id-sources', Path(tmp) / 'missing.json'])
            self.assertEqual(result.returncode, 2)
            self.assertIn('SAD', result.stderr)

    def test_project_id_format_and_unknown_version(self):
        with tempfile.TemporaryDirectory() as tmp:
            config = Path(tmp) / 'formats.json'
            config.write_text(json.dumps({'schema_version': 1, 'formats': {'ADR': [{'prefix': 'DEC-', 'digits': 2}]}}))
            text = TEMPLATE.replace('| ID | TBD |', '| ID | DEC-01 |')
            self.assertEqual(run(text, ['--id-formats', config]).returncode, 0)
            self.assertEqual(run(text).returncode, 1)

    def test_selected_project_local_link_missing_or_outside(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            doc = root / 'adr.md'
            def execute(body):
                doc.write_text(TEMPLATE.replace('## Context\n\nTBD', '## Context\n\n'+body))
                return subprocess.run([sys.executable, str(ROOT / 'playbook'), 'validate-artifact', '--artifact', 'adr', '--standard-version', '1', '--profile', 'standard', '--path', str(doc), '--project-root', str(root)], capture_output=True, text=True)
            self.assertEqual(execute('[missing](missing.md)').returncode, 1)
            self.assertEqual(execute('[outside](../outside.md)').returncode, 1)
            (root / 'exists.md').write_text('evidence')
            report = json.loads(execute('[existing](exists.md)').stdout)
            self.assertTrue(any(x['status'] == 'CHECKED_FILE_EXISTS' for x in report['reference_checks']))
            self.assertEqual(report['human_approval'], 'NOT_VERIFIED')


if __name__ == '__main__':
    unittest.main()
