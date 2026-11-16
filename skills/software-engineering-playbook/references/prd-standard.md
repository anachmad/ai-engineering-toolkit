# PRD standard v1 — approved standard and template

The user approved this PRD standard and its accompanying template on 2026-11-04. The 20 level-two headings and their order are approved. The machine-readable heading contract is `standards/prd-v1.json`. The descriptions below are guidance. Detailed field rules are approved and enforced by PRD contract v2; cross-document validation remains unimplemented. Use the shared PRD template.

## Document Information

Identify title, version, status, owner and date.

## Executive Summary

Summarize the product problem and intended outcomes.

## Product Background & Context

Record product background, context and source evidence.

## Product Vision & Goals

Describe the vision and goals, identifying relevant business objectives.

## Target Users & Personas

Identify user groups, stakeholders and personas supported by evidence.

## User Problems & Needs

Describe user problems and needs and distinguish assumptions from facts.

## Product Scope

State what is in and out of product scope.

## Product Features & Capabilities

Describe product capabilities without duplicating requirements.

## User Journeys & Workflows

Describe relevant journeys and workflows.

## Product Requirements

List stable product requirement IDs, description, source, priority, actor, acceptance criteria and status.

## User Stories & Use Cases

Describe relevant stories and use cases, linking product requirements.

## Business Rules

Record relevant business rules and sources.

## Data & Information Requirements

Describe product information and data needs.

## UX/UI Requirements

Describe applicable user experience and accessibility needs.

## Non-Functional Expectations

Describe product quality expectations and measurable targets where known.

## Integration Requirements

Describe applicable integration needs and dependencies.

## Success Metrics & Analytics

Define success measures, measurement method, source and baseline where known.

## Assumptions, Constraints & Dependencies

Separate assumptions, constraints and dependencies.

## Risks, Open Questions & Decisions

Separate risks, unresolved questions and decisions.

## Acceptance & Traceability

Record acceptance criteria and traceability to sources and verification.

## General guidance and limitations

Use stable product requirement IDs. Follow `skills/software-engineering-playbook/references/requirement-id-compatibility.md`; `PR-001` is the default when no prior format exists. For each product requirement record the description, source requirement or authorized source, priority, actor or stakeholder, acceptance criteria and status. Link business requirements where applicable; Lean projects can use combined requirements. Unknown information is `TBD`; never invent evidence, targets or approvals. Separate verified facts from assumptions, open questions and decisions. Human review is necessary for product meaning, completeness, acceptance and approval. PRD contract v1 checks section structure only. Contract v2 also checks the seven requirement fields, local ID format and uniqueness, priority and status; it does not verify cross-document relationships, semantics, applicability or approval. See `docs/proposals/prd-requirement-rules.md` in the source repository for the approved field rules.

## Approved PRD requirement fields (contract v2)

The Product Requirements table has the seven columns shown in the template. Each requirement ID is unique within the document and remains stable; use the existing project format where present, otherwise use the `PR-001` default; retired IDs are not reused. Record a description, source, priority, actor or stakeholder, acceptance criteria and status. Separate multiple acceptance criteria with `<br>`. Source may refer to a BR or an owner-authorized external source; its authority and existence require review.

Priority is `Must`, `Should`, `Could`, or `TBD`. Requirement status is `Draft`, `In review`, `Approved`, `Deferred`, or `TBD`; `Approved` is a claim, not independently verified approval. These are requirement statuses, separate from the canonical document statuses. All seven cells need values; use `TBD` for unknowns. A fully TBD row is a draft placeholder and produces a warning. Sources, semantic quality, cross-document links, and human approval are not verified by local checks.
