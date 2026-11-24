"""Deterministic SRS checks; source authority and semantic review remain external."""
import re
from . import sections
from .id_formats import matches


def validate(text, contract, id_formats=None, priorities=None, product_ids=None):
    findings = [f for f in sections.validate(text, contract) if f['location'] != 'review']
    def add(level, location, message):
        findings.append({'level': level, 'location': location, 'message': message})
    lines = text.splitlines()
    blocks = {}
    name = None
    fence = None
    for number, line in enumerate(lines, 1):
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
            name = line[3:].strip()
            blocks.setdefault(name, [])
        elif name is not None:
            blocks[name].append((number, line))

    def cells(line):
        line = line.strip()
        if not line.startswith('|') or not line.endswith('|'):
            return None
        return [x.strip().replace(r'\|', '|') for x in re.split(r'(?<!\\)\|', line[1:-1])]

    def table(name, columns):
        block = blocks.get(name, [])
        headers = [i for i, (_, line) in enumerate(block) if cells(line) == columns]
        if len(headers) != 1:
            add('ERROR', name, 'Expected exactly one table with required columns')
            return []
        pos = headers[0]
        sep = cells(block[pos + 1][1]) if pos + 1 < len(block) else None
        if sep is None or len(sep) != len(columns) or not all(re.fullmatch(r':?-{3,}:?', c) for c in sep):
            add('ERROR', name, 'Invalid Markdown table separator')
            return []
        rows = []
        for number, line in block[pos + 2:]:
            if not line.strip().startswith('|'):
                break
            values = cells(line)
            if values is None or len(values) != len(columns):
                add('ERROR', f'line {number}', f'Expected {len(columns)} table cells')
            else:
                rows.append((number, values))
        if not rows:
            add('ERROR', name, 'Table needs a data row or TBD placeholder')
        return rows

    metadata = table('Document Information', ['Field', 'Value'])
    fields = {}
    for number, (key, value) in metadata:
        if key in fields:
            add('ERROR', f'line {number}', f'Duplicate metadata: {key}')
        fields[key] = value
    for key in ('Title', 'Version', 'Status', 'Owner', 'Date'):
        if not fields.get(key):
            add('ERROR', 'Document Information', f'Metadata {key} needs a value or TBD')
    cfg = contract['requirement_table']
    accepted_priorities = priorities if priorities is not None else cfg['priority']
    seen = set()
    for title, kind in [('Functional Requirements', 'FR'), ('Non-Functional Requirements', 'NFR')]:
        for number, row in table(title, cfg['columns']):
            loc = f'line {number}'
            if any(not v for v in row):
                add('ERROR', loc, 'Every field needs a value or TBD')
            if all(v == 'TBD' for v in row):
                continue
            identifier, desc, source, priority, pre, expected, failure, method, status = row
            if not matches(identifier, kind, id_formats, kind + r'-[0-9]{3,}'):
                add('ERROR', loc, f'Invalid {kind} requirement ID {identifier!r}')
            if identifier in seen:
                add('ERROR', loc, f'Duplicate requirement ID: {identifier}')
            seen.add(identifier)
            if priority and priority not in accepted_priorities and priority != 'TBD':
                add('ERROR', loc, f'Invalid priority {priority!r}')
            if method and method not in cfg['verification']:
                add('ERROR', loc, f'Invalid verification method {method!r}')
            if status and status not in cfg['status']:
                add('ERROR', loc, f'Invalid status {status!r}')
            for index, value in enumerate(row):
                if re.match(r'^N/A\b', value, re.I):
                    if index not in (4, 6) or not re.fullmatch(r'N/A\s*(?:—|–|:|-)\s*\S.*', value, re.I):
                        add('ERROR', loc, f'N/A is allowed only with a reason in Preconditions or Failure conditions: {cfg["columns"][index]}')
            if source and source != 'TBD':
                for ref in (x.strip() for x in source.split(',')):
                    if not ref:
                        add('ERROR', loc, 'Empty source reference')
                    elif ref == 'TBD':
                        continue
                    elif product_ids is not None and matches(ref, 'PR', id_formats, r'PR-[0-9]{3,}'):
                        if ref not in product_ids:
                            add('ERROR', loc, f'Product requirement source {ref} not found in selected PRD')
                    elif product_ids is not None and (ref.startswith('PR-') or any(ref.startswith(rule['prefix']) for rule in (id_formats or {}).get('PR', []))):
                        add('ERROR', loc, f'Invalid product requirement source ID {ref!r}')
                    else:
                        add('WARN', loc, f'Source {ref!r} is not verified; review location and authority')
            if status == 'Approved':
                add('WARN', loc, 'Approval is self-reported and not independently verified')
    add('WARN', 'review', 'Semantic review, source authority, test execution and approval are not verified')
    return findings
