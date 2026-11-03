import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from orchestration import core

ROOT = Path(__file__).resolve().parent.parent


def invoke(*args):
    return subprocess.run([sys.executable, '-B', '-m', 'orchestration', *map(str, args)], cwd=ROOT, text=True, capture_output=True)


class Phase21Tests(unittest.TestCase):
    def test_new_local_toolkit_registration_does_not_change_engine_or_gates(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            dummy = tmp / 'dummy'
            dummy.mkdir()
            (dummy / 'SKILL.md').write_text('Local dummy fixture; never executed.')
            config = json.loads((ROOT / 'standards/orchestration.yaml').read_text())
            entry = copy.deepcopy(config['skills']['impeccable'])
            entry.update(provider='local-test', source='https://example.invalid/dummy', capabilities=['dummy-capability'], enabled=True, approved_commit='a' * 40, approved_tree_sha256=core.tree_hash(dummy), supported_hosts={'codex': 'verified', 'claude': 'unsupported'})
            config['skills']['dummy-toolkit'] = entry
            config['routes']['dummy-task'] = {'primary': 'dummy-toolkit', 'secondary': [], 'security_stage': 'requirements', 'capability': 'dummy-capability'}
            review = {'source': entry['source'], 'reviewer': 'fixture reviewer', 'approval': 'fixture approval'}
            review.update({key: True for key in core.REVIEW_FIELDS})
            inventory = {'schema_version': 1, 'skills': {'dummy-toolkit': {'path': str(dummy), 'entrypoint': 'SKILL.md', 'installation_evidence': 'fixture', 'observed_commit': 'a' * 40, 'review': review, 'host_evidence': {'codex': {'invocation_evidence': 'fixture'}}}}}
            config_path, inventory_path = tmp / 'config.json', tmp / 'inventory.json'
            config_path.write_text(json.dumps(config)); inventory_path.write_text(json.dumps(inventory))
            args = ('--config', config_path, 'route', '--intent', 'dummy-task', '--risk', 'high', '--host', 'codex', '--inventory', inventory_path)
            result = invoke(*args)
            self.assertEqual(result.returncode, 0, result.stderr)
            route = json.loads(result.stdout)
            self.assertEqual(route['primary']['id'], 'dummy-toolkit')
            self.assertTrue(route['primary']['available'])
            self.assertEqual(route['primary']['compatibility_assurance'], 'SELF_ATTESTED')
            self.assertIsNone(route['primary']['executed'])
            self.assertEqual(route['security_stage'], 'requirements')
            no_evidence = tmp / 'evidence.json'; no_evidence.write_text('{"schema_version":1,"gates":{}}')
            blocked = invoke('--config', config_path, 'evaluate', '--stage', 'requirements', '--risk', 'high', '--evidence', no_evidence)
            self.assertEqual(blocked.returncode, 1)
            config['routes']['dummy-task']['capability'] = 'unsupported-capability'
            config_path.write_text(json.dumps(config))
            mismatch = invoke(*args)
            self.assertEqual(mismatch.returncode, 2)
            self.assertIn('capability', mismatch.stderr.lower())
            config['routes']['dummy-task']['capability'] = 'dummy-capability'
            config['skills']['dummy-toolkit']['enabled'] = False
            config_path.write_text(json.dumps(config))
            disabled = invoke(*args)
            self.assertEqual(disabled.returncode, 1)
            self.assertFalse(json.loads(disabled.stdout)['primary']['available'])
            config['skills']['dummy-toolkit']['enabled'] = True
            config_path.write_text(json.dumps(config))
            incompatible = invoke('--config', config_path, 'route', '--intent', 'dummy-task', '--risk', 'high', '--host', 'claude', '--inventory', inventory_path)
            self.assertEqual(incompatible.returncode, 1)
            unsupported = json.loads(incompatible.stdout)['primary']
            self.assertFalse(unsupported['compatible'])
            self.assertEqual(unsupported['compatibility_assurance'], 'NOT_VERIFIED')
            (dummy / 'SKILL.md').unlink()
            missing = invoke(*args)
            self.assertEqual(missing.returncode, 1)
            self.assertFalse(json.loads(missing.stdout)['primary']['available'])

    def test_canonical_roles_and_profile_gates_remain_authoritative(self):
        expected = {'discovery': 'gstack', 'implementation': 'superpowers', 'ui-design': 'ui-ux-pro-max', 'design-critique': 'impeccable'}
        registry = json.loads((ROOT / 'standards/orchestration.yaml').read_text())
        for intent, primary in expected.items():
            self.assertEqual(registry['routes'][intent]['primary'], primary)
        canonical = json.loads((ROOT / 'standards/quality-gates.yaml').read_text())
        with tempfile.TemporaryDirectory() as tmp:
            evidence = Path(tmp) / 'empty.json'
            evidence.write_text('{"schema_version":1,"gates":{}}')
            for profile in ('lean', 'standard', 'business-critical'):
                result = invoke('evaluate', '--stage', 'release', '--risk', 'high', '--profile', profile, '--evidence', evidence)
                self.assertEqual(result.returncode, 1)
                outcome = json.loads(result.stdout)
                self.assertEqual(outcome['canonical_profile_gates'], canonical['profiles'][profile])
                self.assertFalse(outcome['canonical_profile_gates_enforced'])
                self.assertFalse(outcome['release_authorized'])

    def test_normalized_cli_outputs_match_for_hosts_in_both_scenarios(self):
        for intent, risk, expected in [('documentation-audit', 'low', 0), ('implementation', 'high', 1)]:
            outputs = []
            for host in ('codex', 'claude'):
                result = invoke('route', '--intent', intent, '--risk', risk, '--host', host)
                self.assertEqual(result.returncode, expected, result.stderr)
                outputs.append(json.loads(result.stdout))
            self.assertEqual(outputs[0], outputs[1])

    def test_critical_finding_blocks_even_with_valid_gate_waiver(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            config = json.loads((ROOT / 'standards/orchestration.yaml').read_text())
            config['security']['authorized_waiver_approvers'] = ['owner']
            config_path = tmp / 'config.json'; config_path.write_text(json.dumps(config))
            evidence_path = tmp / 'evidence.json'
            evidence_path.write_text(json.dumps({'schema_version': 1, 'gates': {'S1': {'outcome': 'WAIVED', 'waiver': {'reason': 'exception', 'approver': 'owner', 'scope': 'S1', 'expires': '2099-01-01'}}}, 'findings': [{'id': 'RSK-1', 'severity': 'critical', 'status': 'open', 'evidence': 'finding-1'}]}))
            result = invoke('--config', config_path, 'evaluate', '--stage', 'requirements', '--risk', 'high', '--evidence', evidence_path)
            self.assertEqual(result.returncode, 1)
            decision = json.loads(result.stdout)
            self.assertEqual(decision['gates'][0]['outcome'], 'WAIVED')
            self.assertEqual(decision['open_critical_findings'], ['RSK-1'])
            self.assertFalse(decision['release_authorized'])

    def test_required_capability_blocks_even_if_omitted_from_route(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            config = json.loads((ROOT / 'standards/orchestration.yaml').read_text())
            config['skills']['secure-engineering']['supported_hosts']['codex'] = 'verified'
            config['routes']['security-review']['secondary'].remove('differential-review')
            inventory = {'schema_version': 1, 'skills': {'secure-engineering': {'installation_evidence': 'fixture', 'host_evidence': {'codex': {'invocation_evidence': 'fixture'}}}}}
            config_path, inventory_path = tmp / 'config.json', tmp / 'inventory.json'
            config_path.write_text(json.dumps(config)); inventory_path.write_text(json.dumps(inventory))
            result = invoke('--config', config_path, 'route', '--intent', 'security-review', '--risk', 'high', '--host', 'codex', '--inventory', inventory_path)
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertIn('differential-review', json.loads(result.stdout)['required_capabilities_missing'])

    def test_unavailable_secure_engineering_blocks_high_risk_implementation(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp); dummy = tmp / 'methodology'; dummy.mkdir()
            (dummy / 'SKILL.md').write_text('Local fixture')
            config = json.loads((ROOT / 'standards/orchestration.yaml').read_text())
            skill = config['skills']['superpowers']
            skill['approved_commit'] = 'a' * 40
            skill['approved_tree_sha256'] = core.tree_hash(dummy)
            skill['supported_hosts']['codex'] = 'verified'
            review = {'source': skill['source'], 'reviewer': 'fixture', 'approval': 'fixture'}
            review.update({key: True for key in core.REVIEW_FIELDS})
            inventory = {'schema_version': 1, 'skills': {'superpowers': {'path': str(dummy), 'entrypoint': 'SKILL.md', 'installation_evidence': 'fixture', 'observed_commit': 'a' * 40, 'review': review, 'host_evidence': {'codex': {'invocation_evidence': 'fixture'}}}}}
            config_path, inventory_path = tmp / 'config.json', tmp / 'inventory.json'
            config_path.write_text(json.dumps(config)); inventory_path.write_text(json.dumps(inventory))
            result = invoke('--config', config_path, 'route', '--intent', 'implementation', '--risk', 'high', '--host', 'codex', '--inventory', inventory_path)
            self.assertEqual(result.returncode, 1, result.stderr)
            outcome = json.loads(result.stdout)
            self.assertTrue(outcome['primary']['available'])
            self.assertIn('secure-engineering', outcome['required_capabilities_missing'])

    def test_skill_gate_evidence_must_match_gate_capability(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            config = json.loads((ROOT / 'standards/orchestration.yaml').read_text())
            inventory = {'schema_version': 1, 'skills': {}}
            for name in ('gstack', 'static-analysis'):
                directory = tmp / name; directory.mkdir()
                (directory / 'SKILL.md').write_text('Local fixture')
                skill = config['skills'][name]
                skill['approved_commit'] = 'a' * 40
                skill['approved_tree_sha256'] = core.tree_hash(directory)
                skill['supported_hosts']['codex'] = 'verified'
                review = {'source': skill['source'], 'reviewer': 'fixture', 'approval': 'fixture'}
                review.update({key: True for key in core.REVIEW_FIELDS})
                inventory['skills'][name] = {'path': str(directory), 'entrypoint': 'SKILL.md', 'installation_evidence': 'fixture', 'observed_commit': 'a' * 40, 'review': review, 'host_evidence': {'codex': {'invocation_evidence': 'fixture'}}}
            config_path, inventory_path, evidence_path = tmp / 'config.json', tmp / 'inventory.json', tmp / 'evidence.json'
            config_path.write_text(json.dumps(config)); inventory_path.write_text(json.dumps(inventory))
            gate = {'outcome': 'PASS', 'method': 'skill', 'skill': 'gstack', 'evidence': 'fixture', 'execution_evidence': 'fixture'}
            evidence_path.write_text(json.dumps({'schema_version': 1, 'gates': {'S4': gate}}))
            args = ('--config', config_path, 'evaluate', '--stage', 'testing', '--risk', 'high', '--host', 'codex', '--inventory', inventory_path, '--evidence', evidence_path)
            wrong = invoke(*args)
            self.assertEqual(wrong.returncode, 2)
            self.assertIn('capability', wrong.stderr.lower())
            gate['skill'] = 'static-analysis'
            evidence_path.write_text(json.dumps({'schema_version': 1, 'gates': {'S4': gate}}))
            correct = invoke(*args)
            self.assertEqual(correct.returncode, 0, correct.stderr)
            self.assertEqual(json.loads(correct.stdout)['gates'][0]['outcome'], 'PASS')
            gate = {'outcome': 'PASS', 'method': 'manual', 'reviewer': 'fixture', 'evidence': 'fixture'}
            evidence_path.write_text(json.dumps({'schema_version': 1, 'gates': {'S4': gate}}))
            manual = invoke(*args)
            self.assertEqual(manual.returncode, 0, manual.stderr)
            self.assertFalse(json.loads(manual.stdout)['release_authorized'])

    def test_legacy_config_without_gate_capabilities_preserves_manual_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            config = json.loads((ROOT / 'standards/orchestration.yaml').read_text())
            for gate in config['security']['gates'].values():
                gate.pop('accepted_skill_capabilities')
            config_path = tmp / 'config.json'; config_path.write_text(json.dumps(config))
            evidence = tmp / 'evidence.json'
            evidence.write_text(json.dumps({'schema_version': 1, 'gates': {'S4': {'outcome': 'PASS', 'method': 'manual', 'reviewer': 'fixture', 'evidence': 'fixture'}}}))
            result = invoke('--config', config_path, 'evaluate', '--stage', 'testing', '--risk', 'high', '--evidence', evidence)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)['gates'][0]['outcome'], 'PASS')
            evidence.write_text(json.dumps({'schema_version': 1, 'gates': {'S4': {'outcome': 'PASS', 'method': 'skill', 'skill': 'static-analysis', 'evidence': 'fixture', 'execution_evidence': 'fixture'}}}))
            result = invoke('--config', config_path, 'evaluate', '--stage', 'testing', '--risk', 'high', '--host', 'codex', '--evidence', evidence)
            self.assertEqual(result.returncode, 2)
            self.assertIn('capabilit', result.stderr.lower())

    def test_unknown_required_intent_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            config = json.loads((ROOT / 'standards/orchestration.yaml').read_text())
            config['skills']['secure-engineering']['required_for']['intents'].append('implementaton')
            path = Path(tmp) / 'config.json'; path.write_text(json.dumps(config))
            result = invoke('--config', path, 'route', '--intent', 'implementation', '--risk', 'high', '--host', 'codex')
            self.assertEqual(result.returncode, 2)
            self.assertIn('required', result.stderr.lower())

    def test_unknown_risk_requires_owner_review_and_is_machine_readable(self):
        result = invoke('risk', '--factors', '{}', '--profile', 'business-critical')
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(data['level'], 'high')
        self.assertTrue(data['unknown_factors'])
        self.assertIs(data['requires_owner_review'], True)

    def test_manual_passing_evidence_is_explicitly_self_attested_and_never_authorizes_release(self):
        with tempfile.TemporaryDirectory() as tmp:
            evidence = Path(tmp) / 'evidence.json'
            evidence.write_text(json.dumps({'schema_version': 1, 'gates': {'S1': {'outcome': 'PASS', 'method': 'manual', 'reviewer': 'owner', 'evidence': 'record-1'}}}))
            result = invoke('evaluate', '--stage', 'requirements', '--risk', 'low', '--profile', 'lean', '--evidence', evidence)
            self.assertEqual(result.returncode, 0, result.stderr)
            decision = json.loads(result.stdout)
            self.assertEqual(decision['decision'], 'REVIEW_REQUIRED')
            self.assertIs(decision['release_authorized'], False)
            self.assertIs(decision['canonical_profile_gates_enforced'], False)
            self.assertEqual(decision['gates'][0]['evidence_assurance'], 'SELF_ATTESTED')
            self.assertEqual(decision['independent_verification'], 'NOT_VERIFIED')
            self.assertEqual(decision['canonical_profile_gates']['security'], 'Secrets, input and authentication baseline')


if __name__ == '__main__':
    unittest.main()
