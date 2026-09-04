# Lineage and evolution contract

## Child layout

```text
<repository>/
├── .codex/skills/<child-name>/      # Full, editable project-steward copy
│   └── references/local/             # Always-owned repository rule pack
└── .steward/
    ├── lineage.json                 # Source version, child path, and local boundary
    ├── port-manifest.json           # Every source section and its disposition
    ├── base/core/                    # Immutable initial core snapshot
    └── evolutions/EV-*.json         # Durable self-evolution records
```

`base/core/` is never edited after `init`. It is the merge base for a future core-only three-way sync. `references/local/` is always owned by the child repository and is not part of that sync.

## Section disposition

Every source heading begins as `keep`. A child may change it to:

- `genericize`: preserve the mechanism while replacing project-specific identifiers.
- `move`: move detail into a child reference without losing the capability.
- `remove`: only for genuinely project-specific material; include a concrete reason.

No disposition permits silently dropping a platform collaboration mechanism.

## Evolution record

An evolution record contains: ID, timestamp, child identity, core base hash, scope, failure, root cause, rule change, evidence, validation and privacy review.

Scopes:

- `local`: valuable only inside this child repository; update `references/local/`.
- `upstream_candidate`: proposed for the canonical template after review.

The harvest report groups exact normalized rule changes. It does not declare semantic equivalence and does not modify the canonical template.

## Upstream acceptance gate

Accept an upstream candidate only if it is generic, evidence-backed, privacy-safe, non-duplicative, and tested at the level its blast radius requires. A severe platform invariant can qualify after one repository; ordinary workflow refinements should normally have evidence from more than one child or a strong general argument.
