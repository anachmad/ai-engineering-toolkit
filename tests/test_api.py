import json
import tempfile
import unittest
from pathlib import Path

from playbook.artifacts import validate_artifact

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = (ROOT / 'skills/software-engineering-playbook/templates/api-template.md').read_text()


class ApiValidationTests(unittest.TestCase):
    def check(self, text, source=None, root=True):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            doc = base / 'api.md'
            doc.write_text(text)
            if source:
                (base / source).write_text('openapi: 3.0.0\n')
            return validate_artifact(doc, 'api', '1', 'standard', project_root=base if root else None)

    def test_template_is_warn_not_approval(self):
        result = self.check(TEMPLATE)
        self.assertEqual(result['outcome'], 'WARN')
        self.assertEqual(result['human_approval'], 'NOT_VERIFIED')
        self.assertFalse(result['release_authorized'])

    def test_missing_heading_and_invalid_metadata(self):
        for text in (TEMPLATE.replace('## Overview', '## Wrong'), TEMPLATE.replace('| Status | draft |', '| Status | done |'), TEMPLATE.replace('| Date | TBD |', '| Date | 2025-02-30 |'), TEMPLATE.replace('| Owner | TBD |', '| Owner |  |')):
            with self.subTest(text=text):
                self.assertEqual(self.check(text)['outcome'], 'FAIL')

    def test_bad_tables_and_duplicate_fields(self):
        for text in (TEMPLATE.replace('| Operation | Purpose | Version / status | Source |', '| Operation | Source |'), TEMPLATE.replace('| Title | TBD |', '| Title | TBD |\n| Title | Again |'), TEMPLATE.replace('| TBD | TBD | TBD | TBD |', '| TBD | | TBD | TBD |', 1)):
            with self.subTest(text=text):
                self.assertEqual(self.check(text)['outcome'], 'FAIL')

    def test_reference_file_exists_but_not_verified(self):
        text = TEMPLATE.replace('| Contract source | TBD |', '| Contract source | openapi.yaml |').replace('| Contract version | TBD |', '| Contract version | 1 |')
        text = text.replace('| Operation | Purpose | Version / status | Source |\n| --- | --- | --- | --- |\n| TBD | TBD | TBD | TBD |', 'Contract reference: see Metadata')
        result = self.check(text, 'openapi.yaml')
        self.assertEqual(result['outcome'], 'WARN')
        self.assertEqual(result['api_contract_source_check']['status'], 'CHECKED_FILE_EXISTS')
        self.assertEqual(self.check(text)['api_contract_source_check']['status'], 'MISSING')
        self.assertEqual(self.check(text, root=False)['api_contract_source_check']['status'], 'NOT_VERIFIED')

    def test_external_or_escaping_source(self):
        text = TEMPLATE.replace('| Contract source | TBD |', '| Contract source | https://example.com/openapi.yaml |')
        self.assertEqual(self.check(text)['api_contract_source_check']['status'], 'NOT_VERIFIED')
        text = text.replace('https://example.com/openapi.yaml', '../outside.yaml')
        self.assertEqual(self.check(text)['outcome'], 'FAIL')
        text = text.replace('../outside.yaml', 'http://[')
        self.assertEqual(self.check(text)['api_contract_source_check']['status'], 'NOT_VERIFIED')

    def test_hidden_content_cannot_supply_required_table(self):
        table = '| Operation | Purpose | Version / status | Source |\n| --- | --- | --- | --- |\n| TBD | TBD | TBD | TBD |'
        for replacement in ('<!--\n' + table + '\n-->', '<div>\n' + table + '\n</div>', '```\n' + table + '\n```'):
            self.assertEqual(self.check(TEMPLATE.replace(table, replacement))['outcome'], 'FAIL')

    def test_not_applicable_requires_reason(self):
        self.assertEqual(self.check(TEMPLATE.replace('| Contract source | TBD |', '| Contract source | **Not applicable** |'))['outcome'], 'FAIL')
        self.assertEqual(self.check(TEMPLATE.replace('| Contract source | TBD |', '| Contract source | Not applicable — no API contract |'))['outcome'], 'WARN')

    def test_contract_marker_cannot_hide_malformed_table(self):
        header = '| Operation | Purpose | Version / status | Source |'
        text = TEMPLATE.replace(header, 'Contract reference: see Metadata\n' + header)
        text = text.replace('| TBD | TBD | TBD | TBD |', '| | | | |', 1)
        self.assertEqual(self.check(text)['outcome'], 'FAIL')

    def test_markdown_autolink_is_unverified_not_missing(self):
        text = TEMPLATE.replace('| Contract source | TBD |', '| Contract source | <https://example.com/openapi.yaml> |')
        result = self.check(text)
        self.assertEqual(result['outcome'], 'WARN')
        self.assertEqual(result['api_contract_source_check']['status'], 'NOT_VERIFIED')

    def test_formatting_only_metadata_is_empty(self):
        text = TEMPLATE.replace('| Owner | TBD |', '| Owner | ** ** |')
        self.assertEqual(self.check(text)['outcome'], 'FAIL')

    def test_fence_with_suffix_does_not_close_fence(self):
        table = '| Operation | Purpose | Version / status | Source |\n| --- | --- | --- | --- |\n| TBD | TBD | TBD | TBD |'
        text = TEMPLATE.replace(table, '```\n``` fake\n' + table + '\n``` fake\n```')
        self.assertEqual(self.check(text)['outcome'], 'FAIL')

    def test_indented_code_block_is_not_a_table(self):
        table = '| Operation | Purpose | Version / status | Source |\n| --- | --- | --- | --- |\n| TBD | TBD | TBD | TBD |'
        for indent in ('    ', ' \t'):
            with self.subTest(indent=indent):
                text = TEMPLATE.replace(table, '\n'.join(indent + line for line in table.splitlines()))
                self.assertEqual(self.check(text)['outcome'], 'FAIL')

    def test_complex_markdown_link_is_not_mistaken_for_missing_file(self):
        for source in ('[OpenAPI](openapi.yaml "Contract")', '[OpenAPI](api(v1).yaml)'):
            with self.subTest(source=source):
                text = TEMPLATE.replace('| Contract source | TBD |', '| Contract source | ' + source + ' |')
                result = self.check(text)
                self.assertEqual(result['outcome'], 'WARN')
                self.assertEqual(result['api_contract_source_check']['status'], 'NOT_VERIFIED')


if __name__ == '__main__':
    unittest.main()
