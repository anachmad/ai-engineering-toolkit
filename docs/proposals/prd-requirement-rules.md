# PRD requirement field rules — proposal for review

Status: **Approved on 2026-11-04.** Local field checks are implemented in PRD contract v2; cross-document resolution remains unimplemented. The approved 20 sections, template, v1 validator and profile requirements remain available.

## Subsequent compatibility decision

On 2026-11-06, the owner decided to preserve established project ID formats; use the new default only when no format already exists for that requirement type. PRD v3 supports explicitly configured project formats; v2 retains its fixed pattern for compatibility. See `skills/software-engineering-playbook/references/requirement-id-compatibility.md`.

## Purpose

Make each product requirement easy to identify, understand, trace and verify. Product requirements express a product need or observable behavior; technical implementation decisions belong in appropriate architecture or system documents. Use the seven existing columns in the Product Requirements table.

## Proposed field contract

| Existing column | Proposed rule | Example |
| --- | --- | --- |
| ID | Use `PR-` followed by at least three digits, for example `PR-001`. Each ID is unique in the PRD and remains stable across revisions. Retire an ID rather than reusing it for a different requirement. | `PR-001` |
| Description | Describe one product need or observable behavior clearly, without assuming a specific technical implementation. | `A user can submit a support request.` |
| Source | Identify a business requirement such as `BR-001`, or identify another authorized source and its reference. Multiple sources may be listed, separated by commas. Do not invent sources or authorization. | `BR-001` |
| Priority | Use `Must`, `Should`, `Could`, or `TBD`. A priority reflects a product decision, not an automatically inferred business value. | `Must` |
| Actor / Stakeholder | Name the relevant user, role, or stakeholder. | `Requesting user` |
| Acceptance criteria | State observable, testable conditions; include limits, outcomes and exception cases where applicable. Use plain language or Given/When/Then. Separate multiple criteria with `<br>`. | `A valid request is acknowledged to the user.` |
| Status | Use `Draft`, `In review`, `Approved`, `Deferred`, or `TBD`. `Approved` is a recorded claim requiring human approval evidence; the validator cannot establish the approver's identity or authority. | `Draft` |

The document's own status is distinct from a requirement's status and follows the existing canonical documentation standard. The proposed requirement-level values above do not replace it.

## Example — illustrative only

The following is a fictional example, not a requirement or evidence for any real project. `BR-001` is assumed to exist only for illustration; a real review must check its source.

| ID | Description | Source | Priority | Actor / Stakeholder | Acceptance criteria | Status |
| --- | --- | --- | --- | --- | --- | --- |
| PR-001 | A user can submit a support request. | BR-001 | Must | Requesting user | A valid request is acknowledged to the user. | Draft |

## Proposed handling of unknown information

- Keep a completely `TBD` row as a draft placeholder; report a warning and do not create a fictitious requirement.
- When a `PR-` ID has been assigned, require every column to contain a value. Empty cells are errors; `TBD` is a warning that the requirement remains incomplete.
- `TBD` never counts as evidence, a verified source, approval, or completed acceptance.
- A project owner determines whether unresolved warnings are acceptable for a particular review. The validator must not infer release readiness or human approval.

## Proposed deterministic checks

| Check | Proposed result | Scope and limitations |
| --- | --- | --- |
| Missing requirement table or columns; malformed row; empty cell | ERROR | Check the exact seven template columns and each table row. |
| Malformed or duplicate `PR-` ID | ERROR | Check definitions within this PRD. Project-wide uniqueness needs a separate cross-document contract. |
| Unknown priority or requirement status | ERROR | Allowed values are the proposed values above, including `TBD`. |
| Placeholder or `TBD` in an actual requirement | WARN | The item is incomplete even if structural validation exits successfully. |
| BR reference in an available, explicitly selected BRD | ERROR if absent | A future cross-document validator must check the specified BRD. The current PRD validator does not do this. |
| Source document unavailable or external source cannot be checked | WARN / NOT VERIFIED | Never label a missing or unchecked source as verified. Record its location and resolve it through review. |
| Requirement approved without independent approval evidence | NOT VERIFIED | A status value alone cannot authenticate an approver. |

The proposed checks do not require every project to have a separate BRD. An authorized source outside a BRD must be identified and assessed by the owner; the format and authority evidence for such sources need agreement before implementation. The exact syntax for linking and selecting source documents is also an open design decision.

Deterministic checks cannot establish that a requirement is unambiguous, correct, complete, aligned with business goals, free of solution bias, or actually tested. These require semantic review and, where applicable, human approval. Existing lifecycle and security gates remain separate. Adding an automated quality gate or CI blocking policy requires its own design and verification.

## Decisions approved

1. Accept or change the proposed priority values and requirement status values.
2. Accept or change the seven field rules and `TBD` handling.
3. Confirm that a source outside the BRD can be used when the project owner identifies it as authorized.

Local PRD field checks are implemented in v2. Specify and test cross-document resolution separately; do not claim it works until implemented.
