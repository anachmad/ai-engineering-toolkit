"""Deterministic BRD format and reference checks; not semantic approval."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ID = re.compile(r'^(BO|BR|KPI)-\d{3,}$')


def validate(text, contract):
    findings = []

    def add(level, location, message):
        findings.append({'level': level, 'location': location, 'message': message})

    lines = text.splitlines()
    sections = []
    fenced = False
    for index, line in enumerate(lines):
        if re.match(r'^\s*(```|~~~)', line):
            fenced = not fenced
        elif not fenced and line.startswith('## '):
            sections.append((line[3:].strip(), index))
    names = [name for name, _ in sections]
    if names != contract['sections']:
        add('ERROR', 'headings', 'Level-two headings must match the 18 required names and order in standards/brd-v1.json; found: ' + ', '.join(names))
    blocks = {}
    for i, (name, start) in enumerate(sections):
        end = sections[i + 1][1] if i + 1 < len(sections) else len(lines)
        if name in blocks:
            add('ERROR', f'line {start + 1}', f'Duplicate section: {name}')
        else:
            blocks[name] = (start, lines[start + 1:end])
        if not any(line.strip() and not line.lstrip().startswith('#') for line in lines[start + 1:end]):
            add('ERROR', f'line {start + 1}', f'{name} needs content or TBD')
    for section, required in {
        'Scope': ['In scope', 'Out of scope'],
        'Assumptions, Constraints & Dependencies': ['Assumptions', 'Constraints', 'Dependencies'],
        'Open Questions & Decisions': ['Open questions', 'Decisions'],
    }.items():
        if section in blocks:
            subheadings = [line[4:].strip() for line in blocks[section][1] if line.startswith('### ')]
            for heading in required:
                if heading not in subheadings:
                    add('ERROR', section, f'Missing required subheading: {heading}')
                else:
                    block = blocks[section][1]
                    pos = block.index('### ' + heading)
                    body = []
                    for line in block[pos + 1:]:
                        if line.startswith('### '):
                            break
                        body.append(line)
                    if not any(line.strip() for line in body):
                        add('ERROR', section, f'Subheading {heading} needs content or TBD')
    for i, line in enumerate(lines):
        if re.search(r'\bTBD\b', line, re.I):
            add('WARN', f'line {i + 1}', 'Resolve or explicitly manage TBD before completion')

    def table(section, headers):
        if section not in blocks:
            return []
        start, block = blocks[section]
        for i, line in enumerate(block):
            cells = [v.strip() for v in line.strip().strip('|').split('|')]
            if line.strip().startswith('|') and cells == headers:
                if i + 1 >= len(block) or not re.fullmatch(r'\s*\|?(?:\s*:?-{3,}:?\s*\|)+\s*', block[i + 1]):
                    add('ERROR', f'line {start + i + 2}', 'Missing Markdown table separator')
                    return []
                rows = []
                for j in range(i + 2, len(block)):
                    if not block[j].strip().startswith('|'):
                        break
                    values = [v.strip() for v in block[j].strip().strip('|').split('|')]
                    loc = f'line {start + j + 2}'
                    if len(values) != len(headers):
                        add('ERROR', loc, f'Expected {len(headers)} table cells')
                    else:
                        if any(not value for value in values):
                            add('ERROR', loc, 'Fill every table cell or use TBD')
                        rows.append((loc, values))
                if not rows:
                    add('ERROR', section, 'Table needs at least one row or a TBD placeholder row')
                return rows
        add('ERROR', section, 'Missing required table with columns: ' + ' | '.join(headers))
        return []

    metadata = table('Document Information', ['Field', 'Value'])
    seen_metadata = set()
    for loc, (key, value) in metadata:
        if key in seen_metadata:
            add('ERROR', loc, f'Duplicate metadata field: {key}')
        seen_metadata.add(key)
        if not value:
            add('ERROR', loc, f'Metadata {key} needs a value or TBD')
    for key in contract['metadata']:
        if key not in seen_metadata:
            add('ERROR', 'Document Information', f'Missing metadata field: {key}')
    tables = {name: table(name, headers) for name, headers in contract['tables'].items()}
    definitions = {'BO': {}, 'BR': {}, 'KPI': {}}
    objectives = {}
    for section, prefix in [('Business Objectives', 'BO'), ('Business Requirements', 'BR'), ('Success Metrics / KPI', 'KPI')]:
        for loc, row in tables[section]:
            identifier = row[0]
            if all(v.upper() == 'TBD' for v in row):
                continue
            if not ID.fullmatch(identifier) or not identifier.startswith(prefix + '-'):
                add('ERROR', loc, f'Expected {prefix}-001 style ID, got {identifier!r}')
                continue
            if identifier in definitions[prefix]:
                add('ERROR', loc, f'Duplicate ID: {identifier}')
            definitions[prefix][identifier] = loc
            if not row[1] or row[1].upper() == 'TBD':
                add('ERROR', loc, f'{identifier} needs a ' + ('measurement definition' if prefix == 'KPI' else 'description'))
            if prefix in ('BR', 'KPI'):
                objectives[identifier] = (loc, row[2])
    def refs(loc, value, prefix, allow_tbd=False):
        if value.upper() == 'TBD' and allow_tbd:
            return []
        parts = [v.strip() for v in value.split(',')]
        for item in parts:
            if not ID.fullmatch(item) or not item.startswith(prefix + '-') or item not in definitions[prefix]:
                add('ERROR', loc, f'Unknown or invalid {prefix} reference: {item or "(empty)"}')
        return parts
    for identifier, (loc, value) in objectives.items():
        refs(loc, value, 'BO')
    traced = set()
    for loc, row in tables['Traceability']:
        if all(v.upper() == 'TBD' for v in row):
            continue
        bos = refs(loc, row[0], 'BO')
        brs = refs(loc, row[1], 'BR')
        kpis = refs(loc, row[2], 'KPI', allow_tbd=True)
        for identifier in brs + kpis:
            if identifier in objectives and not set(bos).intersection(x.strip() for x in objectives[identifier][1].split(',')):
                add('ERROR', loc, f'{identifier} does not reference the listed objective')
        traced.update(brs)
    for identifier in definitions['BR']:
        if identifier not in traced:
            add('ERROR', definitions['BR'][identifier], f'{identifier} is missing from Traceability')
    add('WARN', 'review', 'Human review required for factual evidence, business meaning, nontechnical scope and approval')
    return findings


def run(path):
    contract = json.loads((ROOT / 'standards/brd-v1.json').read_text(encoding='utf-8'))
    findings = validate(Path(path).read_text(encoding='utf-8'), contract)
    for item in findings:
        print(f"{item['level']} {item['location']}: {item['message']}")
    errors = sum(item['level'] == 'ERROR' for item in findings)
    print(f"{errors} error(s), {len(findings) - errors} warning(s); no approval implied")
    return 1 if errors else 0
