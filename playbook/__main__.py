import argparse
import json
from pathlib import Path
import string
import sys

ROOT = Path(__file__).resolve().parent.parent


PROFILE_NAMES = {'lean', 'standard', 'business-critical'}
GATE_NAMES = {'requirements', 'code', 'security', 'qa', 'operations', 'release'}
DOCUMENT_STATUSES = {'draft', 'in-review', 'approved', 'deprecated'}


def require_text(value, field):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'{field} must be a nonempty string')


def validate_manifest(manifest):
    if not isinstance(manifest, dict) or type(manifest.get('schema_version')) is not int or manifest['schema_version'] != 1:
        raise ValueError('Invalid project manifest schema version')
    if manifest.get('profile') not in PROFILE_NAMES or manifest.get('ui') not in ('yes', 'no', 'unknown'):
        raise ValueError('Invalid project manifest profile or UI applicability')
    for field in ('name', 'standards_path'):
        require_text(manifest.get(field), f'project manifest {field}')
    if manifest.get('status') not in DOCUMENT_STATUSES:
        raise ValueError('Invalid project manifest status')


def load_policy():
    profiles = json.loads((ROOT / 'standards/profiles.yaml').read_text())
    gates = json.loads((ROOT / 'standards/quality-gates.yaml').read_text())
    prompts = json.loads((ROOT / 'standards/document-prompts.yaml').read_text())
    for name, policy in (('profiles', profiles), ('quality gates', gates), ('document prompts', prompts)):
        if not isinstance(policy, dict) or type(policy.get('schema_version')) is not int or policy['schema_version'] != 1:
            raise ValueError(f'Invalid {name} schema version')
    if not isinstance(profiles.get('profiles'), dict) or set(profiles['profiles']) != PROFILE_NAMES:
        raise ValueError('Invalid profile definitions')
    if profiles.get('default_profile') not in PROFILE_NAMES:
        raise ValueError('Invalid default profile')
    factors = profiles.get('escalation_factors')
    if not isinstance(factors, list) or not factors:
        raise ValueError('Escalation factors must be a nonempty list')
    for factor in factors:
        require_text(factor, 'escalation factor')
    if not isinstance(gates.get('profiles'), dict) or set(gates['profiles']) != PROFILE_NAMES:
        raise ValueError('Invalid quality gate profiles')
    for name, profile_gates in gates['profiles'].items():
        if not isinstance(profile_gates, dict) or set(profile_gates) != GATE_NAMES:
            raise ValueError(f'Invalid quality gates for {name}')
        for gate, value in profile_gates.items():
            require_text(value, f'{name} {gate} gate')
    documents = prompts.get('documents')
    if not isinstance(documents, dict):
        raise ValueError('Invalid document prompts')
    for name, sections in documents.items():
        safe_relative(name)
        if not isinstance(sections, list) or not sections:
            raise ValueError(f'Invalid prompts for {name}')
        for section in sections:
            require_text(section, f'prompt for {name}')
    for name, profile in profiles['profiles'].items():
        if not isinstance(profile, dict):
            raise ValueError(f'Invalid profile: {name}')
        all_paths = []
        for key in ('artifacts', 'conditional_artifacts'):
            paths = profile.get(key)
            if not isinstance(paths, list) or not all(isinstance(x, str) for x in paths):
                raise ValueError(f'Invalid artifact list: {name} {key}')
            for item in paths:
                safe_relative(item)
                if item.startswith('docs/') and item not in documents:
                    raise ValueError(f'Missing document prompts: {item}')
            all_paths.extend(paths)
        if len(all_paths) != len(set(all_paths)):
            raise ValueError(f'Duplicate artifact: {name}')
    return profiles, prompts


def safe_relative(name):
    path = Path(name)
    if path.is_absolute() or not path.parts or any(p in ('.', '..') for p in path.parts):
        raise ValueError(f'Unsafe artifact path: {name}')
    return path


def destination(base, name):
    rel = safe_relative(name)
    path = base
    for part in rel.parts:
        path = path / part
        if path.is_symlink():
            raise ValueError(f'Symlink in destination: {path}')
    return path


