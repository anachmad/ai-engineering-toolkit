# Documentation validation

`standards/artifacts-v1.json` indexes artifact approval and standard versions. The canonical BRD contract remains `standards/brd-v1.json`; the registry does not repeat its rules. The PRD standard, template and field rules are approved. PRD v1 checks headings and content; PRD v2 also checks local requirement fields. SRS v1, SAD v1, ADR v1 and Data Model v1 validate their approved structure and local fields; remaining artifact structures are proposed. Standard v1 selects the current BRD contract and template; it is not an immutable historical snapshot and the artifact does not embed its standard version. Preserve old versions in the registry and files before changing their meaning; a future migration needs an explicit versioning decision.

Run locally or in a pipeline:

```sh
python3 playbook validate-artifact --artifact brd --standard-version 1 --profile standard --path examples/brd-example.md
```

The command writes JSON. Exit 0 means no deterministic errors; WARN, including `TBD`, can still occur. Exit 1 means deterministic FAIL. Exit 2 means invalid command input, unapproved or unavailable version, or read/configuration error. CI must inspect `outcome` if its own policy treats WARN as blocking. No pipeline, branch protection, or lifecycle gate is installed here.

`semantic_review: NOT_RUN`, `human_approval: NOT_VERIFIED` and `release_authorized: false` are deliberate. The profile argument accepts existing identifiers only; this command does not enforce profile applicability, project quality gates, or security S1–S5. It checks only relationships encoded in one BRD; PRD v2 checks IDs and requirement fields, but PRD sources and references are not verified; cross-document references, version embedded in an artifact, authenticity of information and reviewer identities are not verified. Use the same command and canonical files from either host; host end-to-end execution for this command has not been tested.

The legacy `validate-brd` remains supported. Existing documents are not rewritten. Agents should run applicable validators and report outcomes, limitations, and unresolved findings; no external skill can change these canonical checks, but their execution is not technically mandatory unless a project configures an independent enforcement mechanism.

## Existing project ID formats

BRD v2 and PRD v3 support an explicit project format JSON file. Choose the format based on the existing project, then run, for example:

```sh
python3 playbook validate-artifact --artifact prd --standard-version 3 --profile standard --path path/to/prd.md --id-formats path/to/id-formats.json
```

The file has schema version 1 and a `formats` object keyed by `BO`, `BR`, `KPI` or `PR`. Each value is a list of `{ "prefix": "F-A", "digits": 2 }` rules. Prefixes are literal, uppercase letters, digits or hyphens, start with a letter and end with a non-digit; digits is an exact count from 1 to 12. Types not configured retain the standard default. See `examples/filio-pilot-id-formats.json` in the source repository. Old versions reject this option and retain their existing checks. The tool does not infer a format or validate source links between documents.

## Check PRD references against a selected BRD

For PRD v3, add `--brd-source path/to/brd.md` to check source IDs against the explicitly selected BRD's canonical `Business Requirements` table. Supply `--id-formats path/to/id-formats.json` when the project uses established ID formats. The source field accepts comma-separated BR IDs and other source descriptions. A matching ID only confirms its presence in that table; the tool does not establish source authority, semantic alignment, approval, or project-wide traceability. Other source descriptions remain unverified. A missing or malformed BRD table stops validation with an error; an unknown or malformed BR ID produces FAIL. Without `--brd-source`, sources remain unverified.

Existing documents such as Filio Pilot may have different headings and tables; they cannot be used as canonical BRD input without a reviewed adaptation. Never change their IDs or overwrite the original to make validation pass. `brd_source_check` records whether the selected table was checked; it is not evidence that all sources or requirements were verified.

## SRS validation

Run `python3 playbook validate-artifact --artifact srs --standard-version 1 --profile standard --path path/to/srs.md`. The SRS validator checks the approved structure, metadata and local FR/NFR tables. It reports TBD as incomplete; semantic quality, executed tests and approval are not verified.

