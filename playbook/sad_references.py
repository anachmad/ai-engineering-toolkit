"""Conservative local Markdown link checks for a project-owned SAD."""
import json
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

LINK = re.compile(r'(?<!!)\[[^\]]*\]\(([^)]+)\)')


def check(text, document, project_root, id_sources=None, id_formats=None, toolkit_root=None):
    root = Path(project_root).resolve(strict=True)
    doc = Path(document).resolve(strict=True)
    if not root.is_dir() or not doc.is_relative_to(root):
        raise ValueError('SAD document must be inside the selected project root')
    findings, checks, fence = [], [], None
    source_sets = {}
    patterns = {}
    if id_sources:
        from .traceability import business_ids, product_ids
        config = json.loads(Path(id_sources).read_text(encoding='utf-8'))
        if not isinstance(config, dict) or not config or not set(config) <= {'BR', 'PR'} or not all(isinstance(v, str) and v for v in config.values()):
            raise ValueError('SAD ID sources must map BR or PR to project-relative paths')
        for kind, source in config.items():
            if Path(source).is_absolute():
                raise ValueError('SAD ID source paths must be project-relative')
            path = (root / source).resolve()
            if not path.is_relative_to(root) or not path.is_file():
                raise ValueError(f'SAD ID source missing or outside project root: {source}')
            version = 'brd-v1' if kind == 'BR' else 'prd-v3'
            contract = json.loads((Path(toolkit_root) / 'standards' / (version + '.json')).read_text(encoding='utf-8'))
            source_text = path.read_text(encoding='utf-8')
            source_sets[kind] = business_ids(source_text, contract, id_formats) if kind == 'BR' else product_ids(source_text, contract, id_formats)
            rules = (id_formats or {}).get(kind)
            expression = '|'.join(re.escape(rule['prefix']) + r'[0-9]{' + str(rule['digits']) + '}' for rule in rules) if rules else kind + r'-[0-9]{3,}'
            patterns[kind] = re.compile(r'(?<![A-Za-z0-9-])(?:' + expression + r')(?![A-Za-z0-9-])')
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
        for kind, pattern in patterns.items():
            for item in pattern.finditer(line):
                reference = item.group()
                status = 'CHECKED_ID_EXISTS' if reference in source_sets[kind] else 'MISSING_ID'
                checks.append({'location': f'line {number}', 'target': reference, 'status': status})
                if status == 'MISSING_ID':
                    findings.append({'level': 'ERROR', 'location': f'line {number}', 'message': f'{kind} ID not found in selected source: {reference}'})
        for match in LINK.finditer(line):
            target = match.group(1).strip()
            location = f'line {number}'
            parts = urlsplit(target)
            if parts.scheme or parts.netloc or not parts.path or parts.query or ' ' in target or parts.path.startswith('/'):
                checks.append({'location': location, 'target': target, 'status': 'NOT_VERIFIED'})
                findings.append({'level': 'WARN', 'location': location, 'message': f'Reference not verified: {target}'})
                continue
            candidate = (doc.parent / unquote(parts.path)).resolve()
            if not candidate.is_relative_to(root):
                checks.append({'location': location, 'target': target, 'status': 'OUTSIDE_PROJECT'})
                findings.append({'level': 'ERROR', 'location': location, 'message': f'Reference escapes project root: {target}'})
            elif not candidate.is_file():
                checks.append({'location': location, 'target': target, 'status': 'MISSING'})
                findings.append({'level': 'ERROR', 'location': location, 'message': f'Local file not found: {target}'})
            else:
                checks.append({'location': location, 'target': target, 'status': 'CHECKED_FILE_EXISTS'})
                if parts.fragment:
                    checks.append({'location': location, 'target': target, 'status': 'ANCHOR_NOT_VERIFIED'})
                    findings.append({'level': 'WARN', 'location': location, 'message': f'Anchor not verified: {target}'})
    findings.append({'level': 'WARN', 'location': 'review', 'message': 'Only basic Markdown inline links and explicitly selected BR/PR IDs are checked; other references and source authority remain unverified'})
    return findings, checks
