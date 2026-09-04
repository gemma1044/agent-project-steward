# Dashboard state schema

The renderer accepts one UTF-8 JSON object.

```json
{
  "title": "Project Steward",
  "subtitle": "Mission-oriented project control",
  "updated_at": "2026-01-01 12:00 UTC",
  "missions": [
    {
      "name": "Reduce always-on instructions",
      "note": "Move workflow-only guidance out of the global layer.",
      "status": "active",
      "phase": "baseline",
      "session": "worker-session",
      "rounds": 2,
      "change": "Mapped three duplicate rules.",
      "corrections": "Rejected a second instruction-loading path.",
      "evidence": "Baseline report saved.",
      "gates": {
        "implementation": "pending",
        "tests": "pass",
        "real_path": "pending",
        "reviewable_evidence": "pass",
        "independent_review": "pending"
      },
      "next": "Freeze the first migration batch.",
      "links": [{"label": "Report", "href": "reports/baseline.md"}],
      "screenshots": [{"label": "Baseline", "href": "evidence/baseline.png", "caption": "Initial state"}]
    }
  ],
  "resources": [
    {"name": "Worker sessions", "count": 1, "status": "approved", "purpose": "Implementation"}
  ],
  "decisions": [
    {"question": "Approve one worker session?", "status": "pending", "recommendation": "Approve"}
  ],
  "self_evolution": [
    {"failure": "A completed session did not report back.", "root_cause": "The callback was optional.", "rule_change": "Require a final message-tool callback.", "validation": "Forward test passed."}
  ]
}
```

Required top-level fields: `title`, `missions`. Other fields default to empty values.

Mission statuses: `active`, `complete`, `review`, `pending`, `blocked`, `idle`. Unknown statuses render as `idle`.

The five gate keys are examples rather than schema-enforced names. Keep them stable within one project. `screenshots` belong to their Mission; do not create a global evidence gallery that loses attribution. `self_evolution` records reusable governance failures and their validated rule changes.

All values are HTML-escaped. Links may use `http`, `https`, or relative paths; other URI schemes are rendered as plain text.
