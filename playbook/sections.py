"""Checks for explicitly approved Markdown section structure."""
import re


def validate(text, contract):
    findings = []
    lines = text.splitlines()
    sections = []
    fence = None
    for index, line in enumerate(lines):
        marker = re.match(r'^\s{0,3}(`{3,}|~{3,})', line)
        if marker:
            token = marker.group(1)
            if fence is None:
                fence = (token[0], len(token))
            elif token[0] == fence[0] and len(token) >= fence[1]:
                fence = None
            continue
        if fence is None and line.startswith('## '):
            sections.append((line[3:].strip(), index))
    if [name for name, _ in sections] != contract['sections']:
        findings.append({'level': 'ERROR', 'location': 'headings', 'message': 'Required section names or order do not match the approved contract'})
    for i, (name, start) in enumerate(sections):
        end = sections[i + 1][1] if i + 1 < len(sections) else len(lines)
        if not any(line.strip() and not line.lstrip().startswith('#') for line in lines[start + 1:end]):
            findings.append({'level': 'ERROR', 'location': f'line {start + 1}', 'message': f'{name} needs content or TBD'})
    for i, line in enumerate(lines):
        if re.search(r'\bTBD\b', line, re.I):
            findings.append({'level': 'WARN', 'location': f'line {i + 1}', 'message': 'Resolve or manage TBD before completion'})
    findings.append({'level': 'WARN', 'location': 'review', 'message': 'PRD field, ID, traceability, semantic and approval checks not performed'})
    return findings
