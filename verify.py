"""Regenerate final analyzer reports and run the regression tests."""
from pathlib import Path
import json
import subprocess
import sys


def main():
    """Return failure if an analyzer or the tests fail."""
    root = Path(__file__).resolve().parent
    reports = root / "reports" / "after"
    reports.mkdir(parents=True, exist_ok=True)
    commands = []
    for tool in ("pylint", "bandit", "flake8"):
        args = ["-m", tool]
        if tool == "bandit":
            args += ["-r"]
        args += ["shuttle_system.py"]
        result = subprocess.run([sys.executable, *args], cwd=root,
                                capture_output=True, text=True)
        output = result.stdout + result.stderr
        (reports / f"{tool}_report.txt").write_text(output, encoding="utf-8")
        commands.append({"tool": tool, "exit_code": result.returncode,
                         "command": "python " + " ".join(args)})
        print(f"{tool}: exit {result.returncode}")
        print(output)
    (reports / "commands.json").write_text(
        json.dumps(commands, indent=2), encoding="utf-8")
    tests = subprocess.run([sys.executable, "-m", "pytest", "-q", "-W",
                            "error"], cwd=root, capture_output=True, text=True)
    evidence = root / "evidence"
    evidence.mkdir(exist_ok=True)
    (evidence / "tests.txt").write_text(
        tests.stdout + tests.stderr, encoding="utf-8")
    print(tests.stdout + tests.stderr)
    return int(tests.returncode != 0 or any(
        command["exit_code"] != 0 for command in commands))


if __name__ == "__main__":
    raise SystemExit(main())
