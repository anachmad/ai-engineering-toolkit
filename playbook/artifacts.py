"""Registry-driven artifact validation; no approval or release decision."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def validate_artifact(path, kind, version, profile):
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
    validators = {'brd': 'brd', 'prd': 'section-structure'}
    if validators.get(kind) != item.get('validator'):
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
    else:
        from .sections import validate
    findings = validate(Path(path).read_text(encoding='utf-8'), contract)
    outcome = 'FAIL' if any(x['level'] == 'ERROR' for x in findings) else 'WARN' if findings else 'PASS'
    return {
        'artifact': kind, 'standard_version': version, 'profile': profile,
        'approval_scope': item.get('approval_scope', entry.get('approval_scope', 'BRD structure')),
        'validation_scope': 'BRD-local checks' if kind == 'brd' else 'section structure only',
        'outcome': outcome, 'findings': findings,
        'profile_applicability_enforced': False,
        'standard_version_embedded_in_artifact': 'NOT_VERIFIED',
        'semantic_review': 'NOT_RUN', 'human_approval': 'NOT_VERIFIED',
        'release_authorized': False,
        'limitations': ['Local checks only; project-wide traceability and approvals are not verified',
                        'Document-level validation does not enforce lifecycle or security gates']
    }
