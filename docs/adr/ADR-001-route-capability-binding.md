# ADR-001: Optional route capability binding

Status: draft
Decision: proposed for Phase 2.1 review
Decision owner: engineering owner
Scope: orchestration configuration validation; no external installation or execution.

## Context

Routes select skills by registry ID. A newly registered skill can be selected even if its declared capabilities do not include the capability intended by the route. Host compatibility and review attestations alone do not establish that the skill provides that capability.

## Decision

Allow a route to declare an optional `capability` string. When present, policy validation requires the configured primary skill to list that exact capability. A mismatch or invalid value rejects the configuration before routing. The capability declaration is metadata, not independently verified behavior. Existing routes without this field retain their current interpretation; no automatic migration or inference is performed. Runtime availability and host compatibility checks remain necessary and distinct.

The release-governance pseudo-owner is not a skill and cannot be capability-bound. Project owners review configuration changes. The existing canonical quality gates and mandatory security gates remain authoritative and are not replaced by a capability declaration.

## Consequences

A new toolkit can be registered and bound by configuration without modifying router source. This adds a fail-closed check for routes that opt in, while leaving legacy routes backward compatible. Future work may decide whether capability bindings should become mandatory in a new policy version; doing so is outside this change.
