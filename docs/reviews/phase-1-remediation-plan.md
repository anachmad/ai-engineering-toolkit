# Phase 1 acceptance remediation plan

Status: proposed
Source: [Phase 1 acceptance review](phase-1-acceptance-report.md).
Objective: resolve the Phase 1 exit-gate findings and produce evidence for a fresh acceptance review. Phase 2 routing, external toolkit integration, manager lifecycle, and CI enforcement remain outside this plan.

## Milestone 1 — Safe paths and truthful conflicts (M1, M2, m3, m4)

1. Define the supported filesystem threat model. Decide how to handle symlinked ancestors in the project path, including legitimate system paths on macOS; resolve and display the effective target, and reject unsafe redirection within the project. Assess descriptor-relative, no-follow operations for concurrent replacement where supported. Document platform-specific guarantees and limits without claiming untested race protection.
2. Preflight expected destinations and distinguish regular files from directories and other conflicting object types. Preserve existing regular files; return a nonzero result naming a conflicting path before writing any planned artifact. Handle a collision occurring after preflight without reporting success.
3. Add regression tests using disposable directories for ancestor and nested symlinks, a symlinked project root, a directory at a required file path, and preservation of approved files. Add race tests only if the chosen design claims protection against concurrent replacement.
4. Correct the architecture documentation to match the tested path-safety boundary.

**Acceptance:** supported path cases and effective targets are explicit; unsafe path and non-file conflicts fail clearly without overwriting existing content; no partial writes occur for conflicts found at preflight; tests demonstrate the behavior on the platforms claimed. The prior M1/M2 reproduction scenarios no longer silently succeed contrary to the selected policy.

## Milestone 2 — Versioned schema and standards location (M4)

1. Document versioned contracts for the project manifest, profiles, quality gates, and document prompts, including required fields, allowed values, extension policy, and compatibility behavior. Choose a declarative representation that can be validated with the Python standard library; clearly state that JSON-formatted YAML is the supported syntax unless broader YAML support is deliberately approved.
2. Resolve a relative `standards_path` against the project root and define how absolute paths behave. Validate that the path exists and whether it identifies the same policy source used for the operation; fail clearly or require an explicit reviewed decision when it does not. Define behavior for existing manifests, copied/moved projects, and unsupported schema versions without silently migrating them.
3. Add positive and negative tests for every contract, missing and divergent standards locations, shared-project moves, and unsupported versions. Keep profile, artifact, and gate policy declarative and shared across both adapters.

**Acceptance:** valid current manifests and project-local moved copies work; missing or divergent standards are reported accurately; unsupported versions do not silently migrate; malformed inputs produce understandable failures; contract and tests describe the same behavior. Existing data remains unchanged.

## Milestone 3 — Reviewed UI applicability change (M3)

1. Design an explicit, reviewable operation to transition UI applicability from `unknown` to `yes` or `no`. Show the proposed manifest and artifact changes before applying them. Preserve existing UI documents and other project files; never infer approval from a draft or overwrite an existing manifest without the user's explicit authorization.
2. Apply the selected change only after authorization, create the conditional UI/UX artifact when applicable, and report any conflicts. Preserve status and unrelated manifest fields.
3. Test unknown-to-yes, unknown-to-no, repeated operations, existing UI documents, conflicting manifests, interrupted operations, and all profiles. Verify the resulting audit uses the approved setting.

**Acceptance:** an owner can explicitly review and authorize the change; the manifest and conditional document agree afterward; existing files are not silently changed; reruns and conflicts are predictable. Until this is available, the Filio pilot remains marked UI applicability unknown even though its draft PRD describes a mobile UI.

## Milestone 4 — Playbook behavior and project-copy provenance (AC-04, m1, m2)

1. In isolated workspaces, independently exercise both hosts' audit and refresh instructions against a project containing an approved document, a conflicting draft, and missing approval evidence. Capture prompts, relevant outputs, and before/after hashes; verify that substantive approved-document changes are proposed for authorized review rather than silently applied. Distinguish host instruction-following from the CLI's deterministic presence check.
2. Document how a project-owned toolkit copy records or communicates its source revision and how teams review drift. If a small source-revision record is adopted, define behavior when the source has uncommitted changes; do not build an automatic installer, lockfile lifecycle, or update manager in Phase 1.
3. Update usage guidance with the difference between presence checks and content review, project-local versus user-level skill selection, and previously authorized global links.

**Acceptance:** both hosts produce evidence-backed gap reports and safe refresh proposals in the test scenarios; approved source files remain unchanged without authorization; the scope of automated audit is clear; project-copy provenance and its limitations are understandable without asserting unsupported update guarantees.

## Milestone 5 — Reverification and exit decision

1. Run the full automated suite and isolated Lean, Standard, and Business Critical scaffold/audit scenarios, including UI and existing-file conflicts. Verify profile-specific gates as policy descriptions, not release enforcement.
2. Repeat Codex and Claude Code discovery/invocation separately against identical canonical standards. Record exact commands, outcomes, runtime versions, and untested environments. Keep temporary projects isolated and avoid global changes.
3. Update the acceptance report with results, remaining findings, and any user-approved exceptions. Request engineering-owner sign-off only after the major findings are resolved or explicitly accepted by the responsible owner.

**Acceptance:** AC-01–AC-04 and AC-07 have concrete, current evidence; no unresolved major finding is silently waived; the report states whether the exit recommendation is GO, CONDITIONAL GO, or NO-GO. Phase 2 work starts only after the owner accepts the Phase 1 outcome.

## Working constraints

- Keep this work in small, reviewable changes and preserve existing user documents and settings.
- Use Python 3 standard library and declarative configuration where practical; do not install third-party toolkits or change global agent settings.
- Do not update the Filio pilot's existing manifest or project-owned toolkit copy without explicit authorization. Source BRD and PRD remain unchanged.
- The prior user-level links were created with explicit approval; retain an accurate history rather than claiming no global additions occurred.
