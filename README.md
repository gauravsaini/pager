# pager

Pager-style communication mode: ultra-short, fast to scan, easy to grasp.

Words <= 5 chars. Signs, short forms, and simple synonyms allowed. Captures intent.

Ported bench style from [caveman benchmarks](https://github.com/JuliusBrussee/caveman/blob/main/benchmarks/run.py): base vs terse vs pager, offline, no API key.

## Layout

```
pager/
  skills/pager/SKILL.md   # the skill (source of truth)
  evals/test_pager.py     # word-len + intent evals (6 cases)
  benchmarks/run.py       # EN bench: 10 tasks, base/terse/pager tokens
  benchmarks/run_zh.py    # ZH bench: 5 tasks, char cut
  benchmarks/prompts.json # 10 shared prompts
```

## Use

Add the skill dir to any skills-compatible agent (`codex`, `claude`, `cursor`, ...), or copy `skills/pager/SKILL.md` into your skill store.

Trigger: `$pager`, or say "pager mode".

Escape hatch: say "full text", "normal mode", or "verbose" to revert.

## Run evals (uv)

```bash
cd pager
uv run python evals/test_pager.py
uv run python benchmarks/run.py
uv run python benchmarks/run_zh.py
# dry-run (no compute, list tasks)
uv run python benchmarks/run.py --dry-run
```

EN bench: ~66% cut vs base, 10/10 comply. ZH bench: ~51% char cut, 5/5 pass.

## Publish

```bash
cd pager
git init -b main
git add -A
git commit -m "feat: pager skill + evals + benches"
gh repo create pager --public --source=. --push
```

## License

MIT. See `LICENSE`.
