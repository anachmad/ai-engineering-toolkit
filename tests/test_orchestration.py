import copy
from datetime import date
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from orchestration import core

ROOT = Path(__file__).resolve().parent.parent


class OrchestrationTests(unittest.TestCase):
    def setUp(self): self.p = core.policy()

    def test_routes_have_one_primary_and_expected_owners(self):
        for name, owner in [('implementation','superpowers'),('design-critique','impeccable'),('security-review','secure-engineering')]:
            result = core.route(self.p, name, 'codex', {}, 'high')
            self.assertEqual(result['primary']['id'], owner)
            self.assertTrue(result['blocked'])
            self.assertFalse(result['primary']['available'])

    def test_missing_optional_and_risk_fallback(self):
        result = core.route(self.p, 'implementation', 'claude', {}, 'low')
        self.assertFalse(result['blocked'])
        self.assertIn('manual', result['fallback'])
        status = core.status(self.p, 'impeccable', 'codex', {})
        self.assertFalse(status['installed'])
        self.assertFalse(status['executed'])

    def test_enable_disable_and_new_registration(self):
        p = copy.deepcopy(self.p)
        p['skills']['impeccable']['enabled'] = False
        self.assertFalse(core.status(p, 'impeccable', 'codex', {})['enabled'])
        p['skills']['replacement'] = copy.deepcopy(p['skills']['impeccable'])
        p['skills']['replacement']['enabled'] = True
        p['routes']['design-critique']['primary'] = 'replacement'
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'policy.json'; path.write_text(json.dumps(p))
            loaded = core.policy(path)
            self.assertEqual(core.route(loaded, 'design-critique', 'codex', {}, 'low')['primary']['id'], 'replacement')

    def test_risk_escalation_and_unknowns(self):
        result = core.classify(self.p, {'data_sensitivity':True,'high_business_impact':True})
        self.assertEqual(result['level'], 'critical')
        self.assertIn('internet_exposure', result['unknown_factors'])
        with self.assertRaises(ValueError): core.classify(self.p, {'data_sensitivity':'yes'})
        with self.assertRaises(ValueError): core.classify(self.p, {'bogus':True})

    def test_configured_is_not_installed_or_available(self):
        with tempfile.TemporaryDirectory() as tmp:
            item = core.status(self.p, 'differential-review', 'codex', {'differential-review':{'path':tmp}})
            self.assertTrue(item['files_present'])
            self.assertFalse(item['installed'])
            self.assertFalse(item['loadable'])
            self.assertFalse(item['available'])
            self.assertFalse(item['compatible'])

    def test_review_pin_hash_and_host_evidence_required(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); (root/'SKILL.md').write_text('Reviewed content')
            p = copy.deepcopy(self.p); skill = p['skills']['differential-review']
            skill['approved_commit'] = 'a'*40; skill['approved_tree_sha256'] = core.tree_hash(root)
            skill['supported_hosts']['codex'] = 'verified'
            review = {'source':skill['source'],'reviewer':'security-owner','approval':'MR-123'}
            review.update({x:True for x in core.REVIEW_FIELDS})
            inv = {'differential-review':{'path':tmp,'entrypoint':'SKILL.md','installation_evidence':'install record','observed_commit':'a'*40,'review':review,'host_evidence':{'codex':{'invocation_evidence':'MR-124'}}}}
            result = core.status(p, 'differential-review', 'codex', inv)
            self.assertTrue(result['available'])
            self.assertFalse(result['executed'])
            self.assertFalse(core.status(p, 'differential-review', 'claude', inv)['available'])
            (root/'SKILL.md').write_text('Changed')
            self.assertFalse(core.status(p, 'differential-review', 'codex', inv)['available'])
            (root/'link').symlink_to('/tmp')
            with self.assertRaises(ValueError): core.status(p, 'differential-review', 'codex', inv)

    def test_missing_evidence_and_critical_finding_block_release(self):
        result = core.evaluate(self.p, 'high', 'release', {})
        self.assertTrue(result['blocked'])
        self.assertTrue(all(g['outcome']=='NOT_RUN' for g in result['gates']))
        evidence = {'gates':{k:{'outcome':'PASS','evidence':'CI-123','method':'manual','reviewer':'security-owner'} for k in self.p['security']['gates']}, 'findings':[{'id':'RSK-1','severity':'critical','status':'open','evidence':'issue-123'}]}
        self.assertTrue(core.evaluate(self.p, 'high', 'release', evidence)['blocked'])
        evidence['findings'][0]['status']='resolved'
        final = core.evaluate(self.p, 'high', 'release', evidence)
        self.assertFalse(final['blocked'])
        self.assertEqual(final['decision'], 'REVIEW_REQUIRED')

    def test_rejects_missing_evidence_unauthorized_expired_or_wrong_waiver(self):
        with self.assertRaises(ValueError): core.evaluate(self.p, 'high', 'release', {'gates':{'S1':{'outcome':'PASS'}}})
        with self.assertRaises(ValueError): core.evaluate(self.p, 'high', 'release', {'gates':{'S1':{'outcome':'NOT_APPLICABLE','reason':'not needed'}}})
        waiver={'reason':'pending','approver':'owner','scope':'S1','expires':'2027-01-01'}
        item={'gates':{'S1':{'outcome':'WAIVED','waiver':waiver}}}
        with self.assertRaises(ValueError): core.evaluate(self.p,'high','release',item,today=date(2026,11,2))
        p=copy.deepcopy(self.p);p['security']['authorized_waiver_approvers']=['owner']
        self.assertEqual(core.evaluate(p,'high','release',item,today=date(2026,11,2))['gates'][0]['outcome'],'WAIVED')
        waiver['scope']='S2'
        with self.assertRaises(ValueError): core.evaluate(p,'high','release',item,today=date(2026,11,2))
        waiver['scope']='S1'; waiver['expires']='2025-01-01'
        with self.assertRaises(ValueError): core.evaluate(p,'high','release',item,today=date(2026,11,2))

    def test_unavailable_skill_cannot_supply_passing_gate(self):
        item={'gates':{'S4':{'outcome':'PASS','evidence':'scan.json','method':'skill','skill':'static-analysis','execution_evidence':'run-123'}}}
        with self.assertRaises(ValueError):
            core.evaluate(self.p,'high','testing',item,host='codex',inventory={})

    def test_manual_evidence_needs_named_reviewer(self):
        item={'gates':{'S1':{'outcome':'PASS','evidence':'report.md','method':'manual'}}}
        with self.assertRaises(ValueError): core.evaluate(self.p,'high','requirements',item)

    def test_trail_of_bits_adapters_declare_actual_plugin_and_skills(self):
        expected={'differential-review':['differential-review'],'static-analysis':['codeql','semgrep','sarif-parsing'],'supply-chain-risk-auditor':['supply-chain-risk-auditor']}
        for key, identifiers in expected.items():
            skill=self.p['skills'][key]
            self.assertEqual(skill['source'], 'https://github.com/trailofbits/skills')
            self.assertEqual(skill['native_identifiers'], identifiers)
            self.assertIsNone(skill['approved_commit'])
            self.assertEqual(skill['supported_hosts']['codex'], 'unverified')
        self.assertEqual(self.p['skills']['static-analysis']['kind'], 'plugin')

    def test_optional_failure_still_blocks(self):
        p=copy.deepcopy(self.p)
        item={'gates':{'S3':{'outcome':'FAIL','evidence':'review-1','method':'manual','reviewer':'owner'}}}
        self.assertTrue(core.evaluate(p,'low','review',item)['blocked'])

    def test_business_critical_profile_enforces_risk_floor(self):
        result=core.route(self.p,'implementation','codex',{},'low','business-critical')
        self.assertEqual(result['risk'],'high')
        self.assertTrue(result['blocked'])
        result=core.classify(self.p,{},'business-critical')
        self.assertEqual(result['level'],'high')
        result=core.evaluate(self.p,'low','release',{},profile='business-critical')
        self.assertEqual(result['risk'],'high')
        self.assertTrue(result['blocked'])

    def test_invalid_host_or_intent_are_rejected(self):
        with self.assertRaises(ValueError): core.route(self.p,'invented','codex',{},'low')
        with self.assertRaises(ValueError): core.status(self.p,'impeccable','other',{})

    def test_external_tool_cannot_own_release_governance(self):
        p=copy.deepcopy(self.p)
        p['routes']['release']['primary']='impeccable'
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'policy.json';path.write_text(json.dumps(p))
            with self.assertRaises(ValueError): core.policy(path)

    def test_required_security_capability_blocks_even_when_primary_available(self):
        p=copy.deepcopy(self.p)
        p['skills']['secure-engineering']['supported_hosts']['codex']='verified'
        inv={'secure-engineering':{'installation_evidence':'install record','host_evidence':{'codex':{'invocation_evidence':'review record'}}}}
        result=core.route(p,'security-review','codex',inv,'critical')
        self.assertTrue(result['primary']['available'])
        self.assertIn('differential-review',result['required_capabilities_missing'])
        self.assertTrue(result['blocked'])

    def test_cli_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            f=Path(tmp)/'evidence.json'; f.write_text('{"schema_version":1,"gates":{}}')
            result=subprocess.run([sys.executable,'-m','orchestration','evaluate','--stage','release','--risk','critical','--evidence',str(f)],cwd=ROOT,text=True,capture_output=True)
            self.assertEqual(result.returncode,1,result.stderr)
            self.assertTrue(json.loads(result.stdout)['blocked'])


if __name__ == '__main__': unittest.main()
