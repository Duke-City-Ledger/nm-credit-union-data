# second/: the independent second calculation

Written blind on 2026-10-14 by OpenAI's Codex, which saw only `TASK.md`, `data/dictionary.json`, the spec and
NCUA's instructions and FPR guide, and not the engine's code. The only edit since: the two paths at lines 37 and
128, which point at this repo's `.cache/` and `data/`. Standard library only.

    python3 second.py          # writes second/out/ (gitignored)
    uv run ../scripts/compare_second.py

Its judgment calls are in `NOTES.md`. Keep it separate: fix a difference by finding which reading of NCUA is
right, and change the engine or this file only with the reason written in `docs/second-calculation.md`.
