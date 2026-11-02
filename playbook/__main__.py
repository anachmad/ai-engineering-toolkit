import argparse
import difflib
import hashlib
import tempfile
import json
import os
import shutil
from pathlib import Path
import string
import sys

ROOT = Path(__file__).resolve().parent.parent


PROFILE_NAMES = {'lean', 'standard', 'business-critical'}
GATE_NAMES = {'requirements', 'code', 'security', 'qa', 'operations', 'release'}


def require_text(value, field):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'{field} must be a nonempty string')


def validate_manifest(manifest):
    if not isinstance(manifest, dict) or type(manifest.get('schema_version')) is not int or manifest['schema_version'] != 1:
        raise ValueError('Invalid or unsupported project manifest schema version')
    schema = json.loads((ROOT / 'standards/schemas/project-v1.json').read_text())
    if schema.get('schema_version') != 1:
        raise ValueError('Unsupported project schema version')
    for field in schema['required']:
        if field not in manifest:
            raise ValueError(f'Missing project manifest field: {field}')
    for field, rules in schema['properties'].items():
        if field not in manifest:
            continue
        value = manifest[field]
        if rules['type'] == 'string' and not isinstance(value, str):
            raise ValueError(f'Invalid project manifest {field}: expected string')
        if rules['type'] == 'integer' and type(value) is not int:
            raise ValueError(f'Invalid project manifest {field}: expected integer')
        if rules.get('min_length') and not value.strip():
            raise ValueError(f'Invalid project manifest {field}: empty string')
        if 'enum' in rules and value not in rules['enum']:
            raise ValueError(f'Invalid project manifest {field}')


def load_policy():
    profiles = json.loads((ROOT / 'standards/profiles.yaml').read_text())
    gates = json.loads((ROOT / 'standards/quality-gates.yaml').read_text())
    prompts = json.loads((ROOT / 'standards/document-prompts.yaml').read_text())
    contract = json.loads((ROOT / 'standards/schemas/policies-v1.json').read_text())
    if contract.get('schema_version') != 1:
        raise ValueError('Unsupported policy schema version')
    types = {'integer': int, 'string': str, 'object': dict, 'array': list}
    for name, policy in (('profiles', profiles), ('quality_gates', gates), ('document_prompts', prompts)):
        if not isinstance(policy, dict) or type(policy.get('schema_version')) is not int or policy['schema_version'] != 1:
            raise ValueError(f'Invalid {name} schema version')
        rules = contract['policies'][name]
        for field in rules['required']:
            if field not in policy:
                raise ValueError(f'Missing {name} field: {field}')
        for field, kind in rules['properties'].items():
            if field in policy and type(policy[field]) is not types[kind]:
                raise ValueError(f'Invalid {name} field: {field}')
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
    scaffold_files = profiles.get('scaffold_files', {})
    if not isinstance(scaffold_files, dict):
        raise ValueError('Invalid scaffold files')
    for target, source in scaffold_files.items():
        safe_relative(target)
        if not isinstance(source, str):
            raise ValueError('Invalid scaffold file template')
        relative_source = safe_relative(source)
        if relative_source.parts[:2] != ('templates', 'project'):
            raise ValueError('Scaffold templates must live under templates/project')
        if not (ROOT / relative_source).is_file():
            raise ValueError(f'Missing scaffold template: {source}')
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



def project_base(path):
    requested = Path(path).absolute()
    if requested.is_symlink():
        raise ValueError('Project path must not be a symlink')
    base = requested.resolve()
    print(f'effective project path: {base}')
    return base


def validate_standards_location(base, manifest):
    selected = Path(manifest['standards_path'])
    if not selected.is_absolute():
        selected = base / selected
    if not selected.is_dir():
        raise ValueError(f'Project standards directory is missing: {selected}')
    if selected.resolve() != (ROOT / 'standards').resolve():
        raise ValueError(f'Project standards directory differs from this toolkit: {selected}')


def render_document(name, prompts):
    source = ROOT / 'templates/project' / name if name in ('README.md', 'AGENTS.md', 'CLAUDE.md') else ROOT / 'templates/project/document.md'
    sections = '\n'.join(f'## {section}\n\nTBD.\n' for section in prompts['documents'].get(name, []))
    return source, sections


