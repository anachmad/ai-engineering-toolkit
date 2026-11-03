# Phase 2.1 remediation and acceptance report

Status: draft

Historical note: this report records Phase 2.1 before the later review fixes. See [Phase 2 review fixes](phase-2-review-fixes.md) for subsequent evidence and current limitations.

Recommendation: **CONDITIONAL GO for the Phase 2.1 remediation**, pending engineering-owner review of [ADR-001](../adr/ADR-001-route-capability-binding.md) and the complete working-tree changes. This is not a claim that all external Phase 2 integrations are installed, independently verified, or approved. Phase 3 is not implemented here.

## Finding-to-fix traceability

| Finding | Change and evidence | Result |
| --- | --- | --- |
| REM-01: host-driven workflow | Both hosts discovered the router, read shared policy, ran the same positive and negative CLI scenarios, and reported the CLI output. Their complete returned JSON objects were compared to each other and to fresh direct CLI outputs. | **PASS for the tested scenarios**; see parity table and limitations below. |
| REM-02: dynamic registration | `tests/test_phase21.py` registers a new dummy capability, selects it, disables it, tests an incompatible host and missing entrypoint, and verifies a mandatory gate remains blocked. Optional capability binding is documented in ADR-001. | **PASS for a local synthetic configuration and self-attested fixture**; no external skill is installed or executed. |
| REM-03: security evidence boundaries | `evaluate` returns `evidence_assurance`, `independent_verification: NOT_VERIFIED`, and `release_authorized: false`; risk output contains `requires_owner_review`. Tests cover absent evidence, unauthorized/expired/out-of-scope waivers, critical findings, and unknown risks. | **PASS as a decision aid**; reviewer identity and artifacts are not independently verified. |
| REM-04: policy consistency | `quality-gates.yaml` remains the authority for Phase 1 profile gate descriptions. `policy()` checks that profile names agree with the canonical files; evaluation returns the selected profile's canonical descriptions and explicitly reports `canonical_profile_gates_enforced: false`. S1–S5 are supplementary checks. | **PASS for tested descriptions and routes**; canonical profile gates are not executable enforcement and approved standards were not modified. |
| REM-05: regression and acceptance | Full test suite, host scenarios, configuration and negative-path checks listed below. | **PASS for tested cases**, with environmental and trust limits below. |

## Files changed in this remediation

- `orchestration/core.py`: optional route-capability validation; profile taxonomy validation against canonical Phase 1 configuration; canonical gate descriptions in decisions; explicit self-attestation, independent-verification, release-authorization, and risk-review fields.
- `tests/test_phase21.py`: CLI-level registration, capability mismatch, host-output parity, canonical routing/gates, security evidence and critical-finding checks.
- `docs/adr/ADR-001-route-capability-binding.md`: documents the optional backward-compatible route field before implementation.
- `docs/phase-2-orchestration.md`: clarifies policy ownership, the capability binding and evidence boundaries.
- `docs/reviews/evidence/phase-2-1/`: synthetic evidence inputs and both host final JSON responses; no user or production evidence is included.
- This report. The pre-existing uncommitted Phase 2 implementation remains part of the working tree; it was not reset or replaced.

No Phase 1 canonical quality-gate or documentation-standard file was changed. No global host settings were modified; session-only permissions were used. No external toolkit or production system was installed, executed, updated, or deployed.

## Test commands and results

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v` — **51 tests passed** on Linux/Python 3.14.4: 28 Phase 1 tests, 17 existing Phase 2 tests, and 6 new Phase 2.1 tests.
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p test_phase21.py -v` — **6 tests passed**, covering CLI-level dynamic registration, host-output parity, canonical roles/gates, self-attested evidence, a waived gate with an open critical finding, and unknown risk.
- Test-driven checks were observed failing before the corresponding additive fields or capability validation existed, then passing after implementation. These expected red runs were development evidence, not final test failures.
- `git diff --check` — exit 0 for tracked changes. The newly created review files were separately checked for trailing whitespace.

## Codex versus Claude parity

Hosts: Codex CLI `0.166.0`; Claude Code `2.1.316`. Each host was prompted to use its router skill and run each command separately, using its own host value. Commands ran from the toolkit root, with synthetic evidence files in a temporary directory. `positive.json` has S1 manual self-attested evidence; `negative.json` has no gate evidence. They are preserved under [`evidence/phase-2-1/`](evidence/phase-2-1/).

| Case | Command, with `<host>` equal to `codex` or `claude` | Both hosts' reported result |
| --- | --- | --- |
| Positive route | `python3 -B -m orchestration route --intent documentation-audit --host <host> --risk low --profile lean` | Exit 0; primary `software-engineering-playbook`, not attested as available, manual fallback, `blocked: false`. |
| Positive gate | `python3 -B -m orchestration evaluate --stage requirements --risk low --profile lean --evidence <positive.json>` | Exit 0; S1 `PASS` with `SELF_ATTESTED`, overall `REVIEW_REQUIRED`, `release_authorized: false`. |
| Negative route | `python3 -B -m orchestration route --intent implementation --host <host> --risk high --profile business-critical` | Exit 1; primary `superpowers`, unavailable, `blocked: true`. |
| Negative gate | `python3 -B -m orchestration evaluate --stage release --risk high --profile business-critical --evidence <negative.json>` | Exit 1; S1–S5 `NOT_RUN`, overall `BLOCKED`, `release_authorized: false`. |

