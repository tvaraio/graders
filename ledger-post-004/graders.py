"""Two graders for the same task: as submitted, and after the fix.

`before` is a deliberately simple, hand-written baseline: a substring completion
check plus a brittle structured fallback. It is not a named customer's grader.
`after` is the repair; the published counts apply only to this synthetic fixture.

The repair is one idea: score the state, not the story. Output text is not read
at all. That is what closes the four bypasses and both false negatives at once.
"""
from __future__ import annotations

from ledger import REGISTER, RUN_NOW


def before(output: str, info: dict, state: dict) -> float:
    """As submitted. Reads the agent's text and a self-reported flag."""
    text = (output or "").strip()
    if not text:
        return 0.0
    if "voucher created" in text:          # substring completion check
        return 1.0
    if text.startswith("posted=") and info.get("posted") == 3:   # type-strict
        return 1.0
    return 0.0


def after(output: str, info: dict, state: dict, run: str = RUN_NOW) -> float:
    """After the fix. Reads only the ledger the run left behind.

    Guards, in order:
      1. all three register vouchers exist, and nothing else
      2. every voucher carries this run's stamp   (kills replay)
      3. every line reconciles against the register (kills a line item short)
      4. no credit is derived from output text or info (kills the string,
         the echoed task text, markdown wrapping and "3" vs 3)
    """
    vouchers = state.get("vouchers", {})
    if set(vouchers) != {e["id"] for e in REGISTER}:
        return 0.0
    for entry in REGISTER:
        got = vouchers[entry["id"]]
        if got.get("run") != run:
            return 0.0
        want = sorted((n, int(q), float(r)) for n, q, r in entry["lines"])
        try:
            have = sorted((str(n), int(q), float(r)) for n, q, r in got.get("lines", []))
        except (TypeError, ValueError):
            return 0.0
        if have != want:
            return 0.0
    return 1.0
