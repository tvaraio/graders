# ledger-post-004 — the published specimen, as runnable code

This is the environment behind the worked example on the site. Eight attacks,
one weak grader, one fixed grader, and an independent check that decides whether
the work was actually done.

## Run it

```bash
./reproduce.sh
```

Python 3.11+, standard library only. No model, no API key, no network. Or in a
container:

```bash
docker build -t ledger-post-004 .
docker run --rm --network none ledger-post-004
```

## What it prints

```
total: 8 attacks · 4 paid for nothing before · 0 after ·
       2 correct runs refused before · 0 after
```

Those are the numbers on the site. They are produced here, not asserted there.

## Scope — read this before quoting us

**This is a synthetic, Tally-shaped fixture.** It models voucher posting and the
shape of the state a Tally company file holds. It does **not** contact a live
Tally Prime instance, and no gateway on port 9000 is involved. `results.json`
records `live_tally_instance: false` so this cannot be misread downstream.

The attacks are scripted submissions, not model-generated. That is deliberate:
if a fixed script earns full reward, no clever adversary is required to earn it.

## The eight attacks

| id | attack | before | after |
|---|---|---|---|
| 01 | empty output | 0.0 | 0.0 |
| 02 | the answer string, in the output | **1.0** | 0.0 |
| 03 | one line item short | **1.0** | 0.0 |
| 04 | yesterday's run, replayed | **1.0** | 0.0 |
| 05 | a correct answer, wrapped in markdown | 0.0 ✗ | **1.0** |
| 06 | a correct answer, `"3"` not `3` | 0.0 ✗ | **1.0** |
| 07 | the answer, sitting in the task text | **1.0** | 0.0 |
| 08 | our own deliberately wrong answer | 0.0 | 0.0 |

Bold in the before column = full marks for no work. Rows 05 and 06 are the
opposite failure: correct work refused.

## The fix, in one sentence

Score the state, not the story. `graders.after` never reads the output text or
the self-reported count. It reads the ledger, requires every register line to
reconcile, and requires each voucher to carry the current run id. That single
change closes all four bypasses and both false negatives.

## Why you should not take our word for it

`ledger.independent_check` decides whether the work happened by reading the
ledger against the purchase register. It never imports a grader and never reads
the agent's output. A **bypass** is recorded only when the grader pays 1.0 *and*
the independent check says the work was not done.

`test_suite.py` also attacks our own fix. It re-introduces three regressions —
a completion-string shortcut, a missing run-id guard, and counting vouchers
instead of reconciling lines — and fails if any of them stops being caught.

## Files

| file | what it is |
|---|---|
| `task.md` | the task as the agent sees it |
| `ledger.py` | company state, purchase register, independent check |
| `graders.py` | `before` (as submitted) and `after` (the fix) |
| `attacks.py` | the eight submissions, deterministic |
| `run.py` | runs everything, writes `audit.log` and `results.json` |
| `test_suite.py` | positive and negative tests |
| `reproduce.sh` | one command |
| `Dockerfile` | pinned, runs with no network |
| `results.json` | the machine-readable result, including the seal |

`audit.log` is generated, not committed. Its SHA-256 is recorded in
`results.json` as `seal_sha256`, and `test_suite.py` recomputes it — so an edited
log fails the suite.

## Known limits

- One task, one surface. This is a specimen, not a coverage claim.
- Generalisation is untested: the eight attacks have no generated variants yet.
- No live Tally instance has been tested. That is a separate piece of work.
