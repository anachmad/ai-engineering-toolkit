# Phase 2: modular orchestration and secure engineering

Status: draft

## Scope and architecture

Phase 1 standards and project documentation remain authoritative. `standards/orchestration.yaml` is versioned JSON-formatted YAML; it declares a registry, one primary workflow per intent, optional secondary skills, security stages, risk factors, and S1–S5 gate policy. `orchestration` reads that configuration without changing it or executing external code. `secure-engineering` provides lifecycle guidance and the workflow-router skill explains how to use the policy. Host adapters point to these shared definitions; they do not carry separate security rules.

Policy precedence is repository safety and explicit human approvals, approved project requirements and canonical standards, project adapter instructions, then external workflows. `standards/quality-gates.yaml` is the sole source of the existing profile-level gate descriptions. The evaluator returns those descriptions for a selected profile, with `canonical_profile_gates_enforced: false`: S1–S5 are supplementary security checks and cannot override or replace canonical project gates. Project security requirements and gate policy govern tool outputs; a tool cannot authorize a release or override policy. GitLab and an authorized human remain the intended release-enforcement layer.

Phase 1's `share` copies the orchestrator and project-local adapters into new shared projects. Existing shared copies are not automatically updated. Configuring, enabling, disabling, or replacing a registry entry changes routing recommendations only: it does not install or remove a skill, alter host auto-invocation, or execute it. External installation, uninstallation, and approved version updates remain manual and subject to review; a lifecycle manager is deferred to Phase 3.

## Try the local commands

