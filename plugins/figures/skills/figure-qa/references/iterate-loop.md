# Iterate Loop

The generate, QA, fix, regenerate loop that `figures:ai-full-figure` follows for every AI-generated figure. This reference is owned by `figure-qa` because the loop's fix decisions come directly out of the QA report's JSON block (`figure-qa-procedure.md`, steps 5 and 6); `ai-full-figure` points here rather than duplicating the contract.

The orchestrating skill (`ai-full-figure`) drives the loop. It never QAs its own output; every quality judgment comes from a fresh-context `figure-qa` reviewer, dispatched as described below.

## Contract

1. **Generate N candidates in parallel.** `N` defaults to 2, with a maximum of 4. Each candidate is a separate `generate_figure.py` run with the same prompt and theme; run them concurrently as background shell jobs rather than sequentially; there is no shared state between candidates to serialize on.
2. **QA every candidate in one dispatch.** Send all `N` QA calls in a single message, as parallel `Agent(subagent_type: "figures:figure-qa", model: sonnet)` invocations, one per candidate. Do not QA candidates one at a time; the whole point of generating N candidates is to judge them together.
3. **Rank the QA'd candidates**, in this order:
   1. `status`: `ship` beats `revise` beats `block`.
   2. Fewer `block`-severity findings wins a tie on `status`.
   3. Higher sum of the five `vlm` scores wins a tie on both of the above.
4. **Pick the best-ranked candidate.** If its `status` is `ship`, stop here; report it.
5. **If not `ship`, apply exactly one targeted change** to the best candidate, chosen from its JSON `findings[]` (the highest-severity finding first, using its `action` and `hint` verbatim):
   - `action: "edit"`: `generate_figure.py --edit best.png "<hint>"`.
   - `action: "regenerate"`: rerun `generate_figure.py` with the prompt amended per `<hint>` (for example, a verbatim text block spelled letter by letter, or palette lines moved earlier).
   - `action: "overlay"`: move the string or label named in `<hint>` out of the generation prompt and into the `overlay_labels.py` labels JSON, then rerun the overlay step.
   - `action: "rescale"`: raise the `font_size_pt` or panel scale named in `<hint>`.
   - `action: "recolor"`: apply the recolor instruction in `<hint>` (an `--edit` call, or a prompt palette-line reorder, per the finding-to-action table).
   One change per iteration, not a batch of every open finding; re-QA before deciding the next change, because fixing one finding can shift the ranking or reveal another.
6. **Re-QA** the single changed candidate (a single `figures:figure-qa` dispatch, not the full N-way fan-out again) and re-rank it against the other candidates' last known results.
7. **Stop at `ship`, or after `max_iter` iterations** (default 3, counted from the first QA pass). Whichever comes first ends the loop.
8. **Report the best candidate**: its file path, its remaining findings (empty if `ship`), and the manifest of every prompt used across every generation and edit call in the loop (so the sequence of changes is reproducible and auditable).

## Worker briefing (send this to every QA agent)

Every `figures:figure-qa` dispatch in step 2 and step 6 gets the same briefing shape, with only the candidate path varying across the parallel calls in step 2:

```
Figure path: <candidate path, e.g. out/candidate-2.png>
Target journal: <nature | science | cell | pnas | generic>
Theme path: <path to theme.json, or "none">
Expected verbatim strings: <list every --text string requested for this candidate, or "none">
no-qa: not set (this dispatch always requires a QA pass; only pass no-qa when the caller explicitly opted out upstream of the loop)
```

Do not shorten this to just the figure path. `figure-qa-procedure.md`'s raster text check only runs when it is told which strings to expect; omitting them silently turns off the text branch and produces a false `ship`.

## Model routing

Candidate generation and every QA dispatch run on the Sonnet tier (`model: sonnet` on the `Agent` call, or the equivalent worker-tier model on Codex/Copilot). The orchestrating model, whichever tier is driving `ai-full-figure` itself, does the ranking, the fix selection, and the final report; it does not delegate those judgment calls, because they are exactly the "pick the best candidate" and "which one change" decisions that make the loop worth running. See `project:agent-fanout` for the general worker-tier routing rule this follows.

## Cross-agent fallback

Claude Code dispatches step 2 and step 6 as parallel `Agent` calls to the `figures:figure-qa` agent. Codex and Copilot CLI plugin installs expose `figure-qa` as a skill, not a subagent (see `figure-qa`'s own `SKILL.md` dispatch section); on those platforms, run the QA procedure inline, once per candidate, sequentially, rather than in parallel. The rest of the contract (ranking, one targeted change per iteration, `max_iter`, the final report) is unchanged; only the QA dispatch mechanism differs.

## Stopping conditions summary

| Condition | Outcome |
|---|---|
| Best candidate's `status` is `ship` | Stop immediately; report it. |
| `max_iter` iterations completed and no candidate reached `ship` | Stop; report the best-ranked candidate (by the step 3 ordering) with its remaining findings. |
| A generation or edit call fails outright (script error, missing dependency, backend timeout) | Do not count it as an iteration; report the failure and continue with the remaining candidates, or stop and report if none remain. |
