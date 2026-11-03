# AI Engineering Toolkit

A shared set of engineering standards and documentation tools for teams working with **Codex** and **Claude Code**.

The toolkit helps you start a project's documentation, review an existing project's gaps, and keep decisions connected to requirements and evidence. It is an early foundation: the documentation playbook, scaffolder, local workflow router, and security evidence evaluator are available now. Third-party toolkit installation and CI enforcement are not implemented.

## Why this exists

AI coding agents can help teams move quickly, but speed alone does not ensure that a project has clear requirements, recorded decisions, appropriate tests, or a safe way to operate and release it. Different agents can also receive different instructions, leaving teams with inconsistent documentation and duplicated standards.

This toolkit gives both agents one canonical set of engineering standards. It also recognizes that projects have different levels of risk: a small internal experiment should not need the same documentation as a business-critical service. The goal is to make the important work visible and reviewable without filling a repository with invented requirements or empty approvals.

## What you can do today

- **Initialize** a project with a manifest, agent instructions, and draft documentation appropriate to its risk profile.
- **Audit** an existing project for missing artifacts and use the playbook to review its content, approvals, and evidence.
- **Refresh** documentation with an agent after requirements or architecture change, using a reviewed patch.
- **Share one standard** between Codex and Claude Code through the same playbook and policy files.

The scaffolder creates missing files and preserves existing files. Generated documents contain `TBD` prompts: your team supplies the actual requirements, decisions, approvals, and evidence. A generated file or a successful presence check does not mean a project is compliant or ready to release.

## Choose a profile

| Profile | When to consider it | What it adds |
| --- | --- | --- |
| **Lean** | Small, lower-risk work | Concise requirements, architecture, verification, and run instructions. |
| **Standard** | Most projects; the proposed default | Separate requirements documents, architecture decisions, traceability, security review, and operational guidance. |
| **Business Critical** | Projects with high business, safety, legal, security, or outage impact | Additional approval, threat-model, access-control, and recovery documentation. |

Choose the profile with the project owner. Sensitive data, financial integrity, operational safety, legal obligations, and outage impact may require a higher profile. A complex user interface alone does not make a project Business Critical. See the [documentation standard](standards/documentation-standard.md) and [quality gates](standards/quality-gates.yaml) for the full expectations.

## Get started

You need **Python 3.11 or newer** and a local copy of this repository. No third-party Python packages are required.

```sh
git clone git@github.com:anachmad/ai-engineering-toolkit.git
cd ai-engineering-toolkit
python3 --version
```

Run the commands below from the toolkit directory. Replace the example paths and names with your own. The project path can point to a new directory or an existing project; existing files will be preserved.

### 1. Generate project documentation

For a small, lower-risk project:

```sh
python3 -m playbook init \
  --path /tmp/my-lean-project \
  --profile lean \
  --name "My Lean Project"
```

For a Standard project:

```sh
python3 -m playbook init \
  --path /tmp/my-standard-project \
  --profile standard \
  --name "My Standard Project"
```

Add `--ui` if the project has a user interface; this includes a UI/UX document. Without it, the manifest records UI applicability as unknown and the audit asks for review. Use `--profile business-critical` when that profile is appropriate.

The generated project includes a `.engineering/project.yaml` manifest, `AGENTS.md`, `CLAUDE.md`, and documents under `docs/`. The `docs/08-reference/` directory provides a home for supporting source material; keep authoritative requirements and architecture documents linked and clearly identified. Open the drafts with your team and replace the `TBD` prompts with information you have actually agreed upon. A manifest records the standards location; a shared-project setup uses a project-relative path, while a standalone toolkit uses an absolute path. Review it if the toolkit moves or the project is used on another machine.

### Update UI applicability

When a project was initialized with UI applicability unknown, preview a change first:

```sh
python3 -m playbook set-ui --path /path/to/project --ui yes
```

After reviewing the preview and authorizing the manifest change, repeat the command with `--apply --expected-sha256 <hash>` using the hash printed by the preview. A changed manifest requires a new preview. The command preserves an existing UI document. Selecting `no` does not delete an existing document. A failure during application can leave a newly created UI draft in place; review the project before retrying.

### 2. Audit a project

For a project initialized by the toolkit:

```sh
python3 -m playbook audit --path /tmp/my-standard-project
```

For an existing project without a manifest, provide the profile you want to assess:

