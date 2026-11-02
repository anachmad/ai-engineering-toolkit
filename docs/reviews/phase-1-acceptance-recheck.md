# Phase 1 acceptance recheck

Date: 2026-11-02
Decision: **Phase 1 sign-off approved by the user on 2026-11-02**, under the operating assumptions below.
This recheck follows the [independent acceptance report](phase-1-acceptance-report.md) and [remediation status](phase-1-remediation-status.md). It was performed in the same working session as the remediation, not by a separate independent reviewer; the original report remains unchanged.

## Accepted operating assumptions

On 2026-11-02 the user accepted these recommendations for Phase 1:

1. JSON-formatted YAML and the toolkit's documented schema vocabulary are sufficient; general YAML and arbitrary JSON Schema are not supported.
2. Initial internal use is limited to directories controlled by trusted users; the path checks do not claim protection against a concurrent hostile process replacing filesystem objects.
3. Each shared project owns a toolkit snapshot and reviews updates manually. Automated update management is deferred.

Acceptance of these assumptions is not approval to deploy a particular project or evidence that its gates have passed.

## Findings rechecked

| Finding | Result | Evidence / remaining limit |
| --- | --- | --- |
| M1: ancestor symlinks | **ACCEPTED WITH LIMIT** | The effective target is resolved and displayed; nested symlinks are rejected in generated paths. Regression tests pass. Protection from concurrent hostile changes is outside the agreed trust model, not a verified guarantee. |
| M2: non-file collision | **PASS** | A directory at an expected file path returns a nonzero result before planned writes; regression test passes. A conflict introduced after preflight may leave earlier created files and is reported. |
| M3: UI applicability update | **PASS** | `set-ui` previews the change; application requires an explicit flag and reviewed manifest SHA-256. Tests cover stale hashes, preservation, repeat use, no, yes, and interrupted manifest replacement. A newly created UI draft can remain after a later failure. |
| M4: schemas and standards location | **ACCEPTED WITH LIMIT** | Versioned machine-readable contracts cover manifest fields and policy top-level fields; Python checks deeper policy constraints. Missing or different standards locations are rejected. The agreed schema scope is limited to the documented vocabulary. |
| m1: host audit and refresh | **PASS WITH LIMIT** | Prior separate Codex and Claude checks identified conflicting approved and draft fixture documents, required authorized review, and produced answer-only unified diff proposals when explicitly requested. Approved fixture hashes remained unchanged. This samples host behavior, not technical enforcement. Claude's first plan-mode run created a user-level plan file; see the remediation status report. |
| m2: project-copy drift | **ACCEPTED WITH LIMIT** | `provenance.json` records hashes of the copied bytes. There is no automatic drift check or update process, consistent with the agreed manual-update model. |
| m3–m4: documentation and tests | **PASS** | The path-safety boundary is documented; regression tests exercise the identified cases. |

## Exit criteria

- **AC-01 / AC-02:** Lean and Standard initialization generate configured draft documents and manifests without fabricating business requirements. Automated tests and fresh temporary examples passed.
- **AC-03:** Business Critical scaffolding introduces traceability, threat-model, review, access and recovery prompts and the canonical quality-gate descriptions. These are drafts and requirements, not completed evidence or release enforcement.
- **AC-04:** Existing approved fixture documents were preserved in all three profile tests; separate host exercises reported conflicting content and the need for authorized review. Automated audit alone checks file presence, not substantive compliance.
- **AC-07:** Codex and Claude Code were separately invoked in earlier acceptance and remediation checks. Both resolved their adapters to the same shared playbook and standards. Host behavior is observed in this Linux environment, not a cross-platform guarantee.

AC-05 and AC-06 are Phase 2. AC-08 through AC-11 are Phase 3. AC-12 and enforced release gates are Phase 4. They were not accepted or implemented here.

## Commands and results

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v` — **28 tests passed**, Python 3.14.4, Linux.
- A temporary-directory Python harness called `python3 -B -m playbook init`, `audit`, `set-ui` preview, `set-ui --apply --expected-sha256 <reviewed-hash>`, and `audit` for each of `lean`, `standard`, and `business-critical`. Every command returned 0; a pre-existing approved architecture fixture remained SHA-256 identical for every profile. No real project was modified.
- `git diff --check` — exit 0.
- Prior separate host commands, fixture hashes, and the Claude plan-file side effect are recorded in [remediation status](phase-1-remediation-status.md).

## Residual limitations and handoff

No macOS, Windows, WSL, hostile concurrent filesystem, CI release enforcement, or complete third-party lifecycle test was performed. The CLI audit checks presence and warns that content, approvals, and evidence need human review. Project copies can diverge. User-level skill links were added earlier with explicit user approval; the first Claude plan-mode verification wrote a user-level plan file, also recorded in the remediation status. No global setting was changed as part of this recheck.

The Filio pilot's existing manifest and project-owned toolkit snapshot were not updated during remediation or this recheck. Its project requirements, approvals, UI applicability and Business Critical evidence still require owner review. Those pilot gaps are not proof of toolkit or release compliance.

The user approved Phase 1 sign-off and requested commit and push on 2026-11-02. The user did not supply an individual name or role for the record. Phase 2 routing is not implemented by this sign-off. Record the resulting commit as the reviewed baseline when assessing subsequent work.