def init(args, policy, prompts):
    base = project_base(args.path)
    base.mkdir(parents=True, exist_ok=True)
    manifest_path = destination(base, '.engineering/project.yaml')
    # An existing manifest determines project policy; never mix scaffolds from different profiles.
    if manifest_path.exists():
        old = json.loads(manifest_path.read_text())
        validate_manifest(old)
        validate_standards_location(base, old)
        if old.get('profile') != args.profile or old.get('ui') != ('yes' if args.ui else 'unknown'):
            raise ValueError('Existing project manifest conflicts with requested profile or UI selection; audit and review it first')
    profile = policy['profiles'][args.profile]
    paths = profile['artifacts'] + (profile['conditional_artifacts'] if args.ui else [])
    standards_path = '.engineering/toolkit/standards' if ROOT == base / '.engineering/toolkit' else str(ROOT / 'standards')
    manifest = {'schema_version': 1, 'name': args.name, 'profile': args.profile, 'ui': 'yes' if args.ui else 'unknown', 'standards_path': standards_path, 'status': 'draft'}
    planned = {'.engineering/project.yaml': json.dumps(manifest, indent=2) + '\n'}
    for name in paths:
        source = ROOT / 'templates/project' / name if name in ('README.md', 'AGENTS.md', 'CLAUDE.md') else ROOT / 'templates/project/document.md'
        sections = '\n'.join(f'## {section}\n\nTBD.\n' for section in prompts['documents'].get(name, []))
        template = source.read_text().replace('{{project_name}}', '${project_name}').replace('{{title}}', '${title}').replace('{{sections}}', '${sections}')
        planned[name] = string.Template(template).substitute(project_name=args.name, title=title(name), sections=sections)
    for name, source in policy.get('scaffold_files', {}).items():
        if name in planned:
            raise ValueError(f'Duplicate scaffold target: {name}')
        planned[name] = (ROOT / safe_relative(source)).read_text(encoding='utf-8')
    # Preflight all paths before writing anything.
    for name in planned:
        target = destination(base, name)
        if target.exists() and not target.is_file():
            raise ValueError(f'Expected file but found another object: {target}')
    for name, content in planned.items():
        target = destination(base, name)
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            with target.open('x', encoding='utf-8') as f:
                f.write(content)
            print(f'created: {name}')
        except FileExistsError:
            if target.is_symlink() or not target.is_file():
                raise ValueError(f'Expected file but found another object: {target}')
            print(f'preserved: {name}')
    print('Review drafts, applicability, escalation, approvals and evidence with the project owner.')


def audit(args, policy):
    base = project_base(args.path)
    manifest_path = destination(base, '.engineering/project.yaml')
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text())
        validate_manifest(manifest)
        validate_standards_location(base, manifest)
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


def set_ui(args, policy, prompts):
    base = project_base(args.path)
    manifest_path = destination(base, '.engineering/project.yaml')
    original_bytes = manifest_path.read_bytes()
    original = original_bytes.decode('utf-8')
    manifest = json.loads(original)
    validate_manifest(manifest)
    validate_standards_location(base, manifest)
    digest = hashlib.sha256(original_bytes).hexdigest()
    print(f'manifest sha256: {digest}')
    if args.apply and args.expected_sha256 != digest:
        raise ValueError('Manifest hash differs from preview (or --expected-sha256 is missing); review again')
    updated = dict(manifest)
    updated['ui'] = args.ui
    replacement = json.dumps(updated, indent=2, ensure_ascii=False) + '\n'
    ui_name = 'docs/01-requirements/ui-ux.md'
    ui_path = destination(base, ui_name)
    if ui_path.exists() and not ui_path.is_file():
        raise ValueError(f'Expected file but found another object: {ui_path}')
    print(''.join(difflib.unified_diff(original.splitlines(keepends=True), replacement.splitlines(keepends=True), fromfile='current project manifest', tofile='proposed project manifest')), end='')
    if args.ui == 'yes':
        print(f'{"preserve" if ui_path.is_file() else "create"}: {ui_name}')
    if not args.apply:
        print('Preview only. Review and authorize before running with --apply.')
        return
    # Apply is an explicit request to update this manifest; check for concurrent edits.
    if manifest_path.read_bytes() != original_bytes:
        raise ValueError('Manifest changed since preview; review again')
    if args.ui == 'yes' and not ui_path.exists():
        source, sections = render_document(ui_name, prompts)
        template = source.read_text().replace('{{title}}', '${title}').replace('{{sections}}', '${sections}')
        content = string.Template(template).substitute(title=title(ui_name), sections=sections)
        ui_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with ui_path.open('x', encoding='utf-8') as f:
                f.write(content)
        except FileExistsError:
            raise ValueError('UI document appeared during update; review and retry')
    if manifest_path.read_bytes() != original_bytes:
        raise ValueError('Manifest changed during update; UI draft may have been created; review before retry')
    if updated == manifest:
        print('Project manifest already has the requested UI value; preserved unchanged.')
        return
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile('w', encoding='utf-8', dir=manifest_path.parent, delete=False) as f:
            temp_path = Path(f.name)
            f.write(replacement)
        os.chmod(temp_path, manifest_path.stat().st_mode & 0o777)
        os.replace(temp_path, manifest_path)
    finally:
        if temp_path is not None and temp_path.exists():
            temp_path.unlink()
    print('Updated project manifest. Review and commit the changes.')