```sh
python3 -m playbook audit --path /path/to/existing-project --profile standard
```

The command reports which expected files are present or missing and flags items that need human review. It does not modify the project. An audit exits with status `1` when required files are missing and `2` for an invalid manifest or another error. Inspect document content and evidence separately; file presence alone is not compliance.

### 3. Use the playbook with an agent

Start Codex or Claude Code **in this toolkit repository**. The repository contains project-local skill entry points for both hosts; no global agent configuration is required. If a session was already running when the skill was added, restart it.

Ask the agent to use the playbook and identify the project and profile. For example:

```text
Use the software-engineering-playbook to audit /path/to/my-project
against the Standard profile. Report gaps and a safe plan; don't edit files.
```

For a new project, ask it to initialize the project at a specific path and provide the selected profile and name. For an existing project, ask for an audit first. The playbook also supports proposing documentation updates after a change; substantive changes to approved documents need authorized review.

The repository includes local skill links for use here. For another project, link its `.agents/skills/software-engineering-playbook` (Codex) or `.claude/skills/software-engineering-playbook` (Claude Code) to the corresponding adapter directory in this toolkit. The link must point to the adapter directory itself; keep this toolkit checkout available at that path. Claude Code may require access to the toolkit directory when the project is elsewhere, for example `claude --add-dir /path/to/ai-engineering-toolkit`. The generated project instructions refer to the canonical standards, but the scaffolder does not install the playbook into other projects or configure either agent globally.

## Set up a shared project

A team can keep its own copy of the toolkit inside a project, so both agents use the same project-owned standards without depending on one developer's machine. From this toolkit checkout, run:

```sh
python3 -m playbook share --path /path/to/existing-project
```

The target directory must exist. This creates `.engineering/toolkit/` and relative links in `.agents/skills/` and `.claude/skills/`. Review and commit the toolkit copy and both links with the project. The command stops if any of those destinations already exists; it does not merge or overwrite existing content. If a copy fails partway through, inspect the reported paths before retrying.

For a new project, initialize it using the project-owned copy:

```sh
cd /path/to/existing-project
python3 .engineering/toolkit/playbook init --path . --profile standard --name "My Project"
python3 .engineering/toolkit/playbook audit --path .
```

The manifest created this way records a project-relative standards path, so the project can be moved or cloned. An existing manifest is preserved and is not automatically migrated. The project owns its toolkit copy: `provenance.json` records hashes of the copied files, including any uncommitted source changes. Review updates and commit them like any other project change; the hashes do not prove a release or approval. This command does not install third-party toolkits or automatically update copies. Relative skill links require filesystem symlink support; Windows and WSL have not been verified.

If both user-level and project-level skills have the same name, choose the project-local skill when the host offers a choice, so the project's checked-in standards apply. Claude Code may ask permission to access files or run commands.

## Security and workflow routing

Use the [Phase 2 guide](docs/phase-2-orchestration.md) to classify risk, inspect configured skills, route a task, and evaluate recorded security evidence. The router does not run external skills; an enabled integration is not necessarily installed, compatible, or approved. Missing required evidence blocks the relevant evaluation.

## Verify the toolkit

Run the automated checks from the toolkit directory:

```sh
python3 -m unittest discover -s tests -v
```

The tests cover scaffolding, preservation of existing documents, profile and manifest validation, and both adapters' references to the shared playbook. Codex and Claude Code have also been exercised separately with disposable initialization and audit examples.

## Where to find things

| Location | Purpose |
| --- | --- |
| [`standards/`](standards/) | Canonical profiles, documentation rules, quality gates, and document prompts. |
| [`skills/software-engineering-playbook/`](skills/software-engineering-playbook/) | Shared agent workflow for initialization, audit, and refresh. |
| [`adapters/`](adapters/) | Lightweight Claude Code and Codex entry points. |
| [`templates/project/`](templates/project/) | Templates used to generate project documentation. |
| [`playbook/`](playbook/) | Python scaffolder and audit command. |
| [`tests/`](tests/) | Automated validation tests. |

Policy and manifest files use JSON-formatted YAML, so the scaffolder can validate them with Python's standard library. For design details and planned phases, see the [architecture notes](docs/architecture.md) and [architecture and integration specification](specifications/AI_Engineering_Toolkit_Architecture_Integration_Spec_v1.md).
