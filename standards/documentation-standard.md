# Documentation standard

Version: 1. Policy precedence is repository safety and explicit human approvals, approved project requirements and architecture plus these standards, project adapter instructions, then upstream workflows.

Use Git and merge requests for review. Mark documents draft, in-review, approved, or deprecated. Authorized reviewers must approve substantive changes to approved documents. Record unknowns as TBD, never as invented requirements or completed evidence. Use stable BR-, FR-, NFR-, ADR-, TC-, and RSK- identifiers when applicable. Link requirements through changes, code, test evidence, and release records; GitLab issues and merge requests track execution rather than duplicating a backlog.

Select a profile with the project owner; Standard is the proposed default, not an approval. Escalate for sensitive data, financial integrity, operational safety, legal obligations, or high outage impact. Complex UI alone does not imply Business Critical. Include UI/UX requirements when a UI exists, including accessibility and material approvals for Business Critical.

Lean permits combined requirements and a concise architecture. Standard uses distinct or linked non-duplicative BRD, PRD, and SRD, significant ADRs, requirement IDs and critical-test links. Business Critical requires distinct approved and traceable requirements, accountable signoff, independent architecture and security review, threat model, access matrix, abuse cases, RPO/RTO, restore tests, observability, disaster recovery, and separate business and technical release approvals. Each gate requires machine results or signed human records; placeholders are not evidence. No profile permits secrets exposure or unauthorized production deployment.
