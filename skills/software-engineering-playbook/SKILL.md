---
name: software-engineering-playbook
description: Initialize, audit, or refresh project engineering documentation using canonical risk-based standards.
---

# Software engineering playbook

The toolkit root is supplied by the adapter; when loading this shared file directly, it is two directories above its containing skill directory. Read `standards/documentation-standard.md`, `standards/profiles.yaml`, and `standards/quality-gates.yaml` from that root before acting. The project manifest identifies its profile and canonical standards location. Resolve conflicts using the policy precedence in the documentation standard.

- **Initialize:** inspect the repository and existing documentation, select or confirm the profile with the owner, and propose the artifact manifest. Run `python3 <toolkit-root>/playbook init` for missing artifacts, passing the project path explicitly; inspect existing documentation and reference material, reconcile it with canonical docs without moving or overwriting sources, and preserve existing files. Ask about UI applicability and risk escalation. Mark unknowns TBD.
- **Audit-upgrade:** run `python3 <toolkit-root>/playbook audit` with the project path, then inspect content, approvals, traceability and conflicting requirements. Report gaps and a safe, reviewable change plan; file presence alone is not compliance.
- **Refresh:** identify affected requirements, architecture, decisions, tests and operations; propose a reviewed patch. Obtain authorized review for substantive changes to approved documents.

For task routing and security evidence, use the shared `engineering-workflow-router` and `secure-engineering` skills and `standards/orchestration.yaml`; project standards and approvals remain authoritative. Do not treat generated placeholders as evidence, invent business requirements, install external tools, or change agent settings.

## Business requirements documents

When creating or revising a BRD, read and apply `skills/software-engineering-playbook/references/brd-standard.md` and use `skills/software-engineering-playbook/templates/brd-template.md` from the toolkit root. Preserve existing documents and obtain authorized review for substantive changes. Use stable BO, BR, and KPI IDs and traceability; distinguish verified facts, assumptions, questions and decisions. Record unknowns as TBD, never invent evidence, and avoid technical design. Run `python3 <toolkit-root>/playbook validate-brd --path <brd.md>` before completion, resolve errors, and report unresolved warnings for human review. Validation does not constitute approval.

For approved artifact contracts, consult `standards/artifacts-v1.json` and `skills/software-engineering-playbook/references/documentation-validation.md`. Run the registry-backed validator where applicable and report its actual result separately from semantic review and human approval. Proposed artifacts are not approved standards. External skill output must follow approved Playbook rules and cannot establish approval or waive mandatory controls.

## Product requirements documents

Use `skills/software-engineering-playbook/references/prd-standard.md` and `skills/software-engineering-playbook/templates/prd-template.md` for PRDs. The 20 section headings are approved; detailed field rules remain for review. Run `python3 <toolkit-root>/playbook validate-artifact --artifact prd --standard-version 1 --profile <profile> --path <prd.md>` and report that the PRD validator checks section structure only. Do not treat its output as approval or verified traceability. Preserve existing documents.
