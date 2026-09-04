# Prompt maintenance profile

Use this profile when a Mission changes model-visible instructions, routing, examples, tool guidance, or error recovery.

## Establish the instruction map

Identify every model-visible layer used by the repository, such as global/system instructions, workflow instructions, on-demand knowledge, tool prompts, sub-agent prompts, and runtime error guidance. Record how they are composed and which layers are always loaded.

For each duplicated rule, choose one authoritative layer:

- Global/system: behavior needed across nearly every workflow.
- Workflow: method or routing needed only in one workflow family.
- On-demand knowledge: long, conditional operating detail.
- Tool or sub-agent prompt: contracts for that specific model/tool boundary.
- Runtime error guidance: recovery instructions needed only after a detected failure.

Keep one authoritative body. Other layers may contain only the shortest necessary trigger or pointer. A document cannot be the authoritative load trigger if the model sees it only after loading it.

## Small-batch loop

1. Capture character/token size by layer and the composed baseline.
2. Freeze the affected workflows, decisions, tools, and behavioral cases.
3. Remove obsolete or duplicated text before adding replacement text.
4. Make one attributable migration batch.
5. Run directly related deterministic tests.
6. Re-run positive, negative, and boundary cases for every moved or deleted rule.
7. Run a minimal real-model comparison when routing, planning, tool choice, or generation behavior may change.
8. Have an independent reviewer check placement, duplication, size delta, and behavioral evidence.

Do not use string-presence assertions as the sole behavioral proof. They can protect a contract anchor, but observable model decisions require behavioral cases.

If a batch fails, revisit ownership or narrow the change. Do not restore a large always-on block merely to make a case pass. Keep experiment objectives, cases, metrics, model settings, cost limits, and stopping conditions explicit before paid or large evaluations.
