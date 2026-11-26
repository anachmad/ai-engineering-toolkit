"""Validate an optional data model document without accessing a database."""
import re
from . import sections
from .sad_references import mask_code


def visible_markdown(text):
    """Hide HTML comments outside code while preserving line positions."""
    result, comment, fence = [], False, None
    for line in text.splitlines(keepends=True):
        marker = re.match(r'^ {0,3}(`{3,}|~{3,})([^\r\n]*)', line) if not comment else None
        if marker:
            token, suffix = marker.groups()
            if fence is None and (token[0] != '`' or '`' not in suffix):
                fence = (token[0], len(token))
            elif fence and token[0] == fence[0] and len(token) >= fence[1] and not suffix.strip():
                fence = None
            result.append(line.replace('<!--', 'xxxx'))
            continue
        if fence is not None:
            result.append(line.replace('<!--', 'xxxx'))
            continue
        code_mask = mask_code(line)
        out = list(line)
        pos = 0
        while pos < len(line):
            if comment:
                close = line.find('-->', pos)
                end = len(line) if close < 0 else close + 3
                for i in range(pos, end):
                    if line[i] not in '\r\n':
                        out[i] = ' '
                pos = end
                if close >= 0:
                    comment = False
            elif line.startswith('<!--', pos):
                if code_mask[pos:pos + 4] != '<!--':
                    out[pos:pos + 4] = 'xxxx'
                    pos += 4
                else:
                    comment = True
            else:
                pos += 1
        result.append(''.join(out))
    return ''.join(result)


