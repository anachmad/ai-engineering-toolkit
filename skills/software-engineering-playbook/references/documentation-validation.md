# Documentation validation

`standards/artifacts-v1.json` indexes artifact approval and standard versions. The canonical BRD contract remains `standards/brd-v1.json`; the registry does not repeat its rules. The PRD standard, template and field rules are approved. PRD v1 checks headings and content; PRD v2 also checks local requirement fields. Other structures are proposed and cannot be validated as approved standards. Standard v1 selects the current BRD contract and template; it is not an immutable historical snapshot and the artifact does not embed its standard version. Preserve old versions in the registry and files before changing their meaning; a future migration needs an explicit versioning decision.

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
