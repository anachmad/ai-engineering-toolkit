"""Declarative routing and security decisions. No external skill is executed here."""
import hashlib
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RANK = {'low': 0, 'medium': 1, 'high': 2, 'critical': 3}
STATES = {'PASS', 'FAIL', 'NOT_APPLICABLE', 'NOT_RUN', 'WAIVED'}
REVIEW_FIELDS = ('publisher_reviewed', 'source_reviewed', 'instructions_reviewed', 'executables_reviewed', 'permissions_reviewed', 'injection_reviewed', 'dependencies_reviewed')


def load(path):
    with Path(path).open(encoding='utf-8') as f:
        value = json.load(f)
    if not isinstance(value, dict) or type(value.get('schema_version')) is not int or value['schema_version'] != 1:
        raise ValueError(f'Unsupported or invalid schema in {path}')
    return value


def policy(path=None):
    p = load(path or ROOT / 'standards/orchestration.yaml')
    skills = p.get('skills')
    routes = p.get('routes')
    security = p.get('security')
    if not isinstance(skills, dict) or not isinstance(routes, dict) or not isinstance(security, dict):
        raise ValueError('Missing registry, routes or security policy')
    if not skills.get('secure-engineering', {}).get('enabled') or skills['secure-engineering'].get('provider') != 'internal':
        raise ValueError('secure-engineering is mandatory')
    for name, skill in skills.items():
        if not isinstance(name, str) or not isinstance(skill, dict) or type(skill.get('enabled')) is not bool:
            raise ValueError('Invalid skill entry')
        if not isinstance(skill.get('capabilities'), list) or not skill['capabilities']:
            raise ValueError(f'Missing capabilities: {name}')
        if not isinstance(skill.get('provider'), str) or not skill['provider'].strip():
            raise ValueError(f'Invalid provider: {name}')
        if skill.get('provider') != 'internal' and not isinstance(skill.get('source'), str):
            raise ValueError(f'Missing source: {name}')
        hosts = skill.get('supported_hosts')
        if not isinstance(hosts, dict) or set(hosts) != {'codex', 'claude'} or any(v not in ('verified', 'unverified', 'unsupported') for v in hosts.values()):
            raise ValueError(f'Invalid host configuration: {name}')
        required = skill.get('required_for', {})
        if not isinstance(required, dict) or not isinstance(required.get('intents', []), list) or not isinstance(required.get('risks', []), list) or any(x not in RANK for x in required.get('risks', [])):
            raise ValueError(f'Invalid required capability policy: {name}')
    for name, skill in skills.items():
        requirement = skill.get('required_for', {})
        if requirement and (not requirement.get('intents') or not requirement.get('risks') or any(not isinstance(intent, str) or intent not in routes for intent in requirement.get('intents', []))):
            raise ValueError(f'Invalid required capability intents or risks: {name}')
    for intent, route in routes.items():
        if not isinstance(route, dict) or route.get('primary') not in {*skills, 'release-governance'} or not isinstance(route.get('secondary'), list):
            raise ValueError(f'Invalid route: {intent}')
        if any(x not in skills for x in route['secondary']):
            raise ValueError(f'Invalid secondary skill: {intent}')
        if 'capability' in route:
            capability = route['capability']
            primary = route['primary']
            if not isinstance(capability, str) or not capability.strip() or primary == 'release-governance' or capability not in skills[primary]['capabilities']:
                raise ValueError(f'Primary skill lacks route capability: {intent}')
    if routes.get('release', {}).get('primary') != 'release-governance' or routes.get('security-review', {}).get('primary') != 'secure-engineering':
        raise ValueError('Release governance and security policy owners cannot be replaced by external skills')
    if security.get('default_risk') not in RANK or set(security.get('gates', {})) != {'S1','S2','S3','S4','S5'}:
        raise ValueError('Invalid security risk or gates')
    canonical_profiles = load(ROOT / 'standards/profiles.yaml').get('profiles')
    canonical_gates = load(ROOT / 'standards/quality-gates.yaml').get('profiles')
    floors = security.get('profile_minimum_risk')
    if not isinstance(canonical_profiles, dict) or not isinstance(canonical_gates, dict) or set(canonical_profiles) != set(canonical_gates):
        raise ValueError('Canonical profiles and quality gates disagree')
    if not isinstance(floors, dict) or set(floors) != set(canonical_profiles) or any(v not in RANK for v in floors.values()):
        raise ValueError('Invalid profile risk floors')
    if not isinstance(security.get('authorized_waiver_approvers'), list) or type(security.get('critical_exception_enabled')) is not bool:
        raise ValueError('Invalid waiver policy')
    for factor, level in security.get('factor_levels', {}).items():
        if level not in RANK:
            raise ValueError(f'Invalid risk factor: {factor}')
    for name, gate in security['gates'].items():
        if gate.get('minimum_risk') not in RANK:
            raise ValueError(f'Invalid minimum risk for {name}')
        capabilities = gate.get('accepted_skill_capabilities')
        if capabilities is not None and (not isinstance(capabilities, list) or not capabilities or any(not isinstance(x, str) or not x.strip() for x in capabilities)):
            raise ValueError(f'Missing accepted skill capabilities for {name}')
    for stage, gates in security.get('stage_gates', {}).items():
        if not isinstance(gates, list) or any(g not in security['gates'] for g in gates):
            raise ValueError(f'Invalid stage gates: {stage}')
    if any(route.get('security_stage') is not None and route.get('security_stage') not in security['stage_gates'] for route in routes.values()):
        raise ValueError('Route refers to an unknown security stage')
    if set(security.get('stage_gates', {}).get('release', [])) != set(security['gates']):
        raise ValueError('Release must consider every security gate')
    return p