Codex invocation used `codex exec --ephemeral --sandbox read-only --skip-git-repo-check` with an output-last-message file. Claude invocation used `claude -p ... --permission-mode dontAsk --no-session-persistence --setting-sources project --allowedTools 'Bash(python3 -B -m orchestration *)' --add-dir <temporary-evidence-dir>`. These host processes ran with explicit command approval outside the outer filesystem sandbox; the sessions were instructed not to modify project files and only synthetic evidence was supplied. Claude's first two attempts could not run the commands because its generated shell calls did not match the session allowlist; the successful run used four separate exact commands without shell operators. The denied attempts were not counted as successful execution.

Complete final host JSON: [Codex](evidence/phase-2-1/codex-final.json) and [Claude](evidence/phase-2-1/claude-final.json). All four JSON objects compared equal **field-for-field** after parsing; no fields were excluded. Each host response also matched a fresh direct invocation of the corresponding current CLI command. The optional route-capability validation was added while these host processes were running; the compared default routes do not use that optional field, and the resulting host JSON was checked against the final CLI. The host responses are model-produced reproductions of tool outputs, not signed execution logs. Host-specific `--host` input differed; no host-specific output field needed normalization. Tool availability and results may differ with real host inventories.

## Dynamic registration evidence

The test `test_new_local_toolkit_registration_does_not_change_engine_or_gates` creates a temporary dummy `SKILL.md` with no executable code, a separate JSON configuration, and synthetic review/installation/host attestations. The test:

1. Registers `dummy-toolkit` with `dummy-capability` and selects it as the primary for a new configured intent.
2. Checks the tree digest and attested host evidence, with output explicitly `SELF_ATTESTED` and no recorded task execution.
3. Checks that a missing mandatory security gate still blocks.
4. Rejects a capability mismatch, disables the tool, tests an unsupported host, and tests a missing entrypoint.

No third-party package, marketplace, global configuration, or router source change is required to register that fixture. The optional capability-validation feature itself required a backward-compatible engine change and ADR-001; this does not independently verify the provider's claims.

## Security evidence boundary

A gate `PASS`, `FAIL`, or `WAIVED` is labeled `SELF_ATTESTED`. `independent_verification: NOT_VERIFIED` makes the lack of independent verification explicit; this phase does not implement a verified-evidence claim, identity service, signatures, or artifact validation. `REVIEW_REQUIRED` always includes `release_authorized: false`. Required `NOT_RUN` evidence blocks. An open critical finding blocks even when a gate has a valid scoped waiver. The risk classifier reports omitted factors and `requires_owner_review: true`; callers supplying `--risk` directly must still obtain owner review.

## Policy ownership and intentional boundaries

- `standards/quality-gates.yaml` is the authoritative Phase 1 profile gate description. Orchestration's S1–S5 checks add security-specific evidence requirements; they do not modify, override, or enforce the canonical gates. A selected profile returns the canonical descriptions and an explicit false enforcement flag.
- `standards/orchestration.yaml` maps project profile names to configurable security risk floors. `policy()` rejects profiles that do not match canonical profile/gate names. Profile floors and S1–S5 are Phase 2 configuration; the engineering/security owner must approve policy changes. They do not replace the higher-priority approved engineering standard.
- The configured primary roles remain: Superpowers for implementation, GStack for discovery, UI UX Pro Max for UI design, and Impeccable for design critique. Tests assert these mappings. Release governance and the security-policy owner cannot be handed to an external skill.
- Compatibility and installation are reported as self-attested or unverified, not independently verified. External registry sources and capabilities are declarations until reviewed and tested. Existing host skill selection is not controlled by toggling this registry.

## Remaining limitations

1. The host scenarios used synthetic evidence and no external integration. Trail of Bits, GStack, Superpowers, UI UX Pro Max, and Impeccable remain unpinned and unverified by this implementation; upstream source review is not a host invocation.
2. This phase does not validate reviewer identity, evidence content, a Git commit against a publisher, or artifact signatures. An operator can fabricate attestations. `REVIEW_REQUIRED` does not authorize release; CI and authorized humans are still needed.
3. Only Linux and the specific host/runtime versions above were tested. Different installed plugins, permissions or host versions may produce different results. The first Claude attempts were denied by its shell permissions; no global setting was changed to get a successful run.
4. The risk classifier flags unknown factors, but callers can supply a risk/profile directly; binding an assessment to a project manifest and authenticated identity is outside scope.
5. Existing project-owned toolkit snapshots do not automatically update. Capability binding is optional for backward compatibility; routes that omit it are not checked against a primary skill's advertised capability.
6. Existing filesystem trust assumptions from Phase 1 remain: concurrent hostile filesystem mutation is not handled. The host parity JSON is a limited reproducible sample, not a proof of all workflows or prompts.
