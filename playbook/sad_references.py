"""Conservative local Markdown link checks for a project-owned SAD."""
import json
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

LINK = re.compile(r'(?<!!)\[[^\]]*\]\(([^)]+)\)')
BARE_URL = re.compile(r'https?://[^\s<>]+', re.I)


def mask_code(text):
    """Hide fenced and inline code while retaining line positions and link targets."""
    lines, fence = [], None
    for line in text.splitlines(keepends=True):
        marker = re.match(r'^ {0,3}(`{3,}|~{3,})([^\r\n]*)', line)
        if marker:
            token, suffix = marker.groups()
            if fence is None and (token[0] != '`' or '`' not in suffix):
                fence = (token[0], len(token))
                lines.append(re.sub(r'[^\r\n]', ' ', line))
                continue
            elif fence is not None and token[0] == fence[0] and len(token) >= fence[1] and not suffix.strip():
                fence = None
                lines.append(re.sub(r'[^\r\n]', ' ', line))
                continue
        if fence is not None:
            lines.append(re.sub(r'[^\r\n]', ' ', line))
        else:
            lines.append(line)
    text = ''.join(lines)
    masked = list(text)
    i = 0
    protected_destinations = {}
    while i < len(text):
        if i in protected_destinations:
            i = protected_destinations[i]
            continue
        if text[i] not in '[`':
            i += 1
            continue
        slash = i - 1
        while slash >= 0 and text[slash] == '\\':
            slash -= 1
        if (i - slash - 1) % 2:
            i += 1
            continue
        if text[i] == '[':
            link = LINK.match(text, i)
            if link:
                # Scan the label normally; destination backticks are literal.
                protected_destinations[link.start(1)] = link.end(1)
                i += 1
                continue
            i += 1
            continue
        end = i
        while end < len(text) and text[end] == '`':
            end += 1
        length = end - i
        closing = end
        matched = False
        while closing < len(text):
            if text[closing] == '\n' and re.match(
                r'\n(?:[ \t\r]*\n| {0,3}(?:#{1,6}[ \t]|>|[-+*][ \t]|[0-9]{1,9}[.)][ \t]|<(?!(?:[A-Za-z][A-Za-z0-9+.-]{1,31}:|[^ >]+@[^ >]+>))(?:!--|[!?/A-Za-z])|(?:=+|-+)[ \t]*(?:\r?\n|$)))',
                text[closing:],
            ):
                # A code span cannot extend into a separate Markdown block.
                break
            if text[closing] != '`':
                closing += 1
                continue
            after = closing
            while after < len(text) and text[after] == '`':
                after += 1
            if after - closing == length:
                for offset in range(i, after):
                    if text[offset] not in '\r\n':
                        masked[offset] = ' '
                i = after
                matched = True
                break
            closing = after
        if not matched:
            i = end
    return ''.join(masked)


def check(text, document, project_root, id_sources=None, id_formats=None, toolkit_root=None):
    root = Path(project_root).resolve(strict=True)
    doc = Path(document).resolve(strict=True)
    if not root.is_dir() or not doc.is_relative_to(root):
        raise ValueError('SAD document must be inside the selected project root')
    findings, checks = [], []
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
    for number, line in enumerate(mask_code(text).splitlines(), 1):
        visible = line
        links = list(LINK.finditer(visible))
        # Link targets and bare URLs are not requirement references; labels may be.
        for link in reversed(links):
            start, end = link.span(1)
            visible = visible[:start] + ' ' * (end - start) + visible[end:]
        urls = list(BARE_URL.finditer(visible))
        for url in reversed(urls):
            visible = visible[:url.start()] + ' ' * len(url.group()) + visible[url.end():]
        for kind, pattern in patterns.items():
            for item in pattern.finditer(visible):
                reference = item.group()
                status = 'CHECKED_ID_EXISTS' if reference in source_sets[kind] else 'MISSING_ID'
                checks.append({'location': f'line {number}', 'target': reference, 'status': status})
                if status == 'MISSING_ID':
                    findings.append({'level': 'ERROR', 'location': f'line {number}', 'message': f'{kind} ID not found in selected source: {reference}'})
        for url in urls:
            checks.append({'location': f'line {number}', 'target': url.group(), 'status': 'NOT_VERIFIED'})
            findings.append({'level': 'WARN', 'location': f'line {number}', 'message': f'External URL not verified: {url.group()}'})
        for match in links:
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
