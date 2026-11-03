# Documentation framework assessment and implementation proposal

Date: 2026-11-03. Status: implementation boundary for this change; proposed standards remain pending owner approval.

## Baseline and overlap

Phase 1 has an acceptance recheck and signed-off baseline. Phase 2 has a user sign-off record with accepted limitations in `docs/reviews/phase-2-signoff.md`; the code and report remain uncommitted. Phase 2's registry/router and S1–S5 evaluator remain authoritative for their existing roles. Its external-tool claims and evidence are self-attested, its canonical profile gates are not enforced by that evaluator, and release is not automatically authorized. Preserve the working tree.

The shared Playbook skill and thin host adapters reference the same policies; `profiles.yaml` defines `lean`, `standard`, `business-critical`, and artifacts; `quality-gates.yaml` describes existing governance gates. The BRD contract, template, and `playbook/brd.py` provide an approved structure and deterministic BRD checks. `init` preserves existing files. The general audit checks artifact presence rather than conformance. The BRD implementation and broader Phase 2 changes are uncommitted and must not be replaced.

## Gaps, changes and risks

A discoverable artifact registry, explicit contract version selection, structured validation results and document-level gate outcome are missing. BRD already checks relationships within its tables; project-wide relationships, impact analysis, immutable version archival, semantic review records, authenticated approvals, project gate enforcement and actual CI/host execution remain missing. Existing BRD v1 templates lack an embedded standard version; silently treating their document revision field as a standard version would be incorrect.

The requested PRD, SRS, SAD and supporting structures are proposals, not approved standards. The earlier 17-section PRD proposal differs from the current requested 20-section proposal; retain it as history, and identify the new proposal as current. Do not replace profile identifiers with Lite/Critical aliases without an approved mapping. Do not impose new mandatory artifacts or silently rewrite old BRDs.

## Incremental design

1. Record the user's current proposed structures separately and register them as pending; only BRD v1 is executable/approved.
2. Reuse `playbook.brd.validate` for a generic registry-driven noninteractive validation command. Require an explicit BRD standard version on that new command, report unknown versions and unsupported artifacts as errors, preserve `validate-brd` and existing scaffold behavior. This identifies which version was selected but does not embed or attest it in legacy documents.
3. Map validation findings to FAIL/WARN/PASS and a process exit code while reporting semantic review and human approval independently as NOT_RUN/NOT_VERIFIED. A structural WARN, including TBD, is not approval or release readiness. Do not change existing profile gates or security evaluator outcomes.
4. Test positive/negative cases and old behavior. Document gaps and verification evidence; defer cross-document enforcement and CI until their contracts, approval policy and platform are defined.

The registry is an index into existing definitions, not a second source of BRD rules. It does not make unapproved contracts enforceable. Independent external skills cannot modify validation outcomes through this CLI, but preventing a host or CI operator from skipping the command requires enforcement outside this repository and is not claimed here.
