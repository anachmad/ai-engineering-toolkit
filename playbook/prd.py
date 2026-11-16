"""Deterministic local PRD checks; cross-document evidence remains unverified."""
import re

from . import sections
from .id_formats import matches as matches_id


def validate(text, contract, id_formats=None):
    findings = sections.validate(text, contract)
    findings = [f for f in findings if f['location'] != 'review']

    def add(level, location, message):
        findings.append({'level': level, 'location': location, 'message': message})

    lines = text.splitlines()
    section_lines = []
    in_section = False
    fence = None
    for i, line in enumerate(lines):
        marker = re.match(r'^\s{0,3}(`{3,}|~{3,})', line)
        if marker:
            token = marker.group(1)
            if fence is None:
                fence = (token[0], len(token))
            elif token[0] == fence[0] and len(token) >= fence[1]:
                fence = None
            continue
        if fence is not None:
            continue
        if line.startswith('## '):
            in_section = line[3:].strip() == 'Product Requirements'
            continue
        if in_section:
            section_lines.append((i + 1, line))

    def cells(line):
        # Escaped pipes are literal content, not table delimiters.
        value = line.strip()
        if not value.startswith('|') or not value.endswith('|'):
            return None
        return [x.strip().replace(r'\|', '|') for x in re.split(r'(?<!\\)\|', value[1:-1])]

    config = contract['requirement_table']
    matches = [i for i, (_, line) in enumerate(section_lines) if cells(line) == config['columns']]
    if len(matches) != 1:
        add('ERROR', 'Product Requirements', 'Expected exactly one table with the seven required columns')
    else:
        start = matches[0]
        if start + 1 >= len(section_lines):
            add('ERROR', 'Product Requirements', 'Missing Markdown table separator')
        else:
            sep = cells(section_lines[start + 1][1])
            if sep is None or len(sep) != len(config['columns']) or not all(re.fullmatch(r':?-{3,}:?', c) for c in sep):
                add('ERROR', f'line {section_lines[start + 1][0]}', 'Invalid Markdown table separator')
            rows = []
            for number, line in section_lines[start + 2:]:
                if not line.strip().startswith('|'):
                    break
                rows.append((number, cells(line)))
            if not rows:
                add('ERROR', 'Product Requirements', 'Table requires at least one requirement or TBD placeholder row')
            seen = set()
            for number, row in rows:
                location = f'line {number}'
                if row is None or len(row) != len(config['columns']):
                    add('ERROR', location, 'Expected seven table cells with leading and trailing pipes')
                    continue
                if any(not value for value in row):
                    add('ERROR', location, 'Every requirement field needs a value or TBD')
                if all(value == 'TBD' for value in row):
                    continue
                identifier, _, source, priority, _, _, status = row
                if not matches_id(identifier, 'PR', id_formats, config['id_pattern']):
                    add('ERROR', location, f'Invalid requirement ID {identifier!r} for the selected format')
                elif identifier in seen:
                    add('ERROR', location, f'Duplicate requirement ID: {identifier}')
                else:
                    seen.add(identifier)
                if priority and priority not in config['priority']:
                    add('ERROR', location, f'Invalid priority {priority!r}; use ' + ', '.join(config['priority']))
                if status and status not in config['status']:
                    add('ERROR', location, f'Invalid status {status!r}; use ' + ', '.join(config['status']))
                if source and source != 'TBD':
                    add('WARN', location, f'Source {source!r} is not verified; review its location and authority')
                if status == 'Approved':
                    add('WARN', location, 'Approved status is self-reported; human approval evidence is not verified')
    add('WARN', 'review', 'Semantic review, cross-document references and human approval are not verified')
    return findings
