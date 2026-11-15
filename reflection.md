# Reflection on static code analysis

## Scope note

The repository README refers to four reflection questions from the handout,
but the supplied three-page PDF does not include four numbered questions.
The four prompts below are explicitly based on its learning objectives; they
are not presented as quotations from missing assignment questions.

## 1. How did the three tools contribute different findings?

Pylint identified shared mutable defaults, an unused route argument, global
reassignment, missing docstrings, resource-handling problems, and conventions.
Flake8 focused on blank lines, the long logging statement, and the bare except.
Bandit highlighted swallowed exceptions and non-cryptographic random selection.
Their overlap reinforced some findings, but each tool had a different scope.
Using all three provided a more useful review than relying on one score.

## 2. Which fixes mattered most, and how were they prioritized?

The shared `logs=[]` default and the `except: pass` block were the most important
tool findings for correctness. One leaked state across calls; the other hid
bad data and arithmetic failures. These were addressed along with context-managed
file access and validation before mutation. Bandit reported only Low-severity
findings, so there were no Medium or High findings to prioritize. Its random
choice warning was handled with `secrets.choice`, while recognizing that an
ordinary scheduling choice is not automatically a cryptographic requirement.
Formatting and naming improvements followed the behavior and resource fixes.

## 3. What did static analysis miss, and how were fixes verified?

The baseline demo accepted -6 and `"full"` as passenger counts, then raised
KeyError after deleting R3 and trying to calculate its mean. A valid route with
no observations could divide by zero. The tools did not establish these domain
rules or prove correct outputs. Running the program, reviewing its flow, and
adding regression tests exposed and checked those behaviors. The final suite
has 29 passing tests, covering independent logs, invalid input without mutation,
empty/unknown/deleted routes, the underuse threshold, UTF-8 persistence, file
errors, import side effects, and normal/invalid/cancelled CLI lookup. All three
tools were rerun on the final application; their exit codes are recorded.

## 4. How does this improve maintainability, and what are the limitations?

Explicit contracts, consistent names, short log formatting, predictable
exceptions, and closed file handles make the program easier to understand and
change. The project includes pinned tool versions, before/after reports, and a
repeatable verification command. The final Pylint score is 10.00/10 and Bandit
and Flake8 report no findings, without suppressions. These results reduce
known risks but do not prove the absence of all bugs. The program still uses
in-memory shared state, an educational non-atomic JSON round trip, and simple
random driver selection without availability or scheduling constraints. A
production fleet service would need persistence, concurrency controls, and
domain requirements beyond this lab.
