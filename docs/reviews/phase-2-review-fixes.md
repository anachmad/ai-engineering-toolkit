# Phase 2 review fixes

Status: draft

This report follows the Phase 2 code review and preserves the earlier [Phase 2 acceptance](phase-2-acceptance-report.md) and [Phase 2.1 remediation](phase-2-remediation-report.md) reports as historical evidence. Recommendation: **ready for a fresh review**, not an automatic Phase 2 sign-off.

## Findings and changes

| Finding | Change | Verification |
| --- | --- | --- |
| Mandatory requirements could be bypassed by omitting a skill from `secondary` | `route()` checks all registry entries whose `required_for` intent and risk match, whether or not they appear in the selected route. Invalid or empty required-for mappings and unknown intent names fail policy validation. | A regression removes `differential-review` from the security-review secondary list and checks that a high-risk route is still blocked. |
| Secure Engineering was not mandatory for high-risk implementation | The Phase 2 orchestration policy requires `secure-engineering` for the configured security lifecycle intents at high and critical risk. Low and medium risk continue to use contextual security guidance and applicable security gates. | A synthetic attested Superpowers fixture is available, while Secure Engineering is unavailable; high-risk implementation remains blocked. |
| An unrelated skill could substantiate a security gate | Phase 2 security gates declare `accepted_skill_capabilities`. A tool-backed gate outcome must name an available skill that declares at least one accepted capability. Manual evidence retains its existing reviewer and evidence requirements. | An attested discovery-only fixture is rejected for S4; a static-analysis fixture and separately reviewed manual evidence are accepted as self-attestations. |
| New documents lacked required lifecycle status | The Phase 2 guide, acceptance report, remediation report and ADR now have `Status: draft`; acceptance outcome and proposed ADR decision remain distinct from lifecycle status. | Compared with `standards/documentation-standard.md`. |
| Existing Phase 2 configurations could lack the new capability mapping | Legacy configurations without `accepted_skill_capabilities` still load and can use manual evidence; tool-backed gate evidence fails closed until a mapping is configured. | Regression test checks both paths. This is a conservative behavior change for legacy tool-backed evidence and does not silently migrate configuration. |

The changes to `standards/orchestration.yaml` are **draft Phase 2 policy changes** requiring owner review: the high/critical Secure Engineering requirement and each gate's accepted capability metadata. The approved Phase 1 `standards/quality-gates.yaml` and `standards/documentation-standard.md` were not modified. The gate capability list is an eligibility check, not proof of tool execution or coverage; in particular, a single S4-capable tool does not automatically prove that both static analysis and dependency review were completed.

## Verification

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -q` — **56 tests passed** on Linux/Python 3.14.4.
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p test_phase21.py -q` — **11 tests passed**, including the new mandatory-registry, Secure Engineering, gate-capability, backward-compatibility, and unknown-required-intent checks.
- Regression tests were observed failing on the original reported behaviors before the fixes, and passing afterward. No approved project documents were modified by the tests.
- Codex and Claude Code independently ran the same positive and negative router/gate scenarios with synthetic evidence. Both hosts' four final JSON objects matched each other field-for-field; each also matched a fresh invocation of the final CLI. The negative implementation route reported missing `secure-engineering` and remained blocked; the release evidence with S1–S5 `NOT_RUN` remained blocked. The positive manual evidence remained `SELF_ATTESTED`, `REVIEW_REQUIRED`, and `release_authorized: false`.
- Host output: [Codex](evidence/phase-2-review-fixes/codex.json), [Claude](evidence/phase-2-review-fixes/claude.json); fixture inputs: [positive](evidence/phase-2-review-fixes/positive.json), [negative](evidence/phase-2-review-fixes/negative.json). These are model-produced JSON reproductions of tool results, not signed execution logs. Host processes used non-persistent sessions and session-only permissions; no third-party toolkit was installed or executed.
- `git diff --check` — exit 0 for tracked changes.

The hosts ran the same four commands documented in the earlier [parity report](phase-2-remediation-report.md#codex-versus-claude-parity), using the new synthetic evidence directory. A subsequent validation change rejects unknown `required_for` intents; a fresh direct run of all eight host-specific commands after that change matched the saved host outputs field-for-field.

## Remaining limitations

- Evidence, reviewer names, tool availability, host compatibility and execution are operator attestations, not independently verified identities, signatures, or evidence contents. `REVIEW_REQUIRED` is not release authorization.
- No external toolkit, CI release gate, or Phase 3 lifecycle manager was installed or verified. Linux host scenarios do not prove macOS or other-version compatibility.
- Phase 2 policy and the uncommitted working tree require engineering/security-owner review. Existing project-owned toolkit snapshots are unchanged and do not automatically receive these fixes.
- Capability eligibility does not prove that every control required by a gate was tested. Owners must evaluate the actual evidence and coverage.
