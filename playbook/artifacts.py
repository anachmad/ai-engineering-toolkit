"""Registry-driven artifact validation; no approval or release decision."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def validate_artifact(path, kind, version, profile, id_formats_path=None):
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
    validators = {'brd': {'brd'}, 'prd': {'section-structure', 'prd-fields'}}
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
    findings = validate(text, contract, id_formats) if item.get('supports_project_id_formats') else validate(text, contract)
    outcome = 'FAIL' if any(x['level'] == 'ERROR' for x in findings) else 'WARN' if findings else 'PASS'
    return {
        'artifact': kind, 'standard_version': version, 'profile': profile,
        'id_format_source': str(id_formats_path) if id_formats_path else 'standard default',
        'project_id_formats': id_formats or {},
        'approval_scope': item.get('approval_scope', entry.get('approval_scope', 'BRD structure')),
        'validation_scope': 'BRD-local checks' if kind == 'brd' else ('PRD structure and local requirement fields' if item['validator'] == 'prd-fields' else 'section structure only'),
        'outcome': outcome, 'findings': findings,
        'profile_applicability_enforced': False,
        'standard_version_embedded_in_artifact': 'NOT_VERIFIED',
        'semantic_review': 'NOT_RUN', 'human_approval': 'NOT_VERIFIED',
        'release_authorized': False,
        'limitations': ['Local checks only; project-wide traceability and approvals are not verified',
                        'Document-level validation does not enforce lifecycle or security gates']
    }