Existing ID formats can be supplied using `--id-formats path/to/formats.json`, with `FR` and `NFR` keys as well as the previously supported types. Existing priority values can be supplied with `--srs-priorities path/to/priorities.json`, a JSON array such as `["P0", "P1"]`; `TBD` remains accepted. No mapping or format inference is performed. If no values are supplied, the SRS default priority values apply.

Use `--prd-source path/to/prd.md` to check product requirement IDs in Source against one selected PRD's canonical Product Requirements table. Missing or malformed tables stop validation; a missing ID fails. `prd_source_check` reports ID presence checking only; it does not establish source authority, semantic correctness, test execution, or approval. Other sources and sources without a selected PRD remain unverified. This command does not enforce profile applicability or security gates.

## SAD validation

When a full SAD is applicable, run `python3 playbook validate-artifact --artifact sad --standard-version 1 --profile standard --path path/to/architecture.md`. This checks headings, metadata, the four approved tables and decision status; TBD and unverified evidence produce warnings. A section that is not applicable must include a reason, subject to human review. Profile applicability is not enforced and existing architecture scaffolds remain unchanged. Links and IDs are not resolved; evidence, decisions, diagrams, security controls and human approval are not independently verified.

## SAD profile selection and staged references (v2)

SAD v2 uses the eight-heading concise contract for `lean` and the complete contract for `business-critical`. For `standard`, record `"sad_mode": "concise"` or `"sad_mode": "full"` in the project manifest after the owner selects it. Without a selection, the result reports `sad_applicability: REVIEW_REQUIRED` and does not assert structural compliance. Existing manifest fields remain unchanged; the optional field is compatible with schema v1. The concise draft is `skills/software-engineering-playbook/templates/sad-concise-template.md`. Concise metadata accepts the template table or `Title:`, `Version:`, `Status:`, `Owner:`, and `Date:` lines, optionally as Markdown bullets. For an existing Standard manifest, use `set-sad-mode` to preview and apply the choice with a reviewed manifest hash; rerun `init` to create a missing draft. Existing files are never rewritten.

Run from the toolkit root, using actual project paths:

```sh
python3 playbook validate-artifact --artifact sad --standard-version 2 --profile standard --project-root /path/to/project --path /path/to/project/docs/02-architecture/architecture.md
```

The selected manifest profile must match. Basic inline Markdown relative file links are checked within the project root; missing files and paths or symlinks escaping the root fail. External URLs and anchors are not verified. Reference-style links, complex Markdown, inline code and code fences are not checked; review them manually. To check BR or PR IDs, pass `--sad-id-sources /path/to/sources.json`, where the JSON object maps `BR` and/or `PR` to project-relative canonical source files, for example `{"BR": "docs/01-requirements/business-requirements.md"}`. Source files must contain the canonical tables; use `--id-formats` for established formats. Unknown and unselected reference types remain unverified. Matching an ID or file does not verify its content, meaning, authority, evidence or approval.

These SAD checks do not enforce security or release gates. Historical SAD v1 remains the full-structure validator.

## ADR validation

Run `python3 playbook validate-artifact --artifact adr --standard-version 1 --profile standard --path path/to/adr.md`. To use an existing project ID format, provide `--id-formats path/to/formats.json` with an `ADR` key. Add `--project-root path/to/project` for supported relative Markdown file-link checks within that project. Missing or escaping local files fail; external and unsupported references remain unverified. The validator checks a single document, not project-wide ID uniqueness or cross-document ADR IDs. It does not verify decision quality, approval, source authority, test results or release readiness. Existing decision records are not automatically migrated.

## Data model validation

A separate data model is optional; project governance determines applicability. To validate one, run `python3 playbook validate-artifact --artifact data-model --standard-version 1 --profile standard --path path/to/data-model.md`. Entity and field names are compared exactly, with case-only collisions reported as warnings. A missing entity is an error when the local catalog is complete; if it contains TBD or is unavailable, the reference remains unverified. Use `external:<source-and-entity>` for intentionally external entities; these remain unverified. The validator rejects raw HTML blocks in data model documents; use Markdown outside code fences. It does not inspect a database, authorize sensitive data, verify privacy controls, assess migrations or establish human approval.
