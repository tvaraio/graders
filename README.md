# tvaraio graders

Examples showing how AI task graders can be fooled and how to make them more reliable.

## First example: voucher posting

[ledger-post-004](ledger-post-004/) compares a weak grader with a state-checking grader across eight scripted cases. It uses simulated accounting data and does not connect to Tally.

## Run it

Requires Python 3.11 or later.

```bash
git clone https://github.com/tvaraio/graders.git
cd graders/ledger-post-004
./reproduce.sh
```
