#!/usr/bin/env python3
"""Run all eight attacks against both graders. Write audit.log and results.json.

    python3 run.py

No network, no model, no API key, no dependency outside the standard library.
Every verdict is decided twice: once by the grader, once by an independent check
that reads the ledger against the purchase register. A bypass is a full score
where the independent check says the work was not done.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import sys

from attacks import ATTACKS, FIXES
from graders import after, before
from ledger import RUN_NOW, independent_check

HERE = pathlib.Path(__file__).resolve().parent


def main() -> int:
    lines: list[str] = []
    rows: list[dict] = []

    lines.append("audit.log — ledger-post-004")
    lines.append("synthetic Tally-shaped fixture; no live Tally instance is contacted")
    lines.append(f"run id: {RUN_NOW}")
    lines.append("")
    lines.append("id  attack                                  before  after  work_done  verdict")

    for aid, name, fn in ATTACKS:
        output, info, state = fn()
        sb = before(output, info, state)
        sa = after(output, info, state)
        done, reasons = independent_check(state, RUN_NOW)

        bypass_before = sb == 1.0 and not done
        bypass_after = sa == 1.0 and not done
        fn_before = sb == 0.0 and done
        fn_after = sa == 0.0 and done

        verdict = "paid for nothing" if bypass_before else (
            "correct run refused" if fn_before else "rejected")
        lines.append(f"{aid}  {name:<38}  {sb:>5.1f}  {sa:>5.1f}  {str(done):<9}  {verdict}")
        for r in reasons:
            lines.append(f"      independent: {r}")
        lines.append(f"      fix: {FIXES[aid]}")

        rows.append({
            "id": aid, "name": name,
            "score_before": sb, "score_after": sa,
            "work_done": done, "reasons": reasons,
            "bypass_before": bypass_before, "bypass_after": bypass_after,
            "false_negative_before": fn_before, "false_negative_after": fn_after,
            "fix": FIXES[aid],
        })

    summary = {
        "environment": "ledger-post-004",
        "surface": "synthetic Tally-shaped voucher posting fixture",
        "live_tally_instance": False,
        "attacks": len(rows),
        "bypassed_before": sum(r["bypass_before"] for r in rows),
        "bypassed_after": sum(r["bypass_after"] for r in rows),
        "false_negatives_before": sum(r["false_negative_before"] for r in rows),
        "false_negatives_after": sum(r["false_negative_after"] for r in rows),
        "run_id": RUN_NOW,
    }

    lines.append("")
    lines.append(
        f"total: {summary['attacks']} attacks · "
        f"{summary['bypassed_before']} paid for nothing before · "
        f"{summary['bypassed_after']} after · "
        f"{summary['false_negatives_before']} correct runs refused before · "
        f"{summary['false_negatives_after']} after"
    )
    log = "\n".join(lines) + "\n"
    seal = hashlib.sha256(log.encode("utf-8")).hexdigest()
    lines.append(f"seal sha256 {seal}")
    log = "\n".join(lines) + "\n"

    # The seal covers the log without the seal line, so it can be recomputed.
    HERE.joinpath("audit.log").write_text(log, encoding="utf-8")
    summary["seal_sha256"] = seal
    summary["rows"] = rows
    HERE.joinpath("results.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(log, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
