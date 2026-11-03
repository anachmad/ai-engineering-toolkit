# Phase 2 acceptance report

Status: draft

Historical note: see [Phase 2 review fixes](phase-2-review-fixes.md) for subsequent routing and gate remediations.

Acceptance outcome: **PARTIAL — not ready to declare technically complete**.
Baseline: signed-off Phase 1 at commit `11ed547` plus the current Phase 2 working tree. This is an implementation acceptance record, not a release authorization or an independently signed security assessment.

## Gap analysis and implementation

Phase 1 provided documentation standards, three profiles, templates, shared host adapters, and a standard-library scaffolder. It did not provide a capability registry, router, security lifecycle skill, security risk classifier, or evidence gate evaluator. Phase 2 adds `standards/orchestration.yaml`, the `orchestration` CLI and policy engine, shared `secure-engineering` and `engineering-workflow-router` skills, thin host adapters, and tests. Existing profile and gate standards are reused. Phase 1's `share` now includes the orchestrator and both new skill links in new project-owned copies; existing project copies are unchanged.

The implementation chooses a **non-executing** adapter boundary: configuration and reviewed inventory are interpreted locally; no external source is installed, invoked, or updated automatically. Registry entries for external skills are initially unapproved, unpinned and host-unverified. A user can register, enable, disable, or replace entries in reviewed configuration. Installation and updates require a separately reviewed native host process; no lifecycle manager is claimed.

## Acceptance criteria

| Criterion | Status | Evidence / limitation |
| --- | --- | --- |
| Existing Phase 1 behavior remains functional | **PASS, tested scenarios** | `python3 -m unittest discover -s tests -v`: Phase 1 tests and shared-project move/conflict tests pass with the new files. No claim for untested host versions or other operating systems. |
| Skills registered and discovered through configuration | **PASS** | `registry`, `status`, registry modification tests in `tests/test_orchestration.py`; enabled does not imply installed or discoverable by a host. |
| Enable and disable independently | **PASS for routing configuration** | Registry test toggles an entry; actual host auto-selection or uninstallation is not controlled by this configuration. Mandatory internal security policy cannot be disabled. |
| Routing consistent | **PASS for declared intents** | Deterministic config, one primary per route; tests assert Superpowers for implementation and Impeccable for critique. |
| Missing optional skills handled gracefully | **PASS** | Missing low-risk primary yields manual fallback; missing optional secondary appears unavailable; no installer or skill is invoked. |
| Missing mandatory capabilities prevent false acceptance | **PASS with boundary** | High/critical missing primary or configured mandatory secondary blocks; required gate `NOT_RUN` blocks; task-specific skill evidence must reference an available attested skill. Attestations are not cryptographically verified. |
| Secure Engineering across lifecycle | **PASS for guidance and routing** | Shared skill covers discovery through maintenance; routes point to lifecycle stages. This is a policy/instruction capability, not proof that an agent followed every instruction. |
| Operational security risk classification | **PASS with owner assessment** | Boolean risk factors map to configurable levels and supplied profiles impose risk floors; unknown factors are listed. Risk, factors, and profile remain operator-supplied rather than automatically read from a manifest. |
| Explicit security gate outcomes | **PASS with boundary** | S1–S5 support `PASS`, `FAIL`, `NOT_APPLICABLE`, `NOT_RUN`, `WAIVED`; missing required evidence and open critical findings block. A nonblocked result is `REVIEW_REQUIRED`, not release approval. |
| Third-party skill verification policy implemented | **PARTIAL** | Activation status requires pinned commit, matching local tree hash, review attestations, source, publisher review, approval and host evidence. Commit/publisher identity, review, actual host invocation and approval signatures are not independently verified. No installer or execution occurs. |
| Trail of Bits adapter capabilities correctly declared and validated | **PARTIAL** | Official upstream source inspected; registry tests assert identifiers. `static-analysis` is a plugin containing `codeql`, `semgrep`, and `sarif-parsing`, not a single skill. No reviewed pin or native execution exists. |
| Findings and waivers recorded and traced | **PARTIAL** | Versioned evidence JSON carries gate evidence, methods, reviewers, scoped waiver/expiry, finding IDs and evidence references. The evaluator returns those records but does not validate artifact contents, signatures, or persist them automatically. |
| Documentation remains consistent with Phase 1 | **PASS with boundary** | Existing docs remain source of truth; security guidance links requirements, design, tests and evidence rather than creating mandatory extra documents. |
| Codex compatibility | **PASS for native skill discovery smoke test** | Separate disposable project, Codex CLI 0.166.0: loaded both project-local adapters and shared definitions; router CLI was exercised. External plugins remain unverified. |
| Claude Code compatibility | **PARTIAL** | Disposable project: Claude read both adapters and shared definitions; later `readlink -f` checks resolved each adapter. No full Claude-driven routing/gate workflow or external plugin execution was verified. |
| Expected and failure-path automated tests | **PASS for covered cases** | Routing, configuration, absent skills, hash mismatch, symlinks, risk, `NOT_RUN`, missing evidence, waivers, critical findings, and Phase 1 regression are tested. Host and third-party behaviors are not exhaustively automated. |
| Acceptance report has actual evidence | **PASS** | Commands and results below distinguish observed behavior from attestations and proposed future work. |

