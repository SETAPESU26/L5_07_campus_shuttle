# Lab 5 - Campus Shuttle Static Code Analysis

Completed from the assigned
[SETAPESU26/L5_07_campus_shuttle](https://github.com/SETAPESU26/L5_07_campus_shuttle)
starter at commit `73897d2e657fa662f02b2bd46e1b9f3cf26f0cb0`.

## Verified results

| Check | Before | After |
| --- | --- | --- |
| Pylint | 6.25/10; 18 diagnostics | **10.00/10**, zero diagnostics |
| Bandit | 2 Low findings; 0 Medium/High | **Zero findings** |
| Flake8 | 10 findings | **Zero findings** |
| Demo | Deleted-route KeyError; exit 1 | Handles invalid data; exit 0 |
| Regression tests | No supplied tests | **29 passed**, warnings treated as errors |

No rules are disabled and no findings are suppressed. The analysis target is
the assignment's `shuttle_system.py`; the flawed baseline is intentionally
preserved for comparison. Static analysis is complemented by runtime tests.

## Setup and run

Python 3.12.6 was used for verification.

```sh
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux:
# source .venv/bin/activate
python -m pip install -r requirements.txt
python shuttle_system.py
```

Press Enter for R2, or enter a route ID. The demo skips the starter's invalid
-6 and `"full"` sample counts, calculates R1's mean as 30.0, writes a JSON
snapshot, removes R3, and safely handles the lookup. Driver selection varies.
Input ending early or being cancelled ends the lookup cleanly.

## Reproduce final checks

```sh
python verify.py
```

This runs all three tools, saves their stdout and stderr in `reports/after/`,
records exit codes in `commands.json`, and runs the tests. Individual commands:

```sh
python -m pylint shuttle_system.py
python -m bandit -r shuttle_system.py
python -m flake8 shuttle_system.py
python -m pytest -q -W error
```

An empty `flake8_report.txt` with exit 0 means no style violations; it is not a
missing report. Bandit's informational output is also retained.

## Deliverables

| File or folder | Purpose |
| --- | --- |
| `shuttle_system.py` | Cleaned application with more than four documented fixes |
| `issues.md` | Tool codes, original/fixed line numbers, fixes, and runtime findings |
| `reflection.md` | Four objective-based reflection responses and the source-question gap |
| `reports/before/` | Original Pylint, Bandit, and Flake8 reports, with exit codes |
| `reports/after/` | Final reports, with exit codes |
| `reports/stages/` | Intermediate evidence for the separate tool-fix commits |
| `reports/Lab5_Static_Code_Analysis_Report.pdf` | Summary, issue table, reflection, and visual evidence |
| `evidence/` | Original/fixed runs, test result, tool versions, and screenshot images |
| `baseline/shuttle_system.py` | Exact original source; not imported by the test suite |
| `test_shuttle_system.py` | Regression checks for the identified behavior bugs |

The handout requires three commits covering fixes from the three tools. The
submission separates Bandit fixes, Pylint/correctness fixes, and Flake8 formatting.

Screenshots are browser captures of verbatim recorded command transcripts,
not native console-window screenshots. Raw reports remain available for review.
The supplied three-page handout does not list the four reflection questions
referenced by the starter README. The responses explicitly use prompts based
on the stated learning objectives rather than claiming to reproduce them.

## Contracts and limits

- Route IDs must exist. Unknown routes raise `ValueError`; the CLI explains it.
- Passenger counts must be non-negative integers; booleans are rejected.
- Independent calls receive independent log lists. Caller-provided lists are reused.
- Empty routes have mean 0.0 and are excluded from underuse classification until
  they have observations. Observed means strictly below 10 are underused.
- `assignDriver` is renamed to `assign_driver`; the module state is `ROUTES`.
  The demo and tests use the updated names. External callers need the same update.
- JSON snapshots use UTF-8 context-managed files. This is a simple write/read
  round trip, not atomic storage or a concurrent scheduling service.
- The original Bandit findings were Low severity. Random driver selection is not
  inherently cryptographic; using `secrets.choice` clears the flagged pattern.

To reproduce the original crash, run `python shuttle_system.py` inside
`baseline/` and press Enter. That separate command is expected to fail.
