# Documentation validation

`standards/artifacts-v1.json` indexes artifact approval and standard versions. The canonical BRD contract remains `standards/brd-v1.json`; the registry does not repeat its rules. PRD section structure is also approved; its validator checks headings and content only. Other structures are proposed and cannot be validated as approved standards. Standard v1 selects the current BRD contract and template; it is not an immutable historical snapshot and the artifact does not embed its standard version. Preserve old versions in the registry and files before changing their meaning; a future migration needs an explicit versioning decision.

Run locally or in a pipeline:

```sh
python3 playbook validate-artifact --artifact brd --standard-version 1 --profile standard --path examples/brd-example.md
```

The command writes JSON. Exit 0 means no deterministic errors; WARN, including `TBD`, can still occur. Exit 1 means deterministic FAIL. Exit 2 means invalid command input, unapproved or unavailable version, or read/configuration error. CI must inspect `outcome` if its own policy treats WARN as blocking. No pipeline, branch protection, or lifecycle gate is installed here.

`semantic_review: NOT_RUN`, `human_approval: NOT_VERIFIED` and `release_authorized: false` are deliberate. The profile argument accepts existing identifiers only; this command does not enforce profile applicability, project quality gates, or security S1–S5. It checks only relationships encoded in one BRD; PRD IDs, required fields and references are not validated; cross-document references, version embedded in an artifact, authenticity of information and reviewer identities are not verified. Use the same command and canonical files from either host; host end-to-end execution for this command has not been tested.

The legacy `validate-brd` remains supported. Existing documents are not rewritten. Agents should run applicable validators and report outcomes, limitations, and unresolved findings; no external skill can change these canonical checks, but their execution is not technically mandatory unless a project configures an independent enforcement mechanism.
