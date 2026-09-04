# Contributing

## Source-first public adaptation

When converting a private or project-specific Skill into a public edition, do not rewrite it from memory or summarize it into a new Skill.

Use this sequence:

1. Copy the canonical source into an isolated working branch or temporary comparison file.
2. Build a section inventory before editing.
3. Classify every section as `keep`, `genericize`, `move to reference`, or `remove`.
4. Preserve all platform coordination and safety mechanisms by default.
5. Genericize project names, people, models, paths, domains, IDs, ports, and business examples.
6. Remove a section only when it is genuinely product-specific, and record the reason in the pull request.
7. Compare the final section/capability inventory against the source before publishing.
8. Run tests and the public-release scanner with additional private terms supplied through repeated `--deny` arguments.

The public adaptation must remain behaviorally equivalent for reusable capabilities. “Shorter” is not a goal when it removes task discovery, title management, event waiting, heartbeat monitoring, terminal callbacks, resource authorization, handoff, independent review, or proactive reporting.
