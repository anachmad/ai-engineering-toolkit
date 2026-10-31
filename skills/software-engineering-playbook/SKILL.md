---
name: software-engineering-playbook
description: Initialize, audit, or refresh project engineering documentation using canonical risk-based standards.
---

# Software engineering playbook

Read `standards/documentation-standard.md`, `standards/profiles.yaml`, and `standards/quality-gates.yaml` from this toolkit before acting. The project manifest identifies its profile and canonical standards location. Resolve conflicts using the policy precedence in the documentation standard.

- **Initialize:** inspect the repository and existing documentation, select or confirm the profile with the owner, and propose the artifact manifest. Use `python3 -m playbook init` for missing artifacts; inspect conflicts and preserve existing files. Ask about UI applicability and risk escalation. Mark unknowns TBD.
- **Audit-upgrade:** use `python3 -m playbook audit`, then inspect content, approvals, traceability and conflicting requirements. Report gaps and a safe, reviewable change plan; file presence alone is not compliance.
- **Refresh:** identify affected requirements, architecture, decisions, tests and operations; propose a reviewed patch. Obtain authorized review for substantive changes to approved documents.

Do not treat generated placeholders as evidence, invent business requirements, install external tools, or change agent settings.
