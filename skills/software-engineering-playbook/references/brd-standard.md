# BRD standard v1

The machine-readable formatting contract is `standards/brd-v1.json`. Use the accompanying `templates/brd-template.md`. The following level-two headings are mandatory in exactly this order and spelling. Use the prescribed tables and columns verbatim; each section must contain substantive content or `TBD`. Text may include level-three subheadings.

## Document Information

Identify the document, its owner, version, status and date.

## Executive Summary

Summarize the verified business need and intended outcome.

## Business Context

Describe verified background and cite its source or mark it TBD.

## Problem Statement

State the business problem and its impact without prescribing a solution.

## Business Objectives

List stable business objective IDs and measurable desired outcomes where known.

## Success Metrics / KPI

Define each KPI, its measurement method, objective, baseline and evidence.

## Stakeholders & Users

Identify stakeholders, user groups and their business interests.

## Current State / As-Is

Describe the verified current business situation and its evidence.

## Target State / To-Be

Describe desired business outcomes without implementation details.

## Business Requirements

List business needs with stable IDs and links to business objectives.

## Scope

Identify in-scope and out-of-scope business capabilities.

## Business Rules

Describe business policies or constraints, independently of technical design.

## Assumptions, Constraints & Dependencies

Separate assumptions, constraints and dependencies, including verification status.

## Risks & Business Impact

Describe business risks, impacts and owners where known.

## Priority & Phasing

Record business priorities and proposed phasing with their rationale.

## Acceptance / Business Readiness Criteria

State verifiable business acceptance and readiness criteria.

## Open Questions & Decisions

Separate unresolved questions from decisions and record owners and evidence.

## Traceability

Connect objective, business requirement and KPI IDs and explain gaps.

## General quality criteria

The Document Information table uses `Field | Value` and includes Title, Version, Status, Owner, and Date. The Business Objectives table uses `Objective ID | Business objective`. The Success Metrics / KPI table uses `KPI ID | Measurement definition | Business objective ID | Baseline | Evidence`. The Business Requirements table uses `Requirement ID | Business need | Business objective ID`. The Traceability table uses `Business objective ID | Business requirement ID | KPI ID`. Each requires a data row, and every cell must contain a value or `TBD`. Template placeholder rows are drafts, not requirements. Required level-three subheadings are `In scope`, `Out of scope`, `Assumptions`, `Constraints`, `Dependencies`, `Open questions`, and `Decisions`, as placed in the template; each needs content or `TBD`.

Use `BO-001`, `BR-001`, and `KPI-001` style stable IDs (at least three digits), unique within each type. Define IDs in their respective tables. Every BR must link to an existing BO, and every KPI must link to an existing BO and have a measurement definition. Use comma-separated IDs for multiple references. Traceability table references must resolve to defined IDs, and each defined BR must appear in it with an objective it references. Where KPI relationships are unknown, mark them `TBD`. Do not reuse IDs for different meanings.

Record verified information with its source, and distinguish it from assumptions, unresolved questions and approved decisions. Never invent baselines, evidence or requirements: use `TBD`. Separate business needs from proposals and omit technical implementation details. Human review must assess meaning, evidence, approval and business suitability; deterministic validation cannot prove them. `TBD` warnings and semantic-review warnings do not constitute approval or proof of completion. Correct all errors and resolve or explicitly manage warnings before declaring the BRD complete.

Run `python3 <toolkit-root>/playbook validate-brd --path <brd.md>` before completion. The validator reports errors and warnings with locations; exit 1 means errors, exit 0 means no structural errors, not approval. Existing BRDs are not overwritten; assess and migrate them with owner authorization.
