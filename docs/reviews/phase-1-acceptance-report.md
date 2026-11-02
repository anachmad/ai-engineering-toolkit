# Independent Phase 1 acceptance review

Review date: 2026-11-01
Recommendation: **NO-GO for Phase 1 sign-off**, pending the major findings below.
Review basis: the working tree at commit `161f308` plus its existing uncommitted changes. No implementation changes were made during this review. The specification is a proposed draft; this report is an engineering assessment, not owner approval.

## Scope and method

Reviewed the architecture specification, profile and gate policies, documentation standard, templates, shared skill, host adapters, scaffolder, audit and shared-project setup, README, and automated tests. Generated and inspected Lean, Standard and Business Critical samples in isolated temporary directories; tested preservation, manifests, UI and path conflicts. Ran each host separately in read-only mode. The review did not implement the router, manager, integrations, or release gates.

Statuses mean **PASS**: directly supported by evidence for the criterion's stated scope; **PARTIAL**: evidence supports only part of it or a significant limitation remains; **FAIL**: a stated requirement demonstrably fails; **NOT TESTED**: deferred, unavailable, or not independently exercised. A scaffolded control or passing presence audit does not prove a control was implemented, approved, or enforced.

## Requirements versus implementation

| Requirement | Evidence | Assessment |
| --- | --- | --- |
| Shared standards for both hosts | `standards/`, `skills/software-engineering-playbook/SKILL.md`, both `adapters/*/software-engineering-playbook/SKILL.md`; separate invocations below. | **PASS**: both adapters refer to the same shared skill and policies; adapters contain no profile or gate rules. Copies installed into separate projects can later diverge; there is no version/update mechanism. |
| Lean, Standard and Business Critical | `standards/profiles.yaml`, `standards/quality-gates.yaml`; independent sample generation below. | **PASS** for scaffold and declarative gate descriptions. Gate compliance itself is not automated by Phase 1. |
| Versioned, validated schemas | `playbook/__main__.py:22-92`; `tests/test_validation.py`. | **PARTIAL**: schema versions and selected fields are validated, but no standalone formal schema or compatibility contract exists; only JSON syntax is accepted although filenames end in `.yaml`; manifest `standards_path` is only checked for nonempty text, not existence or agreement with policies used. |
| Project templates and metadata | `templates/project/`, `standards/document-prompts.yaml`, independent samples. | **PARTIAL**: documents have draft/TBD metadata and relevant prompts, while root agent instructions and reference guide intentionally lack document-status metadata. Project-specific completion and approval are manual. The scaffold can report success on a required-file directory conflict (M2). |
| Initialize, audit-upgrade and refresh | Shared playbook instructions and `playbook/__main__.py:116-184`. | **PARTIAL**: CLI initializes and reports artifact presence; substantive compliance and conflict analysis and refresh are agent instructions, not deterministic CLI features. No independent refresh workflow or authorized-review behavior was tested. |
| Preserve existing documents | `tests/test_phase1_acceptance.py` and independent samples. | **PASS** for tested approved regular files; see M1/M2 for path and conflict safety limits. |
| No third-party toolkit installation | Imports and `share` in `playbook/__main__.py`; tracked files inspected. | **PARTIAL**: no third-party installer or bundled toolkit was found in this implementation and none was run in this review. The machine contains independently installed plugins; their installation history cannot be established without a pre-project baseline. |
| No global changes | Current user-level paths inspected; earlier conversation records explicit approval and creation of two skill links. | **FAIL** against the original blanket constraint if interpreted for the entire project history: `~/.agents/skills/software-engineering-playbook` and `~/.claude/skills/software-engineering-playbook` were added after explicit user approval. No global settings-file edit was observed in this review; no global configuration was changed by the review commands. |

## Functional acceptance criteria

