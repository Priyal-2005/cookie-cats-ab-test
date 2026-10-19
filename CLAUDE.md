# Project: Cookie Cats A/B Test - Player Retention Analysis

## Goal
Resume-grade analytics project for a Growth Analyst internship application.
Question: does moving the first progression gate from level 30 (gate_30) to level 40 (gate_40) change day-1 and day-7 retention and engagement?
Deliverables: cleaned data, SQL metrics, validated pandas analysis, dashboard-ready CSVs, README.

## Non-negotiable rules
1. Never invent numbers. Every figure in the README must be read from a file in /outputs that code produced.
2. Print row counts before and after every cleaning step and save them to outputs/cleaning_log.csv.
3. Record every assumption in docs/assumptions.md (for example: rounds played is only an approximate proxy for level reached).
4. Every SQL metric must be cross-checked with an independent pandas calculation. Report mismatches, do not hide them.
5. `python src/run_all.py` must rebuild everything from raw data.
6. Plain, readable code with comments. I am a 2nd-year student and must be able to explain every function. Prefer simple over clever.
7. After each phase, give me: (a) 8-10 lines on what you did and why, (b) a checklist of things I should verify myself.
8. Allowed libraries: pandas, numpy, matplotlib, sqlite3 (stdlib), openpyxl. Ask before adding anything else.
9. Commit after each phase with a descriptive message.
10. If a decision materially changes the metrics, state the options, pick a default, and flag it clearly.
11. I write some SQL files myself (they are marked in the phase prompts). Never overwrite or rewrite those. Review them and list bugs only.
12. Keep a file docs/ai_mistakes_log.md. Whenever you make an error that I or a validation check catches, add a line: what went wrong, how it was caught, what changed.