# Lineage and evolution contract

## Child layout

```text
<repository>/
├── .codex/skills/<child-name>/      # Full, editable project-steward copy
└── .steward/
    ├── lineage.json                 # Source version and child path
    ├── port-manifest.json           # Every source section and its disposition
    ├── base/<child-name>/            # Immutable initial template snapshot
    └── evolutions/EV-*.json         # Durable self-evolution records
```

`base/<child-name>` is never edited after `init`. It is the merge base for a future three-way sync.

## Section disposition

Every source heading begins as `keep`. A child may change it to:

- `genericize`: preserve the mechanism while replacing project-specific identifiers.
- `move`: move detail into a child reference without losing the capability.
- `remove`: only for genuinely project-specific material; include a concrete reason.

No disposition permits silently dropping a platform collaboration mechanism.

## Evolution record

An evolution record contains: ID, timestamp, child identity, base hash, scope, failure, root cause, rule change, evidence, validation and privacy review.

Scopes:

- `local`: valuable only inside this child repository.
- `upstream_candidate`: proposed for the canonical template after review.

The harvest report groups exact normalized rule changes. It does not declare semantic equivalence and does not modify the canonical template.

## Upstream acceptance gate

Accept an upstream candidate only if it is generic, evidence-backed, privacy-safe, non-duplicative, and tested at the level its blast radius requires. A severe platform invariant can qualify after one repository; ordinary workflow refinements should normally have evidence from more than one child or a strong general argument.
