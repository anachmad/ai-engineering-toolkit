# AI Engineering Toolkit

Phase 1 provides shared engineering standards, a playbook, project-local host entry points, and a standard-library scaffolder. Python 3.11+ is required. No third-party tooling is installed.

From this repository, generate examples in new directories:

```sh
python3 -m playbook init --path /tmp/aet-lean --profile lean --name "Lean example"
python3 -m playbook init --path /tmp/aet-standard --profile standard --name "Standard example"
python3 -m playbook audit --path /tmp/aet-standard
python3 -m unittest discover -s tests -v
```

Audit an existing repository without a manifest with `python3 -m playbook audit --path /path/to/project --profile standard`; this performs no writes. Add `--ui` when a UI exists. Without it UI applicability remains undecided; audit reports this for human review. Existing files are never overwritten; inspect conflicts and use the playbook to propose reviewed patches. Generated documents are drafts with unknowns, not requirements or evidence.

`adapters/claude` and `adapters/codex` contain project-local skill entry points referencing the shared skill. The repository-local `.agents/skills/` and `.claude/skills/` entries link to those adapters. Discovery, invocation, initialization and auditing were exercised with both hosts using disposable projects. Restart an existing agent session if it does not see a newly added skill. The manifest records this toolkit's absolute standards path, which must be updated if moved or shared with another machine. See [architecture](docs/architecture.md) and the [specification](specifications/AI_Engineering_Toolkit_Architecture_Integration_Spec_v1.md).

Policy and project manifests use JSON-formatted YAML, validated by the scaffolder with Python standard-library checks. Document prompts live in `standards/document-prompts.yaml`; generated drafts need project-specific information and review.
