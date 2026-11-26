"""Validate a single ADR without claiming verified approval."""
from datetime import date
import re
from . import sections
from .id_formats import matches


def validate(text, contract, id_formats=None):
    findings = [f for f in sections.validate(text, contract) if f['location'] != 'review']
    def add(level, location, message):
        findings.append({'level': level, 'location': location, 'message': message})
    findings.extend(sections.visible_content_findings(text, contract))

    def normalize_na(value):
        value = re.sub(r'^\s*(?:(?:>\s*)|(?:[-+*]\s+)|(?:\d+[.)]\s+))*', '', value)
        return re.sub(r'\*\*|__|\*|_', '', value).strip()

    block, in_metadata, fence = [], False, None
    for number, line in enumerate(text.splitlines(), 1):
        marker = re.match(r'^\s{0,3}(`{3,}|~{3,})', line)
        if marker:
            token = marker.group(1)
            if fence is None:
                fence = (token[0], len(token))
            elif token[0] == fence[0] and len(token) >= fence[1]:
                fence = None
            continue
        if fence:
            continue
        if line.startswith('## '):
            in_metadata = line[3:].strip() == 'Metadata & Status'
        elif in_metadata:
            block.append((number, line))
        normalized = normalize_na(line)
        if re.match(r'^Not applicable\b', normalized, re.I) and not re.fullmatch(r'Not applicable\s*(?:—|–|:|-)\s*\S.*', normalized, re.I):
            add('ERROR', f'line {number}', 'Not applicable requires a reason')
    def cells(line):
        value = line.strip()
        if not value.startswith('|') or not value.endswith('|'):
            return None
        return [x.strip().replace(r'\|', '|') for x in re.split(r'(?<!\\)\|', value[1:-1])]
    headers = [i for i, (_, line) in enumerate(block) if cells(line) == ['Field', 'Value']]
    fields = {}
    if len(headers) != 1:
        add('ERROR', 'Metadata & Status', 'Expected exactly one Field / Value table')
    else:
        pos = headers[0]
        sep = cells(block[pos + 1][1]) if pos + 1 < len(block) else None
        if sep is None or len(sep) != 2 or not all(re.fullmatch(r':?-{3,}:?', v) for v in sep):
            add('ERROR', 'Metadata & Status', 'Invalid Markdown table separator')
        else:
            for number, line in block[pos + 2:]:
                if not line.strip().startswith('|'):
                    break
                row = cells(line)
                if row is None or len(row) != 2:
                    add('ERROR', f'line {number}', 'Expected two metadata cells')
                    continue
                key, value = row
                if key in fields:
                    add('ERROR', f'line {number}', f'Duplicate metadata field: {key}')
                fields[key] = value
                normalized = normalize_na(value)
                if re.match(r'^Not applicable\b', normalized, re.I) and (key != 'Supersedes / superseded by' or not re.fullmatch(r'Not applicable\s*(?:—|–|:|-)\s*\S.*', normalized, re.I)):
                    add('ERROR', f'line {number}', f'Not applicable requires a reason and is not allowed for {key}')
    for field in contract['metadata']:
        if not fields.get(field):
            add('ERROR', 'Metadata & Status', f'Metadata {field} requires a value or TBD')
    identifier = fields.get('ID', '')
    if identifier and identifier != 'TBD' and not matches(identifier, 'ADR', id_formats, r'ADR-[0-9]{3,}'):
        add('ERROR', 'Metadata & Status', f'Invalid ADR ID for selected format: {identifier!r}')
    for field, rule in [('Decision status','decision_status'), ('Document status','document_status')]:
        if fields.get(field) and fields[field] not in contract[rule]:
            add('ERROR', 'Metadata & Status', f'Invalid {field}: {fields[field]!r}')
    value = fields.get('Date', '')
    if value and value != 'TBD':
        try:
            if not re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}', value):
                raise ValueError('wrong date format')
            date.fromisoformat(value)
        except ValueError:
            add('ERROR', 'Metadata & Status', 'Date must be a valid YYYY-MM-DD date or TBD')
    add('WARN', 'review', 'Project-wide ID uniqueness, source authority, semantic review and human approval are not verified')
    return findings