def validate(text, contract):
    visible = visible_markdown(text)
    findings = [f for f in sections.validate(visible, contract) if f['location'] != 'review']
    findings.extend(sections.visible_content_findings(visible, contract))
    def add(level, location, message):
        findings.append({'level': level, 'location': location, 'message': message})
    def normalize_na(value):
        value = re.sub(r'^\s*(?:(?:>\s*)|(?:[-+*]\s+)|(?:\d+[.)]\s+))*', '', value)
        value = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', value)
        return re.sub(r'\*\*|__|\*|_|`', '', value).strip()

    blocks, current, fence = {}, None, None
    for number, line in enumerate(visible.splitlines(), 1):
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
        if re.match(r'^ {0,3}(?:<(?:\?|!\[CDATA\[|![A-Z])|</?(?!(?:[A-Za-z][A-Za-z0-9+.-]*:|[^ >]+@[^ >]+>))[A-Za-z][A-Za-z0-9-]*(?:\s|/?>|$))', line, re.I):
            add('ERROR', f'line {number}', 'Raw HTML blocks are unsupported; use Markdown outside code fences')
        if line.startswith('## '):
            current = line[3:].strip()
            blocks.setdefault(current, [])
        elif current is not None:
            blocks[current].append((number, line))
        normalized = normalize_na(line)
        if re.match(r'^Not applicable\b', normalized, re.I) and not re.fullmatch(r'Not applicable\s*(?:—|–|:|-)\s*\S.*', normalized, re.I):
            add('ERROR', f'line {number}', 'Not applicable requires a reason')

    def cells(line):
        value = line.strip()
        if not value.startswith('|') or not value.endswith('|'):
            return None
        return [x.strip().replace(r'\|', '|') for x in re.split(r'(?<!\\)\|', value[1:-1])]

    def table(name, columns, optional_na=True):
        block = blocks.get(name, [])
        contents = [(n, line.strip()) for n, line in block if line.strip()]
        if optional_na and len(contents) == 1 and re.fullmatch(r'Not applicable\s*(?:—|–|:|-)\s*\S.*', normalize_na(contents[0][1]), re.I):
            add('WARN', name, 'Not applicable rationale requires human review')
            return None
        headers = [i for i, (_, line) in enumerate(block) if cells(line) == columns]
        if len(headers) != 1:
            add('ERROR', name, 'Expected exactly one table with required columns')
            return None
        start = headers[0]
        sep = cells(block[start + 1][1]) if start + 1 < len(block) else None
        if sep is None or len(sep) != len(columns) or not all(re.fullmatch(r':?-{3,}:?', v) for v in sep):
            add('ERROR', name, 'Invalid Markdown table separator')
            return None
        rows = []
        for number, line in block[start + 2:]:
            if not line.strip().startswith('|'):
                break
            value = cells(line)
            if value is None or len(value) != len(columns):
                add('ERROR', f'line {number}', f'Expected {len(columns)} table cells')
                continue
            if any(not item for item in value):
                add('ERROR', f'line {number}', 'Every cell needs a value or TBD')
            for item in value:
                normalized = normalize_na(item)
                if re.match(r'^Not applicable\b', normalized, re.I):
                    if not re.fullmatch(r'Not applicable\s*(?:—|–|:|-)\s*\S.*', normalized, re.I):
                        add('ERROR', f'line {number}', 'Not applicable requires a reason')
                    else:
                        add('WARN', f'line {number}', 'Not applicable rationale requires human review')
            rows.append((number, value))
        if not rows:
            add('ERROR', name, 'Table needs a row or TBD placeholder')
        return rows

    fields = {}
    for number, (key, value) in table('Metadata', ['Field', 'Value'], False) or []:
        if key in fields:
            add('ERROR', f'line {number}', f'Duplicate metadata field: {key}')
        fields[key] = value
    for key in contract['metadata']:
        if not fields.get(key):
            add('ERROR', 'Metadata', f'Metadata {key} needs a value or TBD')
    if fields.get('Status') and fields['Status'] not in contract['document_status']:
        add('ERROR', 'Metadata', f'Invalid document status: {fields["Status"]!r}')
    tables = {name: table(name, columns) for name, columns in contract['tables'].items()}
    entities, folded, catalog_incomplete = set(), {}, tables['Entity Catalog'] is None
    for number, row in tables['Entity Catalog'] or []:
        entity = row[0]
        if entity == 'TBD':
            catalog_incomplete = True
            continue
        if entity in entities:
            add('ERROR', f'line {number}', f'Duplicate entity: {entity}')
        if entity.casefold() in folded and folded[entity.casefold()] != entity:
            add('WARN', f'line {number}', f'Entity differs only by case: {folded[entity.casefold()]} / {entity}; review naming')
        folded[entity.casefold()] = entity
        entities.add(entity)

    def entity_ref(value, loc):
        if value == 'external:':
            add('ERROR', loc, 'External entity reference requires a source identifier')
        elif value == 'TBD' or value.startswith('external:'):
            add('WARN', loc, f'Entity reference {value!r} is not verified')
        elif value not in entities:
            add('WARN' if catalog_incomplete else 'ERROR', loc, f'Entity not found in local catalog: {value}')
    for number, row in tables['Relationships & Cardinality'] or []:
        if all(value == 'TBD' for value in row):
            continue
        entity_ref(row[0], f'line {number}')
        entity_ref(row[2], f'line {number}')
    fields_seen, fields_folded = set(), {}
    for number, row in tables['Field Dictionary'] or []:
        if all(value == 'TBD' for value in row):
            continue
        entity, field, _, _, required, sensitivity, source = row
        loc = f'line {number}'
        entity_ref(entity, loc)
        if required and required not in contract['required_values']:
            add('ERROR', loc, f'Invalid Required value: {required!r}')
        if entity != 'TBD' and field != 'TBD':
            key = (entity, field)
            if key in fields_seen:
                add('ERROR', loc, f'Duplicate entity/field: {entity} / {field}')
            folded_key = (entity.casefold(), field.casefold())
            if folded_key in fields_folded and fields_folded[folded_key] != key:
                add('WARN', loc, 'Entity/field differs only by case; review naming')
            fields_folded[folded_key] = key
            fields_seen.add(key)
        add('WARN', loc, f'Sensitivity {sensitivity!r} and source {source!r} require review; not verified')
    add('WARN', 'review', 'Database, source authority, privacy controls, migration, semantic review and approval are not verified')
    return findings
