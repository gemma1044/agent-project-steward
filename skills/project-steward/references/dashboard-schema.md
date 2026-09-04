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
      "evidence": "Baseline report saved.",
      "next": "Freeze the first migration batch.",
      "links": [{"label": "Report", "href": "reports/baseline.md"}]
    }
  ],
  "resources": [
    {"name": "Worker sessions", "count": 1, "status": "approved", "purpose": "Implementation"}
  ],
  "decisions": [
    {"question": "Approve one worker session?", "status": "pending", "recommendation": "Approve"}
  ]
}
```

Required top-level fields: `title`, `missions`. Other fields default to empty values.

Mission statuses: `active`, `complete`, `review`, `pending`, `blocked`, `idle`. Unknown statuses render as `idle`.

All values are HTML-escaped. Links may use `http`, `https`, or relative paths; other URI schemes are rendered as plain text.
