#!/usr/bin/env python3
"""Render a self-contained project-steward dashboard from JSON."""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
from urllib.parse import urlparse
import webbrowser


STATUSES = {"active", "complete", "review", "pending", "blocked", "idle"}


def esc(value: object) -> str:
    return html.escape(str(value if value is not None else ""), quote=True)


def status_class(value: object) -> str:
    candidate = str(value or "idle").lower()
    return candidate if candidate in STATUSES else "idle"


def safe_href(value: object) -> str | None:
    href = str(value or "").strip()
    if not href:
        return None
    parsed = urlparse(href)
    if parsed.scheme and parsed.scheme not in {"http", "https"}:
        return None
    if href.startswith("//"):
        return None
    return href


def render_links(links: object) -> str:
    if not isinstance(links, list):
        return ""
    rendered: list[str] = []
    for item in links:
        if not isinstance(item, dict):
            continue
        label = esc(item.get("label", "link"))
        href = safe_href(item.get("href"))
        if href is None:
            rendered.append(f"<span>{label}</span>")
        else:
            rendered.append(f'<a href="{esc(href)}">{label}</a>')
    return " ".join(rendered)


def render_gates(gates: object) -> str:
    if not isinstance(gates, dict):
        return ""
    return " ".join(
        f'<span class="gate"><b>{esc(name)}:</b> {esc(value)}</span>'
        for name, value in gates.items()
    )


def render_screenshots(screenshots: object) -> str:
    if not isinstance(screenshots, list) or not screenshots:
        return '<span class="evidence-empty">No screenshots yet.</span>'
    rendered: list[str] = []
    for item in screenshots:
        if not isinstance(item, dict):
            continue
        href = safe_href(item.get("href"))
        label = esc(item.get("label", "Evidence"))
        caption = esc(item.get("caption", ""))
        if href is None:
            rendered.append(f'<span class="evidence-empty">{label}</span>')
        else:
            rendered.append(
                f'<a class="evidence-thumb" href="{esc(href)}" title="{caption}">'
                f'<img loading="lazy" src="{esc(href)}" alt="{label}"><span>{label}</span></a>'
            )
    return "".join(rendered) or '<span class="evidence-empty">No screenshots yet.</span>'


def require_list(data: dict[str, object], key: str) -> list[dict[str, object]]:
    value = data.get(key, [])
    if not isinstance(value, list):
        raise ValueError(f"{key} must be an array")
    if any(not isinstance(item, dict) for item in value):
        raise ValueError(f"every {key} item must be an object")
    return value


def mission_rows(missions: list[dict[str, object]]) -> str:
    if not missions:
        return '<tr><td colspan="9" class="empty">No missions recorded.</td></tr>'
    rows = []
    for mission in missions:
        state = status_class(mission.get("status"))
        rows.append(
            "<tr>"
            f'<td class="mission">{esc(mission.get("name", "Unnamed mission"))}</td>'
            f'<td>{esc(mission.get("note", ""))}</td>'
            f'<td><span class="tag {state}">{esc(mission.get("status", "idle"))}</span><br><span class="code">{esc(mission.get("session", "unassigned"))}</span></td>'
            f'<td>{esc(mission.get("phase", ""))}</td>'
            f'<td class="round">{esc(mission.get("rounds", 0))}</td>'
            f'<td>{esc(mission.get("change", ""))}<div class="correction">{esc(mission.get("corrections", ""))}</div></td>'
            f'<td>{esc(mission.get("evidence", ""))}<div class="gates">{render_gates(mission.get("gates"))}</div></td>'
            f'<td>{esc(mission.get("next", ""))}</td>'
            f'<td class="links">{render_links(mission.get("links"))}<div class="gallery">{render_screenshots(mission.get("screenshots"))}</div></td>'
            "</tr>"
        )
    return "".join(rows)


def simple_rows(items: list[dict[str, object]], columns: list[str]) -> str:
    if not items:
        return f'<tr><td colspan="{len(columns)}" class="empty">None.</td></tr>'
    return "".join(
        "<tr>" + "".join(f"<td>{esc(item.get(column, ''))}</td>" for column in columns) + "</tr>"
        for item in items
    )


