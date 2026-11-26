import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = (ROOT / 'skills/software-engineering-playbook/templates/data-model-template.md').read_text()
PLACE5 = '| TBD | TBD | TBD | TBD | TBD |'
PLACE7 = '| TBD | TBD | TBD | TBD | TBD | TBD | TBD |'


def check(text):
    with tempfile.TemporaryDirectory() as tmp:
        doc = Path(tmp) / 'model.md'
        doc.write_text(text)
        cmd = [sys.executable, str(ROOT / 'playbook'), 'validate-artifact', '--artifact', 'data-model', '--standard-version', '1', '--profile', 'standard', '--path', str(doc)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode, json.loads(result.stdout)


def section_row(text, section, original, replacement):
    left, right = text.split('## ' + section, 1)
    return left + '## ' + section + right.replace(original, replacement, 1)


def populated():
    text = section_row(TEMPLATE, 'Entity Catalog', PLACE5, '| Request | A request | Support | request_id | Source |')
    return section_row(text, 'Field Dictionary', PLACE7, '| Request | request_id | Identifier | Text | Yes | TBD | Source |')


class DataModelTests(unittest.TestCase):
    def test_template_and_structure(self):
        code, report = check(TEMPLATE)
        self.assertEqual(code, 0)
        self.assertEqual(report['outcome'], 'WARN')
        self.assertFalse(report['release_authorized'])
        self.assertEqual(check(TEMPLATE.replace('## Scope', '## Wrong'))[0], 1)
        self.assertEqual(check(TEMPLATE.replace('## Scope\n\nTBD', '## Scope\n\n<!-- empty -->'))[0], 1)
        self.assertEqual(check(TEMPLATE.replace('| Owner | TBD |', ''))[0], 1)

    def test_duplicate_and_case_only_names(self):
        text = populated()
        row = '| Request | A request | Support | request_id | Source |'
        self.assertEqual(check(text.replace(row, row + '\n' + row))[0], 1)
        self.assertEqual(check(text.replace('## Scope\n\nTBD', '## Scope\n\nNot applicable'))[0], 1)
        field = '| Request | request_id | Identifier | Text | Yes | TBD | Source |'
        self.assertEqual(check(text.replace(field, field + '\n' + field))[0], 1)
        code, report = check(text.replace(row, row + '\n| request | Another | Support | id | Source |'))
        self.assertEqual(code, 0)
        self.assertTrue(any('differs only by case' in f['message'] for f in report['findings']))

    def test_references_are_not_falsely_verified(self):
        text = populated()
        field = '| Request | request_id | Identifier | Text | Yes | TBD | Source |'
        self.assertEqual(check(text.replace(field, field.replace('Request', 'Missing')))[0], 1)
        code, report = check(text.replace(field, field.replace('Request', 'external:crm.Account')))
        self.assertEqual(code, 0)
        self.assertTrue(any('not verified' in f['message'] for f in report['findings']))
        self.assertEqual(check(text.replace(field, field.replace('Request', 'external:')))[0], 1)
        self.assertEqual(check(text.replace('| Yes |', '| Maybe |'))[0], 1)
        incomplete = section_row(TEMPLATE, 'Field Dictionary', PLACE7, '| Missing | id | Identifier | Text | Yes | TBD | Source |')
        code, report = check(incomplete)
        self.assertEqual(code, 0)
        self.assertTrue(any(f['level'] == 'WARN' and 'not found' in f['message'] for f in report['findings']))

    def test_hidden_tables_and_hidden_cells_are_not_evidence(self):
        header = '| Entity | Description | Domain | Identifier / key | Source |'
        block = header + '\n| --- | --- | --- | --- | --- |\n| TBD | TBD | TBD | TBD | TBD |'
        hidden = TEMPLATE.replace(block, 'Visible prose.\n\n<!--\n' + block + '\n-->')
        self.assertEqual(check(hidden)[0], 1)
        hidden_cell = TEMPLATE.replace(PLACE7, '| TBD | <!-- hidden --> | TBD | TBD | TBD | TBD | TBD |')
        self.assertEqual(check(hidden_cell)[0], 1)

    def test_table_cell_not_applicable_needs_reason(self):
        for value in ('Not applicable', '**Not applicable**'):
            with self.subTest(value=value):
                text = TEMPLATE.replace(PLACE7, '| TBD | ' + value + ' | TBD | TBD | TBD | TBD | TBD |')
                self.assertEqual(check(text)[0], 1)
        valid = TEMPLATE.replace(PLACE7, '| TBD | Not applicable — not recorded | TBD | TBD | TBD | TBD | TBD |')
        self.assertEqual(check(valid)[0], 0)

    def test_hidden_headings_and_unclosed_comments_fail(self):
        hidden_heading = TEMPLATE.replace('## Scope\n\nTBD', '<!--\n## Scope\nTBD\n-->')
        self.assertEqual(check(hidden_heading)[0], 1)
        unclosed = TEMPLATE.replace('## Entity Catalog', '<!--\n## Entity Catalog', 1)
        self.assertEqual(check(unclosed)[0], 1)

    def test_formatted_not_applicable_is_checked_consistently(self):
        for value in ('`Not applicable`', '[Not applicable](https://example.com)'):
            with self.subTest(value=value):
                text = TEMPLATE.replace(PLACE7, '| TBD | ' + value + ' | TBD | TBD | TBD | TBD | TBD |')
                self.assertEqual(check(text)[0], 1)
        block = '| Entity | Description | Domain | Identifier / key | Source |\n| --- | --- | --- | --- | --- |\n| TBD | TBD | TBD | TBD | TBD |'
        valid = TEMPLATE.replace(block, '**Not applicable — no entities**')
        self.assertEqual(check(valid)[0], 0)

    def test_comment_markers_in_code_do_not_hide_document(self):
        for body in ('```html\n<!-- example\n```\nTBD', 'Example `<!--` text.'):
            with self.subTest(body=body):
                self.assertEqual(check(TEMPLATE.replace('## Scope\n\nTBD', '## Scope\n\n' + body))[0], 0)

    def test_raw_html_script_cannot_hide_required_tables(self):
        self.assertEqual(check('<script>\n' + TEMPLATE + '\n</script>')[0], 1)

    def test_raw_html_container_cannot_supply_required_table(self):
        block = '| Entity | Description | Domain | Identifier / key | Source |\n| --- | --- | --- | --- | --- |\n| TBD | TBD | TBD | TBD | TBD |'
        hidden = TEMPLATE.replace(block, '<div>\n' + block + '\n</div>')
        self.assertEqual(check(hidden)[0], 1)

    def test_raw_html_declarations_cannot_hide_document(self):
        for opening, closing in [('<![CDATA[', ']]>'), ('<?hide', '?>'), ('<!DOCTYPE', '>')]:
            with self.subTest(opening=opening):
                self.assertEqual(check(opening + '\n' + TEMPLATE + '\n' + closing)[0], 1)

    def test_optional_document_not_forced_into_scaffold(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run([sys.executable, str(ROOT / 'playbook'), 'init', '--path', tmp, '--profile', 'business-critical', '--name', 'Example'], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse((Path(tmp) / 'docs/02-architecture/data-model.md').exists())


if __name__ == '__main__':
    unittest.main()