def title(path):
    return Path(path).stem.replace('-', ' ').title()


def init(args, policy, prompts):
    base = Path(args.path).absolute()
    if base.is_symlink():
        raise ValueError('Project path must not be a symlink')
    base.mkdir(parents=True, exist_ok=True)
    manifest_path = destination(base, '.engineering/project.yaml')
    # An existing manifest determines project policy; never mix scaffolds from different profiles.
    if manifest_path.exists():
        old = json.loads(manifest_path.read_text())
        validate_manifest(old)
        if old.get('profile') != args.profile or old.get('ui') != ('yes' if args.ui else 'unknown'):
            raise ValueError('Existing project manifest conflicts with requested profile or UI selection; audit and review it first')
    profile = policy['profiles'][args.profile]
    paths = profile['artifacts'] + (profile['conditional_artifacts'] if args.ui else [])
    manifest = {'schema_version': 1, 'name': args.name, 'profile': args.profile, 'ui': 'yes' if args.ui else 'unknown', 'standards_path': str(ROOT / 'standards'), 'status': 'draft'}
    planned = {'.engineering/project.yaml': json.dumps(manifest, indent=2) + '\n'}
    for name in paths:
        source = ROOT / 'templates/project' / name if name in ('README.md', 'AGENTS.md', 'CLAUDE.md') else ROOT / 'templates/project/document.md'
        sections = '\n'.join(f'## {section}\n\nTBD.\n' for section in prompts['documents'].get(name, []))
        template = source.read_text().replace('{{project_name}}', '${project_name}').replace('{{title}}', '${title}').replace('{{sections}}', '${sections}')
        planned[name] = string.Template(template).substitute(project_name=args.name, title=title(name), sections=sections)
    # Preflight all paths before writing anything.
    for name in planned:
        destination(base, name)
    for name, content in planned.items():
        target = destination(base, name)
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            with target.open('x', encoding='utf-8') as f:
                f.write(content)
            print(f'created: {name}')
        except FileExistsError:
            print(f'preserved: {name}')
    print('Review drafts, applicability, escalation, approvals and evidence with the project owner.')


def audit(args, policy):
    base = Path(args.path).absolute()
    if base.is_symlink():
        raise ValueError('Project path must not be a symlink')
    manifest_path = destination(base, '.engineering/project.yaml')
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text())
        validate_manifest(manifest)
        if args.profile and args.profile != manifest.get('profile'):
            raise ValueError('Requested profile conflicts with existing manifest')
    elif args.profile:
        manifest = {'schema_version': 1, 'profile': args.profile, 'ui': 'unknown'}
        print('missing: .engineering/project.yaml')
    else:
        raise ValueError('Manifest missing; supply --profile to audit an existing repository')
    profile = policy['profiles'][manifest['profile']]
    paths = profile['artifacts'] + (profile['conditional_artifacts'] if manifest['ui'] == 'yes' else [])
    missing = [] if manifest_path.exists() else ['.engineering/project.yaml']
    for name in paths:
        path = destination(base, name)
        present = path.is_file()
        print(f'{"present" if present else "missing"}: {name}')
        if not present:
            missing.append(name)
    if manifest['ui'] == 'unknown':
        print('review: UI applicability is unknown')
    print('review: content, risk escalation, approvals, traceability and gate evidence require human assessment; presence is not compliance')
    return 1 if missing else 0


def main():
    parser = argparse.ArgumentParser(description='Generate and audit engineering documentation')
    sub = parser.add_subparsers(dest='command', required=True)
    create = sub.add_parser('init')
    create.add_argument('--path', required=True)
    create.add_argument('--profile', required=True, choices=('lean', 'standard', 'business-critical'))
    create.add_argument('--name', required=True)
    create.add_argument('--ui', action='store_true')
    check = sub.add_parser('audit')
    check.add_argument('--path', required=True)
    check.add_argument('--profile', choices=('lean', 'standard', 'business-critical'))
    args = parser.parse_args()
    try:
        policy, prompts = load_policy()
        return init(args, policy, prompts) or 0 if args.command == 'init' else audit(args, policy)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f'error: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
