# Phase 1 remediation status

Status: implementation review pending
Original findings: [independent acceptance report](phase-1-acceptance-report.md).
This document records remediation evidence without rewriting the original review.

| Finding | Current evidence | Status and remaining limit |
| --- | --- | --- |
| M1 path ancestors | `project_base()` resolves and prints the effective project path; `tests/test_remediation.py` exercises an ancestor symlink; existing tests reject nested symlinks. | Mitigation implemented: the user-selected root is resolved, not rejected. Path checks do not protect against a concurrent hostile filesystem change; the trust model and untested macOS behavior need owner review. |
| M2 file collision | `init` preflights non-file paths and reports an error; `test_nonfile_conflict_fails_before_writes`. | Addressed for preflight conflicts. A collision after preflight is reported, but earlier created files are not automatically rolled back. |
| M3 UI applicability | `set-ui` previews a unified manifest diff and current SHA-256. `--apply` requires the reviewed hash and explicit invocation; tests cover preservation, repeated operations, stale/missing hash and an interrupted manifest replace. | Implemented. If the manifest replacement fails after creating a missing UI draft, that draft remains and must be reviewed before retry. It never deletes an existing UI file when changing applicability to `no`. No existing project manifest was changed for this remediation. |
| M4 schemas and standards path | `standards/schemas/project-v1.json`, `standards/schemas/policies-v1.json`, `standards/schema-contracts.md`, manifest validation and location checks; tests cover malformed and unsupported manifests, moved project-local copies, and missing standards. | Partially addressed: the manifest and top-level policy fields have machine-readable versioned contracts; deeper policy rules are documented and checked in Python. General YAML and arbitrary JSON Schema remain unsupported. Owner must decide whether this satisfies the Phase 1 schema deliverable. |
| m1 host audit and refresh | Separate read-only/plan host checks against temporary approved architecture and conflicting draft files. Both identified the conflict and said authorized review is needed; the approved file SHA-256 remained `fb613a26bc911c45ea205efc6703bbf6ff1df99cccace54d34cab92ed854821e` in both projects. | Both produced concrete unified diff proposals in a subsequent answer-only test when explicitly asked. They preserved the approved architecture and required authorized review; this is a small host-behavior sample, not guaranteed enforcement. In the first test Codex ran read-only; Claude plan mode wrote a user-level plan file, `/home/andik/.claude/plans/audit-the-lean-project-wild-lynx.md`, despite the no-edit prompt. It did not alter the fixture or agent settings. Its plan file was not removed. |
| m2 shared-copy provenance | `share` creates `provenance.json`, containing SHA-256 hashes of copied files including uncommitted source contents; `tests/test_shared_project.py` checks a recorded hash. | Addressed as a snapshot. There is no automated drift check, Git revision attestation, update manager, or claim that hashes establish approval. |
| m3 path documentation | `docs/architecture.md` and `standards/schema-contracts.md`. | Updated to disclose path resolution, lack of hostile concurrency protection, and schema/standards boundaries. |
| m4 test gaps | `tests/test_remediation.py`; existing acceptance, reference, portability and shared-project suites. | Expanded; platform and concurrency limits remain. |

## Verification

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v`: 28 tests passed; they exercise all three profiles and new remediation paths. Fresh `init --ui` and audit commands returned 0 for all three profiles.
- Codex: `codex exec --ephemeral --sandbox read-only --skip-git-repo-check` with a prompt to audit a Lean disposable project and propose a refresh without edits. It identified the approved read-only architecture versus a draft allowing writes, missing owner/approval evidence, and authorized-review requirement. Exit 0.
- Claude Code: `claude -p` with the equivalent prompt, `--permission-mode plan --no-session-persistence`, and `--add-dir` for its temporary fixture. It identified the same conflict and review requirement. Exit 0; the plan-file side effect above was reported by the host itself.
- Both approved fixture hashes were checked after the host tests and matched the hash recorded before them. A second read-only Codex run and a Claude `--permission-mode dontAsk` run explicitly requested an answer-only unified diff; both returned one and stated the need for authorized review.

## Exit recommendation

**CONDITIONAL GO for a fresh independent acceptance review, not final Phase 1 sign-off.** The engineering owner should resolve the remaining schema-scope and path threat-model decisions, review the host behavior evidence and all uncommitted changes. Rerun the independent acceptance review after those decisions; do not interpret policy text or test fixtures as CI enforcement, project approval, or production evidence. Phase 2 remains unimplemented.