def canonical_profile_gates(profile):
    if profile is None:
        return None
    return load(ROOT / 'standards/quality-gates.yaml')['profiles'][profile]


def profile_risk(p, risk, profile):
    if risk not in RANK:
        raise ValueError('Invalid risk')
    if profile is None:
        return risk
    floors = p['security']['profile_minimum_risk']
    if profile not in floors:
        raise ValueError('Invalid project profile')
    return max((risk, floors[profile]), key=RANK.get)


def classify(p, factors, profile=None):
    if not isinstance(factors, dict):
        raise ValueError('Risk factors must be an object')
    unknown = set(factors) - set(p['security']['factor_levels'])
    if unknown or any(type(v) is not bool for v in factors.values()):
        raise ValueError(f'Unknown or non-boolean risk factors: {sorted(unknown)}')
    level = p['security']['default_risk']
    drivers = []
    for factor, flag in factors.items():
        if flag:
            drivers.append(factor)
            candidate = p['security']['factor_levels'][factor]
            if RANK[candidate] > RANK[level]:
                level = candidate
    level = profile_risk(p, level, profile)
    return {'level': level, 'profile': profile, 'drivers': drivers, 'requires_owner_review': True, 'unknown_factors': sorted(set(p['security']['factor_levels']) - set(factors)), 'basis': 'configured default and supplied factors; owner review required'}


def tree_hash(path):
    root = Path(path)
    if root.is_symlink() or not root.is_dir():
        raise ValueError('Skill path must be an existing non-symlink directory')
    h = hashlib.sha256()
    files = sorted(root.rglob('*'))
    if any(p.is_symlink() for p in files):
        raise ValueError('Skill tree contains a symlink')
    for p in files:
        if p.is_file():
            name = p.relative_to(root).as_posix().encode()
            body = p.read_bytes()
            h.update(len(name).to_bytes(8, 'big')); h.update(name)
            h.update(len(body).to_bytes(8, 'big')); h.update(body)
    return h.hexdigest()