| ID | Status | Evidence and boundary |
| --- | --- | --- |
| AC-01 | **PASS** | Existing automated empty-repository tests and isolated Lean sample: exit 0, all 9 configured artifacts present, root agent files and draft manifest generated, no invented business requirements observed. |
| AC-02 | **PASS** | Standard sample: exit 0 and all 15 configured artifacts present, including distinct requirement, architecture, quality, and operations placeholders. |
| AC-03 | **PASS** | Business Critical sample: exit 0 and all 19 configured artifacts present; approval, threat-model, access-matrix, traceability, and recovery prompts exist. Canonical gates require independent review, separate security review, tested restore, RTO/RPO evidence and separated release approval. These are requirements and placeholders, not evidence of completed controls. |
| AC-04 | **PARTIAL** | For all profiles an approved architecture file's SHA-256 was unchanged after `init`; an existing repository without a manifest returned missing items without writes. The CLI checks presence only and does not itself identify approved status, conflicts, or missing approvals by category. An independent end-to-end host audit of a conflicting approved artifact was not performed in this review. |
| AC-05 | **NOT TESTED** | Router is Phase 2; routing implementation absent and not part of this review. |
| AC-06 | **NOT TESTED** | Toolkit capability detection and fallback belong to Phase 2. |
| AC-07 | **PASS** | Both installed hosts independently invoked their own adapter in this checkout and reported the same shared playbook and three canonical standards; Codex read all three, Claude reported reading the profiles and openings of the other two. This establishes discovery and invocation on this Linux environment, not equivalent enforcement. |
| AC-08 | **NOT TESTED** | Manager installer dry-run belongs to Phase 3. `playbook share` is a separate project-copy command, not evidence for this contract. |
| AC-09 | **NOT TESTED** | Manager lockfile/install lifecycle belongs to Phase 3. Existing `share` intentionally refuses a second run, so it does not establish this criterion. |
| AC-10 | **NOT TESTED** | Manager partial failure and rollback belong to Phase 3. |
| AC-11 | **NOT TESTED** | Manager uninstall belongs to Phase 3. |
| AC-12 | **NOT TESTED** | Enforced Business Critical release gate belongs to Phase 4; YAML text and draft placeholders are not enforcement. |

## Test evidence

Environment: Linux, Python `3.14.4`; Codex CLI `0.166.0`. Tested the current working tree, including uncommitted changes.

1. `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v` — **20 tests, OK**, zero failures/errors. Tests cover profile generation, a preserved approved file, project-relative links, invalid configuration cases, references, and sample controls. They do not cover every test matrix scenario, full schema semantics, host approvals, or symlink race conditions.
2. `PYTHONDONTWRITEBYTECODE=1 python3 /tmp/aet-phase1-independent-check.py` — review-only script, SHA-256 `bf6f38bfe04e07915f5eb15d4e58ae64a03ff579b8a1243569abcc6c1619f310`; the script and projects reside in temporary storage and are not part of the repository. Results:
   - All three profile `init` and `audit` commands exited 0; configured artifacts missing: `[]`; manifest profile matched, status `draft`, UI `unknown`; an existing approved architecture file remained byte-identical. All six gate categories were present in each canonical policy.
   - Standard re-initialization with `--ui` after `ui=unknown` exited **2**, reported a manifest conflict and did not create the UI artifact (M3).
   - A project directory reached through a symlink in its parent path was initialized with exit **0** and received files at the symlink target (M1). Both paths were inside the disposable test area.
   - A directory occupying `README.md` led `init` to exit **0** and print `preserved: README.md`; subsequent audit exited **1** because the file was missing (M2).
   - An existing Business Critical project with only an approved README audited with exit **1** for missing items and remained byte-for-byte unchanged.
3. Separate Python temporary-directory loop invoked `python3 -B -m playbook init --path <temporary-project> --profile <profile> --name 'UI Example' --ui` for each profile. All returned 0; each manifest said `ui: yes`, and each UI document contained an accessibility prompt. Release-gate descriptions were `Owner decision`, `Approved GitLab release gate`, and `Separate business and technical approval`, respectively. These are descriptions, not executable checks.
4. `codex exec --ephemeral --sandbox read-only --skip-git-repo-check 'Use $software-engineering-playbook. Report only the exact adapter and canonical standards paths you read, and the default profile. Do not modify any files.'` — exit 0; identified the Codex adapter, shared skill and `standards/documentation-standard.md`, `profiles.yaml`, `quality-gates.yaml`; default `standard`.
5. `claude -p '/software-engineering-playbook Read the shared canonical standards. Report the exact adapter and standards paths and the default profile. Do not modify files.' --permission-mode plan --no-session-persistence` — exit 0; identified the Claude adapter, same shared skill and standards directory; default `standard`. Claude explicitly said it read only the opening of the documentation standard and quality gates, so full semantic adherence is not proven.
6. `git diff --check` — exit 0. `python3 --version` — `Python 3.14.4`.

The host invocations ran outside the command sandbox with explicit approval because earlier sandboxed host startup failed; the host sessions themselves were read-only/plan and non-persistent. Neither host invocation established enforcement or completed a full initialization/audit scenario in this review.

