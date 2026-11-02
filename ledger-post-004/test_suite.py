#!/usr/bin/env python3
"""The suite that proves the specimen is not a story.

    python3 test_suite.py

Two kinds of test. Positive: the published numbers are what the code produces.
Negative: if you weaken the fixed grader, or edit the log, the suite fails
loudly. A verifier nobody tried to break is not a verifier.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import sys

import graders
from attacks import ATTACKS
from ledger import RUN_NOW, independent_check, reference_solution

HERE = pathlib.Path(__file__).resolve().parent
fails: list[str] = []


def check(cond: bool, msg: str) -> None:
    if not cond:
        fails.append(msg)


def score_all(grader) -> dict:
    out = {}
    for aid, _name, fn in ATTACKS:
        output, info, state = fn()
        done, _ = independent_check(state, RUN_NOW)
        out[aid] = (grader(output, info, state), done)
    return out


# ── positive: the published numbers ────────────────────────────────────────
b = score_all(graders.before)
a = score_all(graders.after)

check(sum(1 for s, d in b.values() if s == 1.0 and not d) == 4,
      "grader as submitted must pay for nothing on exactly 4 of 8 attacks")
check(sum(1 for s, d in a.values() if s == 1.0 and not d) == 0,
      "fixed grader must pay for nothing on 0 of 8 attacks")
check(sum(1 for s, d in b.values() if s == 0.0 and d) == 2,
      "grader as submitted must refuse exactly 2 correct runs")
check(sum(1 for s, d in a.values() if s == 0.0 and d) == 0,
      "fixed grader must refuse 0 correct runs")
check(a["01"][0] == 0.0 and a["08"][0] == 0.0,
      "empty output and our own wrong answer must still be rejected after the fix")
check(graders.after("", {}, reference_solution()) == 1.0,
      "a correct ledger must score 1.0 even with no output text at all")

# ── negative: weaken the fix and the suite must notice ─────────────────────
def weakened_text(output, info, state):
    """Regression: someone re-adds a completion-string shortcut."""
    if "voucher created" in (output or ""):
        return 1.0
    return graders.after(output, info, state)


def weakened_replay(output, info, state):
    """Regression: someone drops the run-id guard."""
    v = state.get("vouchers", {})
    if len(v) == 3:
        return 1.0
    return graders.after(output, info, state)


def weakened_lines(output, info, state):
    """Regression: someone counts vouchers instead of reconciling lines."""
    v = state.get("vouchers", {})
    if len(v) == 3 and all(x.get("run") == RUN_NOW for x in v.values()):
        return 1.0
    return graders.after(output, info, state)


for name, g, aid in (("completion-string shortcut", weakened_text, "02"),
                     ("missing run-id guard", weakened_replay, "04"),
                     ("count instead of reconcile", weakened_lines, "03")):
    output, info, state = dict((x[0], x[2]) for x in ATTACKS)[aid]()
    done, _ = independent_check(state, RUN_NOW)
    check(g(output, info, state) == 1.0 and not done,
          f"negative test broken: {name} should re-open attack {aid}, but did not")

# ── the artefacts on disk match the code ───────────────────────────────────
res = json.loads(HERE.joinpath("results.json").read_text(encoding="utf-8"))
check(res["attacks"] == 8, "results.json must record 8 attacks")
check(res["bypassed_before"] == 4 and res["bypassed_after"] == 0,
      "results.json bypass counts drifted from the code")
check(res["false_negatives_before"] == 2 and res["false_negatives_after"] == 0,
      "results.json false-negative counts drifted from the code")
check(res["live_tally_instance"] is False,
      "results.json must not claim a live Tally instance")

log = HERE.joinpath("audit.log").read_text(encoding="utf-8")
body = log.split("seal sha256 ")[0]
check(hashlib.sha256(body.encode("utf-8")).hexdigest() == res["seal_sha256"],
      "audit.log seal does not match results.json — the log was edited")
check(len(res["seal_sha256"]) == 64, "the seal must be a real 64-character sha256")

if fails:
    print("specimen tests: FAIL")
    for f in fails:
        print("  ✕", f)
    sys.exit(1)
print("specimen tests: clean · 8 attacks, 4→0 bypasses, 2→0 false negatives, "
      "3 regressions caught, seal verified")