def status(p, skill_id, host, inventory):
    if host not in ('codex','claude') or skill_id not in p['skills']:
        raise ValueError('Unknown host or skill')
    s = p['skills'][skill_id]
    if not isinstance(inventory, dict):
        raise ValueError('Inventory skills must be an object')
    out = {'id':skill_id, 'configured':True, 'enabled':s['enabled'], 'files_present':False, 'installed':False, 'loadable':False, 'available':False, 'compatible':False, 'compatibility_assurance':'NOT_VERIFIED', 'executed':None, 'execution_status':'NOT_VERIFIED', 'reason':'not checked', 'capabilities':s['capabilities']}
    if s['provider'] == 'internal':
        file = ROOT / 'skills' / skill_id / 'SKILL.md'
        record = inventory.get(skill_id, {})
        host_evidence = record.get('host_evidence', {}).get(host, {}) if isinstance(record, dict) and isinstance(record.get('host_evidence', {}), dict) else {}
        verified = s['supported_hosts'].get(host) == 'verified' and isinstance(host_evidence, dict) and isinstance(host_evidence.get('invocation_evidence'), str) and bool(host_evidence['invocation_evidence'].strip())
        installed = isinstance(record, dict) and isinstance(record.get('installation_evidence'), str) and bool(record['installation_evidence'].strip())
        out.update(files_present=file.is_file(), installed=installed and file.is_file(), loadable=file.is_file(), compatible=verified, compatibility_assurance='SELF_ATTESTED' if verified else 'NOT_VERIFIED', available=s['enabled'] and installed and file.is_file() and verified, reason='installation and host invocation attested; task execution not established' if installed and verified else 'internal file present; installation or host invocation not established' if file.is_file() else 'internal skill missing')
        return out
    if not isinstance(inventory, dict):
        raise ValueError('Inventory skills must be an object')
    record = inventory.get(skill_id, {})
    if not isinstance(record, dict):
        raise ValueError(f'Invalid inventory for {skill_id}')
    path = record.get('path')
    if not path:
        out['reason'] = 'no installation path supplied'
        return out
    root = Path(path)
    out['files_present'] = root.is_dir()
    if not out['files_present']:
        out['reason'] = 'installation path missing'
        return out
    entry = record.get('entrypoint')
    if not isinstance(entry, str) or not entry or Path(entry).is_absolute() or '..' in Path(entry).parts:
        out['reason'] = 'safe native entrypoint not supplied'
        return out
    candidate = root / entry
    if candidate.is_symlink() or not candidate.is_file() or not candidate.resolve().is_relative_to(root.resolve()):
        out['reason'] = 'native entrypoint missing or unsafe'
        return out
    out['loadable'] = True
    out['installed'] = isinstance(record.get('installation_evidence'), str) and bool(record['installation_evidence'].strip())
    # A plugin may have multiple native skills. A directory alone is not a host invocation.
    review = record.get('review', {})
    if not isinstance(review, dict):
        raise ValueError('Invalid review record')
    pin = s.get('approved_commit')
    expected = s.get('approved_tree_sha256')
    reasons = []
    if not s['enabled']: reasons.append('disabled')
    if not out['installed']: reasons.append('host installation not attested')
    if not isinstance(pin, str) or not re.fullmatch(r'[0-9a-f]{40}', pin): reasons.append('immutable commit not approved')
    if record.get('observed_commit') != pin or not pin: reasons.append('observed commit not attested')
    if not isinstance(expected, str) or not re.fullmatch(r'[0-9a-f]{64}', expected): reasons.append('content hash not approved')
    elif tree_hash(root) != expected: reasons.append('installed content hash differs')
    if review.get('source') != s['source']: reasons.append('source not verified')
    if not isinstance(review.get('reviewer'), str) or not review['reviewer'].strip(): reasons.append('reviewer missing')
    if not isinstance(review.get('approval'), str) or not review['approval'].strip(): reasons.append('approval evidence missing')
    if any(review.get(f) is not True for f in REVIEW_FIELDS): reasons.append('verification incomplete')
    # The inventory is a human attestation, not an independent host probe.
    host_evidence = record.get('host_evidence', {}).get(host, {}) if isinstance(record.get('host_evidence', {}), dict) else {}
    compatible = s['supported_hosts'].get(host) == 'verified' and isinstance(host_evidence, dict) and isinstance(host_evidence.get('invocation_evidence'), str) and bool(host_evidence['invocation_evidence'].strip())
    out['compatible'] = compatible
    out['compatibility_assurance'] = 'SELF_ATTESTED' if compatible else 'NOT_VERIFIED'
    if not compatible: reasons.append('host compatibility/invocation not verified')
    out['available'] = not reasons
    out['reason'] = '; '.join(reasons) if reasons else 'reviewed and host invocation attested; execution for this task not established'
    return out


def route(p, intent, host, inventory, risk, profile=None):
    if intent not in p['routes'] or risk not in RANK:
        raise ValueError('Unknown intent or risk')
    risk = profile_risk(p, risk, profile)
    rule = p['routes'][intent]
    primary = rule['primary']
    primary_status = {'id':primary,'configured':True,'available':False,'compatible':False,'compatibility_assurance':'NOT_VERIFIED','executed':None,'execution_status':'NOT_VERIFIED','reason':'human/CI governance has not been verified by the router'} if primary == 'release-governance' else status(p, primary, host, inventory)
    secondary = [status(p, x, host, inventory) for x in rule['secondary']]
    checked = {x['id']: x for x in secondary}
    if primary != 'release-governance':
        checked[primary] = primary_status
    required_missing = []
    for skill_id, skill in p['skills'].items():
        requirement = skill.get('required_for', {})
        if intent in requirement.get('intents', []) and risk in requirement.get('risks', []):
            skill_status = checked.get(skill_id)
            if skill_status is None:
                skill_status = status(p, skill_id, host, inventory)
            if not skill_status['available']:
                required_missing.append(skill_id)
    missing = not primary_status['available']
    return {'required_capabilities_missing': required_missing, 'intent':intent,'risk':risk,'primary':primary_status,'secondary':secondary,'security_stage':rule['security_stage'],'fallback':('blocked pending required capability or approved equivalent evidence' if risk in ('high','critical') or required_missing else 'manual workflow; record missing capability and evidence') if missing or required_missing else None,'blocked':bool((missing and risk in ('high','critical')) or required_missing),'note':'Routing is a recommendation, not a tool execution or gate result.'}


