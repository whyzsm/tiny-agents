# Xueba Model Eval Workflow

Use this workflow when checking actual model behavior, not just deterministic file structure.

## Boundary

`scripts/run_evals.py` proves that the skill package is structurally valid. It does not prove that a model will produce high-quality study notes or agent-boundary answers.

Model-output evaluation requires real executor runs, grading, aggregation, and a review page. Do not call this complete until outputs and `grading.json` files exist.

## Prepare workspace

```bash
python3 scripts/prepare_model_eval_workspace.py
```

Default core eval IDs:

```text
2,4,6,7,9,10,11,13
```

These cover pasted learning material, vault upgrade report mode, authenticated-source handling, temporary-path leakage, technical note quality, Learning Expert Mode, Agent Design Mode, and Runtime Harness Mode.

The script creates a sibling workspace:

```text
xueba-workspace/
  skill-current/
  skill-baseline-9b38d23/
  iteration-1/
    eval-*/
      with_skill/run-1/
      old_skill/run-1/
  run_with_codex.sh
  generate_viewer.sh
  MODEL_EVAL_RUNBOOK.md
```

## Run model outputs

```bash
../xueba-workspace/run_with_codex.sh
```

Each run writes `outputs/final.md`. During eval, runs are instructed not to modify the user's real Obsidian vault; they should write intended notes, reports, or specs inside the output directory.

The generated script defaults to `CODEX_EXEC_ARGS=--dangerously-bypass-approvals-and-sandbox` because the current Codex CLI non-interactive command does not expose `--ask-for-approval never`. Override `CODEX_EXEC_ARGS` when a local safer non-interactive profile is available.

## Grade outputs

For every run directory, create `grading.json` from `grading.template.json` after inspecting output files.

The required grading fields are:

- `expectations[].text`
- `expectations[].passed`
- `expectations[].evidence`
- `summary.passed`
- `summary.failed`
- `summary.total`
- `summary.pass_rate`

Do not copy template grades as final grades. A run is ungraded until a reviewer has checked the outputs.

## Generate benchmark and viewer

```bash
../xueba-workspace/generate_viewer.sh
```

This runs skill-creator's benchmark aggregator and static review page generator. Expected outputs:

- `iteration-1/benchmark.json`
- `iteration-1/benchmark.md`
- `iteration-1/review.html`

The viewer script auto-detects Python 3.10+ through `PYTHON_BIN`, `python3.12`, `python3.11`, then `python3`. Set `PYTHON_BIN` explicitly if the system default `python3` is older.

## Release rule

The release may say deterministic checks pass after `run_evals.py` succeeds.

It may say behavior is model-evaluated only after:

- model output files exist
- `grading.json` files exist
- benchmark is generated
- `review.html` is generated
- user or reviewer feedback has been read
