---
name: software-engineering-playbook
description: Initialize, audit, or refresh project engineering documentation using canonical risk-based standards.
---

# Software engineering playbook

The toolkit root is supplied by the adapter; when loading this shared file directly, it is two directories above its containing skill directory. Read `standards/documentation-standard.md`, `standards/profiles.yaml`, and `standards/quality-gates.yaml` from that root before acting. The project manifest identifies its profile and canonical standards location. Resolve conflicts using the policy precedence in the documentation standard.

- **Initialize:** inspect the repository and existing documentation, select or confirm the profile with the owner, and propose the artifact manifest. Run `python3 <toolkit-root>/playbook init` for missing artifacts, passing the project path explicitly; inspect existing documentation and reference material, reconcile it with canonical docs without moving or overwriting sources, and preserve existing files. Ask about UI applicability and risk escalation. Mark unknowns TBD.
- **Audit-upgrade:** run `python3 <toolkit-root>/playbook audit` with the project path, then inspect content, approvals, traceability and conflicting requirements. Report gaps and a safe, reviewable change plan; file presence alone is not compliance.
- **Refresh:** identify affected requirements, architecture, decisions, tests and operations; propose a reviewed patch. Obtain authorized review for substantive changes to approved documents.

Do not treat generated placeholders as evidence, invent business requirements, install external tools, or change agent settings.
