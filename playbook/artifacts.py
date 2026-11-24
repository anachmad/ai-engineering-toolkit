"""Registry-driven artifact validation; no approval or release decision."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def validate_artifact(path, kind, version, profile, id_formats_path=None, brd_source=None, srs_priorities=None, prd_source=None, project_root=None, sad_id_sources=None):
    registry = json.loads((ROOT / 'standards/artifacts-v1.json').read_text(encoding='utf-8'))
    if registry.get('schema_version') != 1:
        raise ValueError('Unsupported artifact registry version')
    profiles = json.loads((ROOT / 'standards/profiles.yaml').read_text(encoding='utf-8'))['profiles']
    if profile not in profiles:
        raise ValueError(f'Unknown profile: {profile}')
    entry = registry.get('artifacts', {}).get(kind)
    if entry is None:
        raise ValueError(f'Unknown artifact: {kind}')
    if entry.get('status') != 'approved':
        raise ValueError(f'Artifact {kind} is proposed and not approved for enforcement')
    item = entry.get('versions', {}).get(version)
    if item is None:
        raise ValueError(f'Unsupported {kind} standard version: {version}')
    validators = {'brd': {'brd'}, 'prd': {'section-structure', 'prd-fields'}, 'srs': {'srs-fields'}, 'sad': {'sad-fields', 'sad-profile'}, 'adr': {'adr-fields'}}
    if item.get('validator') not in validators.get(kind, set()):
        raise ValueError('Unsupported artifact validator')
    # Contract path is constrained to the canonical registry's standard directory.
    contract_path = (ROOT / item['contract']).resolve()
    if not contract_path.is_relative_to((ROOT / 'standards').resolve()):
        raise ValueError('Invalid artifact contract location')
    contract = json.loads(contract_path.read_text(encoding='utf-8'))
    if contract.get('schema_version') != 1:
        raise ValueError('Unsupported BRD contract schema version')
    if kind == 'brd':
        from .brd import validate
    elif item['validator'] == 'adr-fields':
        from .adr import validate
    elif item['validator'] in ('sad-fields', 'sad-profile'):
        from .sad import validate
    elif item['validator'] == 'srs-fields':
        from .srs import validate
    elif item['validator'] == 'prd-fields':
        from .prd import validate
    else:
        from .sections import validate
    id_formats = None
    if id_formats_path:
        if not item.get('supports_project_id_formats'):
            raise ValueError('Selected artifact standard version does not support project ID formats')
        from .id_formats import load
        id_formats = load(id_formats_path)
    text = Path(path).read_text(encoding='utf-8')
    source_ids = None
    if brd_source:
        if kind != 'prd' or item['validator'] != 'prd-fields':
            raise ValueError('BRD source checking requires a PRD field validator')
        from .traceability import business_ids
        brd_contract = json.loads((ROOT / 'standards/brd-v1.json').read_text(encoding='utf-8'))
        source_ids = business_ids(Path(brd_source).read_text(encoding='utf-8'), brd_contract, id_formats)
    priorities = None
    product_sources = None
    if (srs_priorities or prd_source) and kind != 'srs':
        raise ValueError('SRS priority and PRD source options require an SRS')
    if srs_priorities:
        priorities = json.loads(Path(srs_priorities).read_text(encoding='utf-8'))
        if not isinstance(priorities, list) or not priorities or not all(isinstance(v, str) and v.strip() == v and v and len(v) <= 50 for v in priorities) or len(set(priorities)) != len(priorities):
            raise ValueError('SRS priorities must be a nonempty JSON array of unique nonempty strings')
    if prd_source:
        from .traceability import product_ids
        prd_contract = json.loads((ROOT / 'standards/prd-v3.json').read_text(encoding='utf-8'))
        product_sources = product_ids(Path(prd_source).read_text(encoding='utf-8'), prd_contract, id_formats)
    sad_mode = None
    sad_applicability = 'NOT_EVALUATED'
    reference_checks = []
    if sad_id_sources and (kind != 'sad' or item['validator'] != 'sad-profile'):
        raise ValueError('SAD ID source checking requires SAD standard version 2')
    if sad_id_sources and not project_root:
        raise ValueError('SAD ID source checking requires --project-root')
    if project_root and not (kind == 'adr' or (kind == 'sad' and item['validator'] == 'sad-profile')):
        raise ValueError('Project-root reference checks require ADR v1 or SAD v2')
    if kind == 'sad' and item['validator'] == 'sad-profile':
        manifest = None
        if project_root:
            project = Path(project_root).resolve(strict=True)
            manifest = json.loads((project / '.engineering/project.yaml').read_text(encoding='utf-8'))
            if not isinstance(manifest, dict) or manifest.get('schema_version') != 1 or manifest.get('profile') != profile:
                raise ValueError('Project manifest missing or conflicts with selected profile')
            if 'sad_mode' in manifest and manifest['sad_mode'] not in ('concise', 'full'):
                raise ValueError('Invalid project sad_mode; expected concise or full')
        if manifest and ((profile == 'lean' and manifest.get('sad_mode') == 'full') or (profile == 'business-critical' and manifest.get('sad_mode') == 'concise')):
            raise ValueError('Project SAD mode conflicts with selected profile')
        if profile == 'lean':
            sad_mode = 'concise'
        elif profile == 'business-critical':
            sad_mode = 'full'
        elif manifest and manifest.get('sad_mode') in ('concise', 'full'):
            sad_mode = manifest['sad_mode']
        if sad_mode:
            sad_applicability = 'SELECTED'
            findings = validate(text, contract, sad_mode)
        else:
            sad_applicability = 'REVIEW_REQUIRED'
            findings = [{'level': 'WARN', 'location': 'project', 'message': 'Standard SAD mode not selected; owner review required'}]
        if project_root:
            from .sad_references import check
            ref_findings, reference_checks = check(text, path, project_root, sad_id_sources, id_formats, ROOT)
            findings.extend(ref_findings)
        else:
            findings.append({'level': 'WARN', 'location': 'references', 'message': 'Project root not selected; local references not verified'})
    elif kind == 'adr':
        findings = validate(text, contract, id_formats)
        if project_root:
            from .sad_references import check
            ref_findings, reference_checks = check(text, path, project_root)
            findings.extend(ref_findings)
        else:
            findings.append({'level': 'WARN', 'location': 'references', 'message': 'Project root not selected; references not verified'})
    elif kind == 'srs':
        findings = validate(text, contract, id_formats, priorities, product_sources)
    elif kind == 'prd' and item['validator'] == 'prd-fields':
        findings = validate(text, contract, id_formats, source_ids)
    else:
        findings = validate(text, contract, id_formats) if item.get('supports_project_id_formats') else validate(text, contract)
    outcome = 'FAIL' if any(x['level'] == 'ERROR' for x in findings) else 'WARN' if findings else 'PASS'
    return {
        'artifact': kind, 'standard_version': version, 'profile': profile,
        'id_format_source': str(id_formats_path) if id_formats_path else 'standard default',
        'project_id_formats': id_formats or {},
        'approval_scope': item.get('approval_scope', entry.get('approval_scope', 'BRD structure')),
        'validation_scope': 'ADR structure and local fields' if kind == 'adr' else ('SAD structure and local fields' if kind == 'sad' else ('SRS structure and local requirement fields' if kind == 'srs' else ('BRD-local checks' if kind == 'brd' else ('PRD structure and local requirement fields' if item['validator'] == 'prd-fields' else 'section structure only')))),
        'sad_applicability': sad_applicability, 'sad_mode': sad_mode, 'reference_checks': reference_checks,
        'srs_priority_values': priorities,
        'prd_source_check': {'status': 'CHECKED_ID_EXISTENCE' if prd_source else 'NOT_RUN', 'path': str(prd_source) if prd_source else None, 'scope': 'Selected PRD table only; authority and meaning not verified'},
        'outcome': outcome, 'findings': findings,
        'profile_applicability_enforced': bool(kind == 'sad' and item['validator'] == 'sad-profile' and sad_mode),
        'standard_version_embedded_in_artifact': 'NOT_VERIFIED',
        'brd_source_check': {'status': 'CHECKED_ID_EXISTENCE' if brd_source else 'NOT_RUN', 'path': str(brd_source) if brd_source else None, 'scope': 'Selected BRD table only; authority, meaning and completeness not verified'},
        'semantic_review': 'NOT_RUN', 'human_approval': 'NOT_VERIFIED',
        'release_authorized': False,
        'limitations': ['Project-wide traceability, source authority and approvals are not verified',
                        'Document-level validation does not enforce lifecycle or security gates']
    }