def share(args):
    """Create a project-owned copy and native links, without modifying existing paths."""
    base = project_base(args.path)
    if not base.is_dir():
        raise ValueError('Project path must be an existing directory')
    toolkit = destination(base, '.engineering/toolkit')
    links = {
        '.agents/skills/software-engineering-playbook': 'codex',
        '.claude/skills/software-engineering-playbook': 'claude',
    }
    for name in ('.engineering/toolkit', *links):
        target = destination(base, name)
        if target.exists() or target.is_symlink():
            raise ValueError(f'Path already exists; no files changed: {target}')
    # Check source symlinks before copying; never follow unexpected links.
    sources = ('standards', 'skills', 'adapters', 'templates', 'playbook')
    for name in sources:
        source = ROOT / name
        if not source.is_dir() or source.is_symlink() or any(p.is_symlink() for p in source.rglob('*')):
            raise ValueError(f'Invalid toolkit source: {source}')
    toolkit.parent.mkdir(parents=True, exist_ok=True)
    toolkit.mkdir()  # Exclusive creation; never replace an existing toolkit.
    try:
        for name in sources:
            shutil.copytree(ROOT / name, toolkit / name, ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '*.pyo'))
        hashes = {p.relative_to(toolkit).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(toolkit.rglob('*')) if p.is_file()}
        provenance = {'schema_version': 1, 'description': 'SHA-256 of copied files, including any uncommitted source changes; not a release or approval record.', 'files': hashes}
        (toolkit / 'provenance.json').write_text(json.dumps(provenance, indent=2) + '\n', encoding='utf-8')
        for name, host in links.items():
            target = destination(base, name)
            target.parent.mkdir(parents=True, exist_ok=True)
            relative = os.path.relpath(toolkit / 'adapters' / host / 'software-engineering-playbook', target.parent)
            target.symlink_to(relative, target_is_directory=True)
            print(f'created: {name} -> {relative}')
    except OSError as exc:
        raise OSError(f'Shared setup incomplete; inspect {toolkit} and any created links before retrying: {exc}') from exc
    print(f'created: {toolkit}')
    print('Review and commit the project-owned toolkit and links together; update them through project review.')


def main():
    parser = argparse.ArgumentParser(description='Generate and audit engineering documentation')
    sub = parser.add_subparsers(dest='command', required=True)
    create = sub.add_parser('init')
    create.add_argument('--path', required=True)
    create.add_argument('--profile', required=True, choices=('lean', 'standard', 'business-critical'))
    create.add_argument('--name', required=True)
    create.add_argument('--ui', action='store_true')
    ui = sub.add_parser('set-ui', help='Preview or apply an explicit UI applicability change')
    ui.add_argument('--path', required=True)
    ui.add_argument('--ui', required=True, choices=('yes', 'no', 'unknown'))
    ui.add_argument('--apply', action='store_true')
    ui.add_argument('--expected-sha256', help='Manifest SHA-256 from the reviewed preview; required with --apply')
    shared = sub.add_parser('share', help='Add a project-owned toolkit and agent skill links')
    shared.add_argument('--path', required=True)
    check = sub.add_parser('audit')
    check.add_argument('--path', required=True)
    check.add_argument('--profile', choices=('lean', 'standard', 'business-critical'))
    args = parser.parse_args()
    try:
        policy, prompts = load_policy()
        if args.command == 'init':
            return init(args, policy, prompts) or 0
        if args.command == 'set-ui':
            return set_ui(args, policy, prompts) or 0
        if args.command == 'share':
            return share(args) or 0
        return audit(args, policy)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f'error: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