From the toolkit root (or a project's `.engineering/toolkit`):

```sh
python3 -m orchestration registry
python3 -m orchestration status --host codex
python3 -m orchestration risk --factors '{"data_sensitivity":true,"internet_exposure":true}'
python3 -m orchestration route --intent implementation --risk high --host codex
python3 -m orchestration evaluate --stage release --risk high --evidence examples/security-evidence.json
```

The last command expects a JSON evidence file; `examples/security-evidence.json` is available in this repository, not in existing shared snapshots. It intentionally returns `BLOCKED` and exit 1. Commands return exit 2 for invalid input; routing also exits 1 when blocked. Do not treat exit 0 as release authorization: a nonblocked evidence decision is `REVIEW_REQUIRED`.

To change registry configuration, copy `standards/orchestration.yaml` to a reviewed, project-controlled file, edit its `skills` and `routes` entries, and pass `--config /absolute/path/to/policy.json` **before** the subcommand. Every entry names a provider, capabilities, source, host support, installation requirements, activation via routes/`required_for`, fallback and evidence contract. Register a replacement by adding an entry and changing a route's `primary` or `secondary`. A route may set an optional `capability`; if present, policy validation rejects a primary that does not declare that capability. This is a configuration assertion, not proof the capability works; see [ADR-001](adr/ADR-001-route-capability-binding.md). The release owner remains `release-governance` and the security-review primary remains `secure-engineering`; validation rejects external takeover. Review policy changes with the authorized owner. Configuration may not relax higher-priority project security policy.

Risk starts at the configured default (`medium`) and escalates to the highest level associated with a true factor. Inputs are booleans from `security.factor_levels`; omitted factors are reported as unknown rather than silently asserted false. This is a decision aid, not a substitute for owner risk assessment. An explicitly supplied `--risk` controls routing/evaluation, so the reviewer must use the approved classification and account for unknowns. When `--profile` is supplied, configured profile floors prevent lowering Business Critical below high and Standard below medium. The CLI does not automatically read a project manifest, so pass the actual profile explicitly.

## Status and trust

`status` defaults to no inventory: enabled is configuration, not proof of installation. It separately reports configured, enabled, files present, installed, loadable, available, compatible and executed. Installed requires a named `installation_evidence` record; this remains an attestation rather than a host probe. `executed` remains `null` with `execution_status: NOT_VERIFIED`: the orchestrator never runs or independently verifies a task's execution. Tool-backed gate evidence may carry an execution attestation, which is not proof of execution. Internal skills need host evidence too; file presence does not prove native discovery. External skills require an explicitly supplied local inventory and remain unavailable unless all of the following are provided:

- A local directory, safe relative native `entrypoint`, and `installation_evidence` reference.
- A registry `approved_commit` of 40 lowercase hex characters and `approved_tree_sha256` (64 lowercase hex characters), plus matching `observed_commit` in inventory. The commit is **human-attested**, not independently checked against Git or publisher signatures.
- An inventory `review` containing matching `source`, named `reviewer`, approval evidence reference, and true values for `publisher_reviewed`, `source_reviewed`, `instructions_reviewed`, `executables_reviewed`, `permissions_reviewed`, `injection_reviewed`, and `dependencies_reviewed`.
- Host support set to `verified` in the reviewed registry and host-specific `host_evidence.<host>.invocation_evidence` in the inventory. This is an attestation, not a live host probe.

`tree_hash(path)` in `orchestration/core.py` hashes sorted relative filenames and file bytes with length prefixes and rejects symlinks; compare this local digest to the approved digest. Source and publisher authenticity, a real immutable commit, full review of executable components and installation mechanisms, licensing, approvals, and correct scope still require human verification. Changing content breaks the digest check. Do not enable or execute a third-party skill until that verification has occurred; update the reviewed commit, digest, review and host evidence together for each upgrade.

Inventory is JSON, for example (replace all placeholders only after review):

```json
{"schema_version":1,"skills":{"differential-review":{"path":"/absolute/skill-dir","entrypoint":"SKILL.md","installation_evidence":"<install-record>","observed_commit":"<40-hex-commit>","review":{"source":"https://github.com/trailofbits/skills","reviewer":"<owner>","approval":"<review-record>","publisher_reviewed":true,"source_reviewed":true,"instructions_reviewed":true,"executables_reviewed":true,"permissions_reviewed":true,"injection_reviewed":true,"dependencies_reviewed":true},"host_evidence":{"codex":{"invocation_evidence":"<smoke-test-record>"}}}}}
```

A one-off local tree digest can be calculated after inspecting the target with `python3 -c "from orchestration.core import tree_hash; print(tree_hash('/absolute/skill-dir'))"`. This reads local files only; do not run untrusted project scripts.

No bundled external adapter is approved or pinned by default. Repository paths, supported plugin formats, and host APIs can change; recheck official documentation before use. A missing primary produces a manual fallback for low/medium risk, and blocks high/critical routes. The router checks every registry entry with an applicable `required_for` rule, even when it is not listed as a route secondary; a missing required skill blocks. Secure Engineering is required for configured lifecycle intents at high and critical risk. Low and medium risk use contextual security guidance and the applicable gates. Approved alternative evidence can be supplied to gate evaluation through a named human reviewer, subject to project policy; the router does not assert equivalence automatically.

## Security gate evidence

S1 covers requirements and architecture, S2 implementation, S3 code review, S4 dependency/static analysis, and S5 release readiness. Risk and stage select required gates. Each gate has one explicit outcome: `PASS`, `FAIL`, `NOT_APPLICABLE`, `NOT_RUN`, or `WAIVED`. Missing required gates are `NOT_RUN` and block; required gates cannot be marked not applicable. Non-required `NOT_APPLICABLE` needs a reason. A `PASS` or `FAIL` needs an evidence reference and either a `manual` method with named reviewer, or a `skill` method with a known, reviewed, host-compatible skill, task-specific execution evidence, and at least one capability accepted by that gate. Accepted capabilities are declared in `security.gates.<gate>.accepted_skill_capabilities`. Existing configurations that omit this field continue to support manual evidence but reject tool-backed gate evidence until accepted capabilities are configured. Capability matching is self-attested metadata, not proof that a tool covered every control: for example, one S4 tool does not automatically establish both dependency and static-analysis coverage. The output marks these records `SELF_ATTESTED` and `independent_verification: NOT_VERIFIED`, with `release_authorized: false` even for `REVIEW_REQUIRED`. Records are operator attestations: the evaluator cannot validate the underlying artifacts, identity, signatures, scope, or actual execution.

For example, a human-reviewed S1 record has this shape (the paths and names must be real records, not placeholders):

```json
{"schema_version":1,"gates":{"S1":{"outcome":"PASS","method":"manual","reviewer":"Security Owner","evidence":"MR-123:security-design-review"}},"findings":[]}
```

A tool-backed record instead uses `method: "skill"`, `skill`, and `execution_evidence`, and needs `--host` plus an approved `--inventory`. File names and reviewer identities are references supplied by the operator; they are not independently checked.

A waiver needs reason, approver, gate ID as scope, and ISO expiry. The approver must appear in the reviewed `authorized_waiver_approvers` policy; the default list is empty. Open critical findings block by default, even if a gate is waived. An exception to an open critical finding is not implemented; setting `critical_exception_enabled` does not change that. Findings require unique IDs, severity, `open`/`resolved` status, and evidence references. Keep the reviewed JSON evidence in the project's existing documentation or issue/MR/CI evidence store; link requirements, controls, tests, findings and release decisions there. Do not put secrets in evidence records.

## External adapters: source verification status

The [official Trail of Bits marketplace](https://github.com/trailofbits/skills) lists Claude Code and Codex marketplace approaches, but these project adapters do not install or invoke them. The following descriptions are source-level findings, not local compatibility or safety approvals:

| Registry ID | Official capability and prerequisites | Local state |
| --- | --- | --- |
| `differential-review` | [Security-focused diff review](https://github.com/trailofbits/skills/blob/main/plugins/differential-review/skills/differential-review/SKILL.md); uses Git history and review context. | Unpinned, unreviewed, host invocation unverified. |
| `static-analysis` | [Plugin](https://github.com/trailofbits/skills/tree/main/plugins/static-analysis) containing `codeql`, `semgrep`, and `sarif-parsing`; scanners and dependencies vary. Some upstream workflows may access network and third-party rule repositories. | Plugin, not a single native skill; unpinned and unverified. |
| `supply-chain-risk-auditor` | [Dependency auditor](https://github.com/trailofbits/skills/blob/main/plugins/supply-chain-risk-auditor/README.md) for npm, PyPI and Go; uses `uv`, registry/advisory access or cache, and recommends authenticated `gh`. | Unpinned, unreviewed, host invocation unverified. |
| `insecure-defaults`, `sharp-edges` | Listed in the [official marketplace](https://github.com/trailofbits/skills); optional. | Disabled and unverified. |

GStack, Superpowers, UI UX Pro Max, and Impeccable are registry entries with source URLs, not installed or verified integrations. No third-party source is copied into this toolkit.

## Host installation and boundaries

For a new shared project use Phase 1's `share`; it creates relative skill links under `.agents/skills/` and `.claude/skills/` to the project's own toolkit. For an existing project, inspect both destinations and add only missing links to the matching `adapters/<host>/<skill>` directories with project-owner approval. Restart the host if discovery is stale. Do not overwrite an existing skill or change user-level configuration without authorization. Claude may need access to the toolkit directory and shell permission; use its supported permission mechanism. A successful file link or registry status does not prove invocation. Project-local Codex and Claude skill loading were exercised in temporary projects as recorded in the acceptance report; external plugin invocation remains unverified.

For an already shared project where these links do not exist, the following project-local commands link to that project's own toolkit; inspect the destinations first and run only the missing ones:

```sh
mkdir -p .agents/skills .claude/skills
ln -s ../../.engineering/toolkit/adapters/codex/secure-engineering .agents/skills/secure-engineering
ln -s ../../.engineering/toolkit/adapters/codex/engineering-workflow-router .agents/skills/engineering-workflow-router
ln -s ../../.engineering/toolkit/adapters/claude/secure-engineering .claude/skills/secure-engineering
ln -s ../../.engineering/toolkit/adapters/claude/engineering-workflow-router .claude/skills/engineering-workflow-router
```

These commands require the updated adapters to already be present in the project's `.engineering/toolkit/`; existing Phase 1 snapshots do not contain them. `ln -s` does not replace existing links. Updating that snapshot requires a separately reviewed project change.

The current path and symlink threat model is Phase 1's accepted trusted-user-directory model; concurrent hostile filesystem manipulation is not prevented. Third-party instructions, repository text, tool output and external references are untrusted; keep least privilege and human review. The CLI does not enforce tool sandboxing or production deployment controls.