def evaluate(p, risk, stage, evidence, today=None, host=None, inventory=None, profile=None):
    if risk not in RANK or stage not in p['security']['stage_gates'] or not isinstance(evidence, dict):
        raise ValueError('Invalid risk, stage, or evidence')
    risk = profile_risk(p, risk, profile)
    results = evidence.get('gates', {})
    findings = evidence.get('findings', [])
    if not isinstance(results, dict) or not isinstance(findings, list) or set(results)-set(p['security']['gates']):
        raise ValueError('Invalid gate evidence or findings')
    now = today or date.today()
    evaluated = []
    for gate_id in p['security']['stage_gates'][stage]:
        gate = p['security']['gates'][gate_id]
        required = RANK[risk] >= RANK[gate['minimum_risk']]
        entry = results.get(gate_id, {})
        if not isinstance(entry, dict): raise ValueError(f'Invalid evidence for {gate_id}')
        outcome = entry.get('outcome','NOT_RUN')
        if outcome not in STATES: raise ValueError(f'Invalid outcome for {gate_id}')
        detail = entry.get('evidence')
        if outcome in ('PASS','FAIL'):
            if not isinstance(detail,str) or not detail.strip():
                raise ValueError(f'{gate_id} {outcome} requires an evidence reference')
            method = entry.get('method')
            if method == 'manual':
                if not isinstance(entry.get('reviewer'), str) or not entry['reviewer'].strip():
                    raise ValueError(f'{gate_id} manual evidence requires a named reviewer')
            elif method == 'skill':
                skill_id = entry.get('skill')
                if not isinstance(skill_id,str) or skill_id not in p['skills'] or host not in ('codex','claude'):
                    raise ValueError(f'{gate_id} skill evidence requires a known skill and host')
                accepted = gate.get('accepted_skill_capabilities', [])
                if not set(p['skills'][skill_id]['capabilities']).intersection(accepted):
                    raise ValueError(f'{gate_id} evidence skill does not declare an accepted capability')
                if not isinstance(entry.get('execution_evidence'),str) or not entry['execution_evidence'].strip():
                    raise ValueError(f'{gate_id} requires task-specific execution evidence')
                if not status(p, skill_id, host, inventory or {})['available']:
                    raise ValueError(f'{gate_id} evidence skill is not available and verified')
            else:
                raise ValueError(f'{gate_id} evidence requires manual or skill method')
        if outcome == 'NOT_APPLICABLE' and (required or not isinstance(entry.get('reason'),str) or not entry['reason'].strip()):
            raise ValueError(f'{gate_id} cannot be marked not applicable without a valid reason and optional status')
        if outcome == 'WAIVED':
            w = entry.get('waiver', {})
            if not isinstance(w,dict) or not all(isinstance(w.get(k),str) and w[k].strip() for k in ('reason','approver','scope','expires')):
                raise ValueError(f'{gate_id} waiver requires reason, approver, scope and expiry')
            try: expiry = date.fromisoformat(w['expires'])
            except ValueError: raise ValueError(f'{gate_id} waiver expiry must be an ISO date') from None
            if w['approver'] not in p['security']['authorized_waiver_approvers'] or w['scope'] != gate_id or expiry < now:
                raise ValueError(f'{gate_id} waiver is unauthorized, out of scope, or expired')
        evaluated.append({'id':gate_id,'name':gate['name'],'required':required,'outcome':outcome,'evidence':entry.get('evidence'), 'method':entry.get('method'), 'reviewer':entry.get('reviewer'), 'skill':entry.get('skill'), 'execution_evidence':entry.get('execution_evidence'), 'evidence_assurance': 'SELF_ATTESTED' if outcome in ('PASS', 'FAIL', 'WAIVED') else 'NOT_CLAIMED', 'reason':entry.get('reason'), 'waiver':entry.get('waiver'), 'blocked':outcome == 'FAIL' or (required and outcome == 'NOT_RUN')})
    critical = []
    seen = set()
    for f in findings:
        if not isinstance(f,dict) or not all(isinstance(f.get(k),str) and f[k].strip() for k in ('id','severity','status','evidence')):
            raise ValueError('Each finding needs id, severity, status and evidence')
        if f['id'] in seen or f['severity'] not in RANK or f['status'] not in ('open','resolved'):
            raise ValueError('Invalid or duplicate finding')
        seen.add(f['id'])
        if f['severity']=='critical' and f['status']=='open': critical.append(f['id'])
    # Critical exceptions are deliberately unsupported until an actual exception policy is implemented.
    blocked = any(x['blocked'] for x in evaluated) or bool(critical)
    return {'risk':risk,'stage':stage,'profile':profile,'canonical_profile_gates':canonical_profile_gates(profile),'canonical_profile_gates_enforced':False,'release_authorized':False,'independent_verification':'NOT_VERIFIED','gates':evaluated,'open_critical_findings':critical,'findings':findings,'blocked':blocked,'decision':'BLOCKED' if blocked else 'REVIEW_REQUIRED','note':'Evidence and reviewer identities are supplied records, not verified signatures; no deployment is authorized.'}
