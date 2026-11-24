"""Validate a full SAD's approved structure and fields without claiming approval."""
import re
from . import sections


def validate(text, contract, mode="full"):
    if mode == "concise":
        contract = dict(contract, sections=contract["concise_sections"], tables={})
    findings = [f for f in sections.validate(text, contract) if f['location'] != 'review']
    def add(level, location, message):
        findings.append({'level': level, 'location': location, 'message': message})
    blocks = {}
    current, fence = None, None
    for number, line in enumerate(text.splitlines(), 1):
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
            current = line[3:].strip()
            blocks.setdefault(current, [])
        elif current is not None:
            blocks[current].append((number, line))

    def cells(line):
        line = line.strip()
        if not line.startswith('|') or not line.endswith('|'):
            return None
        return [x.strip().replace(r'\|', '|') for x in re.split(r'(?<!\\)\|', line[1:-1])]

    def table(section, headers):
        block = blocks.get(section, [])
        content = [(n, line.strip()) for n, line in block if line.strip()]
        if len(content) == 1 and re.fullmatch(r'Not applicable\s*(?:—|–|:|-)\s*\S.*', content[0][1], re.I):
            add('WARN', section, 'Not applicable rationale requires human review')
            return []
        found = [i for i, (_, line) in enumerate(block) if cells(line) == headers]
        if len(found) != 1:
            add('ERROR', section, 'Expected exactly one table with required columns')
            return []
        pos = found[0]
        sep = cells(block[pos + 1][1]) if pos + 1 < len(block) else None
        if sep is None or len(sep) != len(headers) or not all(re.fullmatch(r':?-{3,}:?', x) for x in sep):
            add('ERROR', section, 'Invalid Markdown table separator')
            return []
        result = []
        for number, line in block[pos + 2:]:
            if not line.strip().startswith('|'):
                break
            values = cells(line)
            if values is None or len(values) != len(headers):
                add('ERROR', f'line {number}', f'Expected {len(headers)} cells')
            else:
                if any(not value for value in values):
                    add('ERROR', f'line {number}', 'Every cell needs a value or TBD')
                result.append((number, values))
        if not result:
            add('ERROR', section, 'Table needs a row or TBD placeholder')
        return result

    for section, block in blocks.items():
        for number, line in block:
            if re.match(r'^\s*Not applicable\b', line, re.I) and not re.fullmatch(r'\s*Not applicable\s*(?:—|–|:|-)\s*\S.*', line, re.I):
                add('ERROR', f'line {number}', 'Not applicable needs a reason')
    metadata = table('Document Information', ['Field', 'Value'])
    fields = {}
    for number, (key, value) in metadata:
        if key in fields:
            add('ERROR', f'line {number}', f'Duplicate metadata: {key}')
        fields[key] = value
    for name in contract['metadata']:
        if not fields.get(name):
            add('ERROR', 'Document Information', f'Metadata {name} needs a value or TBD')
    for section, columns in contract['tables'].items():
        for number, row in table(section, columns):
            if section == 'Architecture Decisions & Trade-offs' and row[-1] not in contract['decision_status']:
                add('ERROR', f'line {number}', f'Invalid decision status {row[-1]!r}')
            if section == 'Architecture Decisions & Trade-offs' and row[-1] == 'Accepted':
                add('WARN', f'line {number}', 'Accepted status is self-reported; approval is not verified')
            if any(value != 'TBD' for value in row):
                add('WARN', f'line {number}', 'References and evidence are not verified; review manually')
    add('WARN', 'review', 'Diagrams, trade-offs, security adequacy, tests and approval require human review')
    return findings
