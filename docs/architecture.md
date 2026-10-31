# Phase 1 architecture

The shared playbook and versioned canonical standards are authoritative. Both project-local host entry points reference the same skill. The Python standard-library scaffolder consumes JSON-formatted YAML (a YAML subset) and shared templates. It creates only missing files, rejects symlink traversal, and reports conflicts. Audit checks presence, not approval or actual gate compliance.

Native agent discovery, invocation, initialization and auditing were exercised with both installed hosts using disposable projects; results depend on the host environment. Schema checks validate the supported version and required fields, not full YAML or arbitrary JSON Schema. Router, manager, integrations, GitLab enforcement and vendor tooling belong to later phases.