## Verification evidence

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v`: **45 tests passed** on Linux/Python 3.14.4 at the time of this report, including 17 orchestration tests and the 28 Phase 1 tests.
- `python3 -m orchestration risk --factors '{"data_sensitivity":true,"internet_exposure":true}'`: returned `high` with omitted factors listed as unknown.
- `python3 -m orchestration evaluate --stage release --risk high --evidence examples/security-evidence.json`: returned exit **1**, decision `BLOCKED`, five required gates `NOT_RUN`. This was an expected negative test.
- `python3 -m orchestration route --intent implementation --risk high --host codex`: returned exit **1**, recommended Superpowers but reported it unavailable and blocked the high-risk route.
- Skill-creator `quick_validate.py` passed for both shared native skill directories; it validates structure, not host behavior or security quality.
- Codex: `codex exec --ephemeral --sandbox read-only --skip-git-repo-check` in a temporary project with local skill links; it resolved both adapters and definitions, read policy, and ran a route. Exit 0.
- Claude Code: `claude -p` in the same temporary project, `--permission-mode dontAsk --no-session-persistence --add-dir <toolkit>`; it read both adapters and definitions. Separate read-only runs with `readlink` permission resolved each adapter. No full host-driven gate execution was verified. Exit 0.
- Host commands ran outside the command sandbox with explicit approval to accommodate local host runtime restrictions; no external integration was installed. No production changes were performed.

## Security references and integration verification

- Official [Trail of Bits marketplace](https://github.com/trailofbits/skills) identifies the candidate plugins and describes Claude Code and Codex marketplace methods. Official [static-analysis](https://github.com/trailofbits/skills/tree/main/plugins/static-analysis) distinguishes its component skills. Official [supply-chain-risk-auditor](https://github.com/trailofbits/skills/blob/main/plugins/supply-chain-risk-auditor/README.md) specifies `uv` and network/cache considerations. These sources were inspected on 2026-11-02; executable components, licensing approval, current immutable commits, and host execution were **not** reviewed or approved.
- The native skill points to [OWASP ASVS](https://asvs.owasp.org/) and the [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/); the user must select relevant controls and record versioned references and evidence.

## Known limitations and Phase 3 recommendations

1. Implement reviewed lifecycle operations, approved immutable pin verification against the actual source, installation planning, backups, update and rollback. Never execute unreviewed installers or silently alter hooks/settings.
2. Add trusted, authenticated identity and evidence verification if gate decisions will be used beyond local decision support. Current reviewer names, refs, commit and host checks are attestations and can be fabricated by an operator. Enforce critical gates in CI with authorized human release approval.
3. Verify external plugin discovery, invocation, permissions, dependencies, and execution independently in each host. Validate Claude's complete routing and gate workflow; record absent or unsupported capabilities rather than declaring success.
4. Assess manual fallbacks, test expiry and exception policy against organizational approval rules, and implement cryptographically or otherwise independently verifiable audit evidence as needed. Critical finding exceptions are currently unsupported and always block.
5. Add runtime risk-context binding, richer project-specific policy validation, portable project-copy version/update handling, and cross-platform tests after those requirements are approved. Unknown risk factors require owner review.
6. The accepted Phase 1 filesystem trust model applies: concurrent hostile filesystem mutation is out of scope. macOS and Windows/WSL are unverified in this implementation.
