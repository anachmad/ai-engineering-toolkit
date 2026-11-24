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

    def test_concise_metadata_can_be_plain_text(self):
        self.manifest(sad_mode='concise')
        table = '| Field | Value |\n| --- | --- |\n| Title | TBD |\n| Version | TBD |\n| Status | Draft |\n| Owner | TBD |\n| Date | TBD |'
        plain = '- Title: Example\n- Version: 1\n- Status: Draft\n- Owner: Owner\n- Date: TBD'
        self.doc.write_text(CONCISE.replace(table, plain))
        result = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.doc.write_text(CONCISE.replace(table, plain.replace('- Owner: Owner\n', '')))
        self.assertEqual(self.run_cli().returncode, 1)

    def test_inline_code_and_urls_are_not_ids_or_links(self):
        self.manifest(sad_mode='concise')
        (self.base / 'brd.md').write_text(BRD)
        sources = self.base / 'sources.json'
        sources.write_text(json.dumps({'BR': 'brd.md'}))
        body = 'See https://example.com/BR-999, [external](https://example.com/BR-998), `BR-997` and ``cat [x](missing.md)``.'
        self.doc.write_text(CONCISE.replace('## System Context\n\nTBD', '## System Context\n\n' + body))
        result = self.run_cli(extra=['--sad-id-sources', sources])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        checks = json.loads(result.stdout)['reference_checks']
        self.assertTrue(any(c['status'] == 'NOT_VERIFIED' for c in checks))
        self.assertFalse(any(c['status'] in ('MISSING', 'MISSING_ID') for c in checks))

    def test_escaped_backticks_keep_real_missing_link_visible(self):
        self.manifest(sad_mode='concise')
        self.doc.write_text(CONCISE.replace('## System Context\n\nTBD', '## System Context\n\n' + r'\` [missing](missing.md) \`'))
        result = self.run_cli()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        checks = json.loads(result.stdout)['reference_checks']
        self.assertTrue(any(c['target'] == 'missing.md' and c['status'] == 'MISSING' for c in checks))

    def test_multiline_inline_code_does_not_generate_link_findings(self):
        self.manifest(sad_mode='concise')
        self.doc.write_text(CONCISE.replace('## System Context\n\nTBD', '## System Context\n\n`example\n[missing](missing.md)\nexample`'))
        result = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse(any(c['target'] == 'missing.md' for c in json.loads(result.stdout)['reference_checks']))

    def test_backticks_inside_link_destination_are_literal(self):
        self.manifest(sad_mode='concise')
        self.doc.write_text(CONCISE.replace('## System Context\n\nTBD', '## System Context\n\n[file](file`code`.md)'))
        result = self.run_cli()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        checks = json.loads(result.stdout)['reference_checks']
        self.assertTrue(any(c['target'] == 'file`code`.md' and c['status'] == 'MISSING' for c in checks))

    def test_unclosed_code_does_not_hide_link_in_next_paragraph(self):
        self.manifest(sad_mode='concise')
        content = '`unclosed\n\n[missing](missing.md)\n\n`'
        self.doc.write_text(CONCISE.replace('## System Context\n\nTBD', '## System Context\n\n' + content))
        result = self.run_cli()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertTrue(any(c['target'] == 'missing.md' and c['status'] == 'MISSING' for c in json.loads(result.stdout)['reference_checks']))

    def test_autolink_inside_multiline_code_does_not_break_span(self):
        self.manifest(sad_mode='concise')
        content = '`example\n<https://example.com>\n[missing](missing.md)\nend`'
        self.doc.write_text(CONCISE.replace('## System Context\n\nTBD', '## System Context\n\n' + content))
        result = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse(any(c['target'] == 'missing.md' for c in json.loads(result.stdout)['reference_checks']))

    def test_unclosed_code_stops_at_new_markdown_blocks(self):
        self.manifest(sad_mode='concise')
        for block in ('# Heading', '- list', '> quote', '1. item', '<!-- comment -->'):
            with self.subTest(block=block):
                content = '`unclosed\n' + block + '\n[missing](missing.md)\n`'
                self.doc.write_text(CONCISE.replace('## System Context\n\nTBD', '## System Context\n\n' + content))
                result = self.run_cli()
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertTrue(any(c['target'] == 'missing.md' and c['status'] == 'MISSING' for c in json.loads(result.stdout)['reference_checks']))

    def test_invalid_fence_and_setext_heading_do_not_hide_links(self):
        self.manifest(sad_mode='concise')
        samples = ('Unmatched ` here\n---\n[missing](missing.md)\n`', '``` invalid ` info\n[missing](missing.md)\n```')
        for content in samples:
            with self.subTest(content=content):
                self.doc.write_text(CONCISE.replace('## System Context\n\nTBD', '## System Context\n\n' + content))
                result = self.run_cli()
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertTrue(any(c['target'] == 'missing.md' and c['status'] == 'MISSING' for c in json.loads(result.stdout)['reference_checks']))

    def test_code_in_link_label_is_not_checked_as_id(self):
        self.manifest(sad_mode='concise')
        (self.base / 'brd.md').write_text(BRD)
        (self.base / 'exists.md').write_text('source')
        sources = self.base / 'sources.json'
        sources.write_text(json.dumps({'BR': 'brd.md'}))
        self.doc.write_text(CONCISE.replace('## System Context\n\nTBD', '## System Context\n\n[`BR-999`](exists.md)'))
        result = self.run_cli(extra=['--sad-id-sources', sources])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        checks = json.loads(result.stdout)['reference_checks']
        self.assertTrue(any(c['target'] == 'exists.md' and c['status'] == 'CHECKED_FILE_EXISTS' for c in checks))
        self.assertFalse(any(c['target'] == 'BR-999' for c in checks))

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
