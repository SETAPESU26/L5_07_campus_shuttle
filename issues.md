# Issue table

Original line numbers refer to the preserved `baseline/shuttle_system.py` at
upstream commit `73897d2e657fa662f02b2bd46e1b9f3cf26f0cb0`.
Fixed line numbers refer to the completed `shuttle_system.py`.

## Findings reported by the required tools

The original Bandit scan found **two Low severity, High confidence** issues.
It reported **no Medium or High severity issues**. Pylint warning/convention
categories and Flake8 codes below are not Bandit security severity ratings.
The harmful shared-state and error-hiding behaviors were addressed first.

| Issue | Type / tool code | Original line(s) | Description | Fix approach / fixed line(s) |
| --- | --- | --- | --- | --- |
| Shared mutable default | Bug / Pylint W0102 | 11 | `logs=[]` is reused across independent calls. | Use `None`, create a new list per call, preserve explicit lists; 23-35. |
| Exceptions silently swallowed | Error handling / Pylint W0702, Bandit B110 (Low), Flake8 E722 | 26-30 | Bare `except: pass` masks empty-route and malformed-data failures. | Validate counts at entry and explicitly skip routes with no observations; no swallowing handler; 26-32, 50-55. |
| Non-cryptographic random choice | Security heuristic / Bandit B311 (Low) | 35 | Bandit flags `random.choice` as unsuitable for security-sensitive selection. Ordinary driver scheduling is not inherently cryptographic. | Use `secrets.choice` without suppressing the rule; 58-61. This is not evidence of an actual exploit. |
| File handles not reliably closed | Resource management / Pylint R1732 | 39-43 | Manual open/close; the read handle is not closed explicitly. | Use two context managers so handles close on success or exception; 70-73. |
| Unspecified file encoding | Portability / Pylint W1514 | 39, 42 | Default encoding varies across systems. | Specify UTF-8 for both reading and writing; 70-73. |
| Global reassignment | Maintainability / Pylint W0603 | 38, 43 | Rebinding `routes` can leave existing references stale. | Mutate the existing `ROUTES` mapping with clear/update; 74-75. |
| Unused route argument | Logic warning / Pylint W0613 | 33 | Driver assignment ignores the requested route. | Validate the route before selecting a driver; 60. |
| Nonstandard function name | Convention / Pylint C0103 | 33 | `assignDriver` violates snake_case naming. | Rename to `assign_driver` and update the demo call; 58, 86. |
| Missing documentation | Convention / Pylint C0114, C0116 | 1, 11, 16, 19, 23, 33, 37, 45 | Module and public functions lack docstrings. | Add module/function contracts and explain empty-route/file semantics; throughout. |
| Old-style string formatting | Convention / Pylint C0209 | 13 | Percent formatting makes the long log expression harder to read. | Use a shorter f-string; 34. |
| Incorrect blank-line separation | Style / Flake8 E302, E305 | 11, 16, 19, 23, 33, 37, 45, 60 | Top-level definitions and entry-point call have too few blank lines. | Add two blank lines at top-level boundaries; throughout. |
| Overlong logging line | Style / Flake8 E501 | 13 | The log expression is 82 characters (limit 79). | Replace it with a shorter f-string; 34. |

## Additional bugs found by running and reviewing the program

These are runtime/manual findings, not claims that the tools detected them.

| Issue | Type | Original line(s) | Description | Fix approach / fixed line(s) |
| --- | --- | --- | --- | --- |
| Invalid passenger data accepted | Data integrity | 12, 49-50 | Negative counts and `"full"` enter the fleet; R2's original mean becomes -1.0. | Accept only non-negative integer counts, reject booleans and invalid log containers before mutating state; 25-33. Demo explains rejected samples; 80-85. |
| Empty mean divides by zero | Runtime bug | 21 | A known route with no trips has no denominator. | Return 0.0 for the empty mean; exclude unobserved routes from underuse classification; 44-55. |
| Unknown/deleted route crashes | Runtime bug | 17, 20, 55-58 | The demo removes R3 and then computes its mean, raising KeyError. Lookup input is unchecked. | Centralize route validation, remove the invalid follow-up lookup, and explain unknown route input; 16-20, 94-105. |
| Import starts the demo | Side effect | 60 | Import runs input prompts and writes a file. | Guard execution with `if __name__ == "__main__"`; 109-110. |

## Verified result

| Check | Before | After |
| --- | --- | --- |
| Pylint | 6.25/10; 18 diagnostics; exit 28 | 10.00/10; zero diagnostics; exit 0 |
| Bandit | 2 Low / 0 Medium / 0 High findings; exit 1 | Zero findings; exit 0 |
| Flake8 | 10 findings; exit 1 | Zero findings; exit 0 (empty report is expected) |
| Demo with default lookup | KeyError after looking up removed R3; exit 1 | Rejects bad samples, shows R2 trips `[4]`; exit 0 |
| Regression suite | No supplied test suite | 29 tests pass, with warnings treated as errors |

No lint rules were disabled, no `nosec` comments were added, and no findings
were hidden with an exit-zero option. Static checks target the assignment
application, not the intentionally flawed baseline or test assertions.
