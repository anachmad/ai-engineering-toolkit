"""Validate an API document; never fetch or execute its contract."""
import datetime
import re
from pathlib import Path
from urllib.parse import urlsplit

from . import sections
from .data_model import visible_markdown


def validate(text, contract, document, project_root=None):
    visible = visible_markdown(text)
    findings = [f for f in sections.validate(visible, contract) if f['location'] != 'review']
    findings.extend(sections.visible_content_findings(visible, contract))
    blocks, current, fence = {}, None, None

    def add(level, location, message):
        findings.append({'level': level, 'location': location, 'message': message})

    def normalize(value):
        value = re.sub(r'^\s*(?:(?:>\s*)|(?:[-+*]\s+)|(?:\d+[.)]\s+))*', '', value)
        value = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', value)
        return re.sub(r'\*\*|__|\*|_|`', '', value).strip()

    def check_na(value, location):
        value = normalize(value)
        if re.match(r'^Not applicable\b', value, re.I):
            if not re.fullmatch(r'Not applicable\s*(?:—|–|:|-)\s*\S.*', value, re.I):
                add('ERROR', location, 'Not applicable requires a reason')
            else:
                add('WARN', location, 'Not applicable rationale requires human review')
            return True
        return False

    for number, line in enumerate(visible.splitlines(), 1):
        marker = re.match(r'^\s{0,3}(`{3,}|~{3,})(.*)$', line)
        if marker:
            token = marker.group(1)
            if fence is None:
                fence = (token[0], len(token))
            elif token[0] == fence[0] and len(token) >= fence[1] and not marker.group(2).strip():
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
            if not line.strip().startswith('|'):
                check_na(line, f'line {number}')

    def cells(line):
        if line.expandtabs(4).startswith('    '):
            return None
        line = line.strip()
        if not line.startswith('|') or not line.endswith('|'):
            return None
        return [x.strip().replace(r'\|', '|') for x in re.split(r'(?<!\\)\|', line[1:-1])]

    def table(name, columns, allow_na=True):
        block = blocks.get(name, [])
        contents = [(n, line.strip()) for n, line in block if line.strip()]
        if allow_na and len(contents) == 1 and re.fullmatch(r'Not applicable\s*(?:—|–|:|-)\s*\S.*', normalize(contents[0][1]), re.I):
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
            row = cells(line)
            if row is None or len(row) != len(columns):
                add('ERROR', f'line {number}', f'Expected {len(columns)} table cells')
                continue
            if any(not normalize(value) for value in row):
                add('ERROR', f'line {number}', 'Every cell needs a value or TBD')
            for value in row:
                check_na(value, f'line {number}')
            rows.append((number, row))
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
    status = fields.get('Status')
    if status and status not in contract['document_status']:
        add('ERROR', 'Metadata', f'Invalid document status: {status!r}')
    date = fields.get('Date')
    if date and date != 'TBD':
        try:
            if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', date):
                raise ValueError()
            datetime.date.fromisoformat(date)
        except ValueError:
            add('ERROR', 'Metadata', 'Date must be a real YYYY-MM-DD date or TBD')
    endpoint = blocks.get('Endpoint Catalog', [])
    markers = [line.strip() for _, line in endpoint if line.strip() == contract['contract_reference_marker']]
    if markers:
        if len(markers) != 1 or len([line for _, line in endpoint if line.strip()]) != 1:
            add('ERROR', 'Endpoint Catalog', 'Use only one contract reference marker or the required table')
        for key in ('Contract source', 'Contract version'):
            if normalize(fields.get(key, '')).lower().startswith('not applicable'):
                add('ERROR', 'Endpoint Catalog', f'{key} cannot be Not applicable when referencing a contract')
    else:
        table('Endpoint Catalog', contract['tables']['Endpoint Catalog'])
    table('Testing & References', contract['tables']['Testing & References'])

    source = fields.get('Contract source', '')
    result = {'status': 'NOT_VERIFIED', 'source': source or None, 'scope': 'File existence only; validity, authority, runtime and approval are not verified'}
    if source and source != 'TBD' and not normalize(source).lower().startswith('not applicable'):
        match = re.fullmatch(r'\[[^\]]+\]\(([^)]+)\)', source)
        target = match.group(1) if match else source
        complex_link = (source.startswith('[') and not match) or (match and (re.search(r'\s+["\']', target) or '(' in target))
        if target.startswith('<') and target.endswith('>'):
            target = target[1:-1]
        try:
            parsed = urlsplit(target)
        except ValueError:
            parsed = None
        if complex_link or parsed is None or parsed.scheme or parsed.netloc or parsed.query or parsed.fragment or not project_root:
            add('WARN', 'Contract source', 'External, complex or unselected contract source not verified')
        else:
            try:
                root = Path(project_root).resolve(strict=True)
                if not root.is_dir():
                    raise ValueError('Project root must be a directory')
                doc = Path(document).resolve(strict=True)
                if not doc.is_relative_to(root):
                    raise ValueError('API document must be inside project root')
                candidate = (doc.parent / target).resolve()
                if not candidate.is_relative_to(root):
                    raise ValueError('Contract source escapes project root')
                if not candidate.is_file():
                    add('ERROR', 'Contract source', 'Selected local contract file does not exist')
                    result['status'] = 'MISSING'
                else:
                    result['status'] = 'CHECKED_FILE_EXISTS'
            except (OSError, RuntimeError, ValueError) as exc:
                add('ERROR', 'Contract source', f'Cannot safely check contract source: {exc}')
                result['status'] = 'INVALID_PATH'
    add('WARN', 'review', 'Contract validity, runtime, security, semantic review and human approval are not verified')
    return findings, result