def render_dashboard(data: dict[str, object]) -> str:
    title = str(data.get("title") or "Project Steward")
    missions = require_list(data, "missions")
    resources = require_list(data, "resources")
    decisions = require_list(data, "decisions")
    evolution = require_list(data, "self_evolution")
    counts = {status: 0 for status in STATUSES}
    for mission in missions:
        counts[status_class(mission.get("status"))] += 1

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <style>
    :root {{ --ink:#172032;--muted:#657086;--paper:#f3f6fb;--panel:#fff;--line:#d9e0eb;--navy:#142947;--blue:#2868d7;--green:#177557;--green-bg:#e6f6ef;--amber:#9a5b00;--amber-bg:#fff2d8;--red:#b53d46;--red-bg:#fde9eb;--gray-bg:#edf1f6; }}
    *{{box-sizing:border-box}} html{{background:var(--paper);color:var(--ink);font-family:Inter,ui-sans-serif,system-ui,-apple-system,sans-serif}} body{{margin:0;min-width:320px}} a{{color:var(--blue)}}
    .shell{{max-width:1500px;margin:auto;padding:28px}} .masthead{{padding:30px 32px;color:#f8fbff;background:var(--navy);border-radius:22px;box-shadow:0 16px 40px #17203214}}
    .eyebrow{{margin:0 0 8px;color:#9fc0fa;font:700 12px/1.4 ui-monospace,monospace;letter-spacing:.14em;text-transform:uppercase}} h1{{margin:0;font-size:clamp(28px,4vw,48px);line-height:1.08}} .lede{{max-width:850px;color:#cbd8eb;line-height:1.7}} .stamp{{color:#dce7f7;font:600 12px ui-monospace,monospace}}
    .metrics{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin:18px 0 30px}} .metric{{padding:17px 18px;background:var(--panel);border:1px solid var(--line);border-radius:15px}} .metric b{{display:block;font-size:28px}} .metric span{{color:var(--muted);font-size:12px}}
    section{{margin:28px 0}} h2{{font-size:20px}} .table-wrap{{overflow:auto;background:var(--panel);border:1px solid var(--line);border-radius:16px}} table{{width:100%;min-width:900px;border-collapse:collapse}} .mission-table{{min-width:1220px}} th{{padding:12px 14px;background:#f7f9fc;border-bottom:1px solid var(--line);color:#566276;font-size:11px;text-align:left;text-transform:uppercase}} td{{padding:14px;border-bottom:1px solid #e9edf4;font-size:13px;line-height:1.5;vertical-align:top}} .mission{{font-weight:750}} .round{{font-family:ui-monospace,monospace;text-align:center}} .code{{font:11px ui-monospace,monospace;color:#40506a}} .tag{{display:inline-flex;padding:5px 8px;border-radius:999px;font-size:11px;font-weight:750}} .active,.complete{{color:var(--green);background:var(--green-bg)}} .pending,.review{{color:var(--amber);background:var(--amber-bg)}} .blocked{{color:var(--red);background:var(--red-bg)}} .idle{{color:#5e697b;background:var(--gray-bg)}} .links>a,.links>span{{display:inline-block;margin:0 8px 6px 0}} .empty{{color:var(--muted);text-align:center}} .correction{{margin-top:8px;color:var(--red)}} .gates{{display:grid;gap:4px;margin-top:8px}} .gate{{font-size:11px}} .gallery{{display:grid;grid-template-columns:repeat(2,minmax(110px,1fr));gap:8px;margin-top:10px}} .evidence-thumb{{overflow:hidden;color:var(--ink);background:#fff;border:1px solid var(--line);border-radius:10px;text-decoration:none}} .evidence-thumb img{{display:block;width:100%;height:72px;object-fit:cover;border-bottom:1px solid var(--line)}} .evidence-thumb span{{display:block;padding:6px;font-size:10px;font-weight:700}} .evidence-empty{{padding:8px;color:var(--muted);background:#f7f9fc;border:1px dashed var(--line);border-radius:8px;font-size:10px}}
    footer{{margin-top:32px;padding-top:20px;color:var(--muted);font-size:12px;border-top:1px solid var(--line)}} @media(max-width:760px){{.shell{{padding:14px}}.masthead{{padding:24px 20px}}.metrics{{grid-template-columns:repeat(2,1fr)}}}}
  </style>
</head>
<body><main class="shell">
  <header class="masthead"><p class="eyebrow">MISSION CONTROL</p><h1>{esc(title)}</h1><p class="lede">{esc(data.get("subtitle", "Mission-oriented project control"))}</p><p class="stamp">Updated: {esc(data.get("updated_at", "not recorded"))}</p></header>
  <div class="metrics" aria-label="Project summary"><div class="metric"><b>{len(missions)}</b><span>Missions</span></div><div class="metric"><b>{counts['complete']}</b><span>Complete</span></div><div class="metric"><b>{counts['active'] + counts['review']}</b><span>Active or review</span></div><div class="metric"><b>{counts['blocked'] + counts['pending']}</b><span>Blocked or pending</span></div></div>
  <section><h2>Mission status</h2><div class="table-wrap"><table class="mission-table"><thead><tr><th>Mission</th><th>Purpose</th><th>Session</th><th>Phase</th><th>Rounds</th><th>Latest change</th><th>Evidence</th><th>Next</th><th>Links</th></tr></thead><tbody>{mission_rows(missions)}</tbody></table></div></section>
  <section><h2>Resources</h2><div class="table-wrap"><table><thead><tr><th>Resource</th><th>Count</th><th>Status</th><th>Purpose</th></tr></thead><tbody>{simple_rows(resources, ['name','count','status','purpose'])}</tbody></table></div></section>
  <section><h2>Decisions</h2><div class="table-wrap"><table><thead><tr><th>Question</th><th>Status</th><th>Recommendation</th></tr></thead><tbody>{simple_rows(decisions, ['question','status','recommendation'])}</tbody></table></div></section>
  <section><h2>Self-evolution</h2><div class="table-wrap"><table><thead><tr><th>Observed failure</th><th>Root cause</th><th>Rule change</th><th>Validation</th></tr></thead><tbody>{simple_rows(evolution, ['failure','root_cause','rule_change','validation'])}</tbody></table></div></section>
  <footer>Generated from structured JSON. Regenerate after material state changes and report those changes in conversation.</footer>
</main></body></html>"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("state", type=Path, help="Input dashboard JSON")
    parser.add_argument("output", type=Path, help="Output HTML file")
    parser.add_argument("--open", action="store_true", help="Open the rendered dashboard")
    args = parser.parse_args()

    data = json.loads(args.state.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("dashboard state must be a JSON object")
    if not str(data.get("title", "")).strip():
        raise ValueError("title is required")
    output = render_dashboard(data)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(output, encoding="utf-8")
    print(f"rendered {args.output}")
    if args.open:
        webbrowser.open(args.output.resolve().as_uri())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