## Findings

### Critical

None established by this review. This is not a security audit and does not establish absence of critical vulnerabilities.

### Major

- **M1 — Project-root ancestor symlinks are not rejected.** `playbook/__main__.py:116-120` checks only whether the final project path is a symlink, while `destination()` starts checking below that base. The isolated test above wrote through a symlink in a parent path. This does not demonstrate privilege escalation or a write outside the authorized user-selected logical path; it demonstrates that symlink ancestors bypass the stated symlink-path defense and may redirect writes when path components are untrusted. There is also a check/use window; resistance to concurrent symlink replacement was not tested. Reconcile the supported trust model with the specification's path-validation control.
- **M2 — A directory conflict is reported as successful initialization.** At `playbook/__main__.py:145-153`, any `FileExistsError` is treated as a preserved file. A directory named `README.md` causes exit 0 despite a missing required file; `audit` subsequently exits 1. Existing files are preserved, but success output is misleading and the scaffold is incomplete.
- **M3 — Existing UI applicability cannot be advanced through the scaffolder.** A project initialized with UI `unknown` cannot later use `init --ui`: `playbook/__main__.py:123-127` rejects the change, leaving the UI document absent. This protects existing manifests but leaves no supported reviewed upgrade flow for a common case, including the Filio pilot. Manual reviewed changes are possible; no automatic overwrite is authorized by this finding.
- **M4 — Schema and standards-location validation are incomplete.** `validate_manifest()` checks `standards_path` only for nonempty text, while `audit` always loads policies from its own `ROOT`. A manifest can point elsewhere or to a missing path and still pass structural validation, creating ambiguity about which policy is authoritative. No separately specified formal schema or incompatible-migration contract was found. This is a Phase 1 deliverable and shared-standards consistency concern; owner confirmation of schema scope is needed.

### Minor

- **m1 — Skill audit and refresh remain instruction-dependent.** The CLI's documented audit is a presence check; it does not reliably detect approved-document conflicts, missing approvals, or traceability. Neither host's full audit/refresh behavior was independently exercised here. The README acknowledges the audit limitation.
- **m2 — Shared-project copies can drift.** `share` copies canonical files into each project and records no source revision or managed update mechanism. The README asks teams to review changes, but no automatic divergence check exists. This is a maintainability and future lifecycle risk; a full manager is deferred.
- **m3 — Documentation claims exceed demonstrated path safety.** `docs/architecture.md` says the scaffolder rejects symlink traversal, while M1 shows an ancestor-symlink case it accepts. Its statement should reflect the tested boundary.
- **m4 — Existing test assertions are incomplete.** The current tests exercise a symlink below the project root and several malformed policies, but not the M1/M2/M3 reproductions. Passing tests are not proof of these cases.

## Residual risks and untested areas

- Existing user-level links were created earlier by explicit user approval; they depend on the current toolkit path. A no-global-changes claim would be inaccurate. This review did not edit those links or settings.
- No historical global filesystem snapshot exists to prove what third-party toolkits were or were not installed before the project began. Runtime dependencies and code reviewed use the standard library; installed host plugins are outside this repository.
- Linux/Python 3.14 were tested. macOS, Python 3.11–3.13, Windows, and WSL were not tested in this review. No compatibility claim follows from a test on one platform.
- No end-to-end refresh approval, concurrent filesystem attack, hostile hooks, offline host operation, upgrade/rollback, CI enforcement, or deployment gate was exercised. Later-phase ACs remain untested, not failed merely because they are deferred.
- The review tested draft generation, not real approval, traceability completeness, test evidence, production readiness, or legal compliance.

## Recommended corrective actions

1. Agree and implement the project-path and symlink threat model; add tests for ancestor symlinks and any supported concurrent-change behavior (M1).
2. Detect non-file collisions before writes, return a failure identifying the path, and cover the case with a regression test (M2).
3. Design a reviewed, explicit UI-applicability update that preserves existing files and approval requirements; test unknown-to-yes and project conflicts (M3).
4. Specify versioned policy and manifest schemas, define compatibility behavior, validate the selected canonical standards location, and add positive and negative tests (M4).
5. Independently exercise host-driven audit and refresh against approved and conflicting documents; capture reproducible outputs (m1).
6. Document project-copy provenance and the path-safety boundary; defer automated update lifecycle to the appropriate phase (m2–m3).
7. Rerun this acceptance review and obtain an engineering owner's Phase 1 sign-off before declaring the exit gate passed.
