"""Regression checks for state, validation, persistence, and CLI behavior."""
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys

import pytest

import shuttle_system as shuttle

INITIAL_ROUTES = deepcopy(shuttle.ROUTES)


@pytest.fixture(autouse=True)
def isolated_routes():
    """Prevent a test's route mutations leaking into another test."""
    shuttle.ROUTES.clear()
    shuttle.ROUTES.update(deepcopy(INITIAL_ROUTES))
    yield
    shuttle.ROUTES.clear()
    shuttle.ROUTES.update(deepcopy(INITIAL_ROUTES))


def test_default_logs_are_independent():
    first = shuttle.add_trip_log("R1", 32)
    second = shuttle.add_trip_log("R1", 28)
    assert first is not second
    assert len(first) == len(second) == 1
    assert "R1 carried 32" in first[0]
    assert shuttle.average_load("R1") == 30


def test_explicit_log_list_is_updated():
    logs = ["existing"]
    assert shuttle.add_trip_log("R1", 0, logs) is logs
    assert len(logs) == 2
    assert shuttle.get_route("R1")["trips"] == [0]


@pytest.mark.parametrize("count", [-6, "full", None, 1.5, True, False])
def test_bad_counts_do_not_mutate_state(count):
    before = deepcopy(shuttle.ROUTES)
    with pytest.raises(ValueError, match="non-negative integer"):
        shuttle.add_trip_log("R1", count)
    assert shuttle.ROUTES == before


def test_invalid_logs_do_not_mutate_state():
    with pytest.raises(ValueError, match="Logs must be"):
        shuttle.add_trip_log("R1", 10, "not a list")
    assert shuttle.get_route("R1")["trips"] == []


@pytest.mark.parametrize("route_id", ["MISSING", None, [], 42])
def test_invalid_route_ids(route_id):
    with pytest.raises(ValueError, match="Unknown route"):
        shuttle.get_route(route_id)


@pytest.mark.parametrize("operation", [
    lambda: shuttle.add_trip_log("MISSING", 10),
    lambda: shuttle.remove_route("MISSING"),
    lambda: shuttle.average_load("MISSING"),
    lambda: shuttle.assign_driver("MISSING"),
])
def test_unknown_route_operations_report_error(operation):
    with pytest.raises(ValueError, match="Unknown route"):
        operation()


def test_empty_and_underused_route_rules():
    assert shuttle.average_load("R1") == 0.0
    assert shuttle.underused_routes() == []
    shuttle.add_trip_log("R1", 9)
    shuttle.add_trip_log("R2", 10)
    assert shuttle.underused_routes() == ["R1"]


def test_route_removal_is_explicit():
    shuttle.remove_route("R3")
    assert "R3" not in shuttle.ROUTES
    with pytest.raises(ValueError, match="Unknown route"):
        shuttle.average_load("R3")


def test_driver_belongs_to_the_registered_pool():
    assert shuttle.assign_driver("R1") in shuttle.DRIVERS


def test_utf8_snapshot_round_trip(tmp_path):
    shuttle.ROUTES["R1"]["name"] = "Biblioth\u00e8que"
    shuttle.add_trip_log("R1", 32)
    before = deepcopy(shuttle.ROUTES)
    identity = shuttle.ROUTES
    target = tmp_path / "fleet.json"
    shuttle.sync_fleet_data(target)
    assert json.loads(target.read_text(encoding="utf-8")) == before
    assert shuttle.ROUTES is identity
    assert shuttle.ROUTES == before


def test_snapshot_io_errors_are_not_hidden(tmp_path):
    with pytest.raises(OSError):
        shuttle.sync_fleet_data(tmp_path / "missing" / "fleet.json")


@pytest.mark.parametrize("stdin,expected", [
    ("\n", "Trips on R2 : [4]"),
    (" r1 \n", "Trips on R1 : [32, 28]"),
    ("R3\n", "Unknown route: 'R3'"),
    ("INVALID\n", "Unknown route: 'INVALID'"),
    ("", "Lookup cancelled."),
])
def test_cli_is_safe(tmp_path, stdin, expected):
    script = Path(shuttle.__file__).resolve()
    result = subprocess.run([sys.executable, str(script)], input=stdin,
                            cwd=tmp_path, text=True, capture_output=True)
    assert result.returncode == 0
    assert result.stderr == ""
    assert expected in result.stdout
    assert "Skipped invalid trip for R2" in result.stdout
    assert "Skipped invalid trip for R3" in result.stdout
    assert "R1 average: 30.0" in result.stdout
    snapshot = json.loads((tmp_path / "fleet.json").read_text())
    assert snapshot["R2"]["trips"] == [4]


def test_import_has_no_demo_or_file_side_effects(tmp_path):
    folder = str(Path(shuttle.__file__).resolve().parent)
    code = f"import sys; sys.path.insert(0, {folder!r}); import shuttle_system"
    result = subprocess.run([sys.executable, "-c", code], cwd=tmp_path,
                            text=True, capture_output=True)
    assert result.returncode == 0
    assert result.stdout == result.stderr == ""
    assert not (tmp_path / "fleet.json").exists()


def test_main_reports_sync_failure(monkeypatch, capsys):
    def fail_sync():
        raise OSError("disk unavailable")

    monkeypatch.setattr(shuttle, "sync_fleet_data", fail_sync)
    assert shuttle.main() == 1
    assert "Fleet sync failed: disk unavailable" in capsys.readouterr().out
