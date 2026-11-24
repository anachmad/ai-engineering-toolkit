"""Extract business requirement IDs from the explicitly selected BRD table."""
import re

from .id_formats import matches


def business_ids(text, contract, formats):
    lines = text.splitlines()
    section, fence = False, None
    rows = []
    for number, line in enumerate(lines, 1):
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
            section = line[3:].strip() == 'Business Requirements'
        elif section:
            rows.append((number, line))

    def cells(line):
        value = line.strip()
        if not value.startswith('|') or not value.endswith('|'):
            return None
        return [x.strip() for x in re.split(r'(?<!\\)\|', value[1:-1])]

    expected = contract['tables']['Business Requirements']
    headers = [i for i, (_, line) in enumerate(rows) if cells(line) == expected]
    if len(headers) != 1:
        raise ValueError('BRD must contain exactly one Business Requirements table with canonical columns')
    start = headers[0]
    if start + 1 >= len(rows):
        raise ValueError('BRD Business Requirements table separator missing')
    sep = cells(rows[start + 1][1])
    if sep is None or len(sep) != len(expected) or not all(re.fullmatch(r':?-{3,}:?', c) for c in sep):
        raise ValueError('BRD Business Requirements table separator invalid')
    identifiers = set()
    count = 0
    for number, line in rows[start + 2:]:
        if not line.strip().startswith('|'):
            break
        count += 1
        row = cells(line)
        if row is None or len(row) != len(expected) or any(not item for item in row):
            raise ValueError(f'Malformed BRD requirement row at line {number}')
        if all(value == 'TBD' for value in row):
            continue
        identifier = row[0]
        if not matches(identifier, 'BR', formats, r'BR-[0-9]{3,}'):
            raise ValueError(f'Invalid BRD requirement ID at line {number}: {identifier}')
        if identifier in identifiers:
            raise ValueError(f'Duplicate BRD requirement ID: {identifier}')
        identifiers.add(identifier)
    if not count:
        raise ValueError('BRD Business Requirements table needs a row or TBD placeholder')
    return identifiers


def product_ids(text, contract, formats):
    """Read identifiers only from the canonical PRD requirement table."""
    expected = contract['requirement_table']['columns']
    lines = text.splitlines()
    block, section, fence = [], False, None
    for number, line in enumerate(lines, 1):
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
            section = line[3:].strip() == 'Product Requirements'
        elif section:
            block.append((number, line))
    def cells(line):
        value = line.strip()
        if not value.startswith('|') or not value.endswith('|'):
            return None
        return [x.strip() for x in re.split(r'(?<!\\)\|', value[1:-1])]
    headers = [i for i, (_, line) in enumerate(block) if cells(line) == expected]
    if len(headers) != 1:
        raise ValueError('PRD must contain exactly one canonical Product Requirements table')
    pos = headers[0]
    sep = cells(block[pos + 1][1]) if pos + 1 < len(block) else None
    if sep is None or len(sep) != len(expected) or not all(re.fullmatch(r':?-{3,}:?', c) for c in sep):
        raise ValueError('PRD Product Requirements table separator invalid')
    ids = set()
    count = 0
    for number, line in block[pos + 2:]:
        if not line.strip().startswith('|'):
            break
        count += 1
        row = cells(line)
        if row is None or len(row) != len(expected) or any(not x for x in row):
            raise ValueError(f'Malformed PRD requirement row at line {number}')
        if all(x == 'TBD' for x in row):
            continue
        identifier = row[0]
        if not matches(identifier, 'PR', formats, r'PR-[0-9]{3,}'):
            raise ValueError(f'Invalid PRD requirement ID at line {number}: {identifier}')
        if identifier in ids:
            raise ValueError(f'Duplicate PRD requirement ID: {identifier}')
        ids.add(identifier)
    if not count:
        raise ValueError('PRD Product Requirements table needs a row or TBD placeholder')
    return ids
