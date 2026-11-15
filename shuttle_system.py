"""Track campus shuttle passenger loads and persist the fleet as JSON."""

import json
import secrets
from datetime import datetime

ROUTES = {
    "R1": {"name": "Main Gate - Library", "trips": []},
    "R2": {"name": "Hostel - Sports Complex", "trips": []},
    "R3": {"name": "Admin Block - Metro", "trips": []},
}
MIN_CAPACITY = 10
DRIVERS = ("Prakash", "Leela", "Imran", "Tom")


def get_route(route_id):
    """Return a route, raising ValueError for an unknown or invalid ID."""
    if not isinstance(route_id, str) or route_id not in ROUTES:
        raise ValueError(f"Unknown route: {route_id!r}")
    return ROUTES[route_id]


def add_trip_log(route_id, passenger_count, logs=None):
    """Log a non-negative integer count without sharing default log lists."""
    route = get_route(route_id)
    if (not isinstance(passenger_count, int)
            or isinstance(passenger_count, bool) or passenger_count < 0):
        raise ValueError("Passenger count must be a non-negative integer")
    if logs is None:
        logs = []
    elif not isinstance(logs, list):
        raise ValueError("Logs must be a list or None")
    route["trips"].append(passenger_count)
    logs.append(f"{datetime.now()}: {route_id} carried {passenger_count}")
    return logs


def remove_route(route_id):
    """Remove a known route; report an unknown route with ValueError."""
    get_route(route_id)
    del ROUTES[route_id]


def average_load(route_id):
    """Return the mean load, or 0.0 when a known route has no trips."""
    trips = get_route(route_id)["trips"]
    return sum(trips) / len(trips) if trips else 0.0


def underused_routes():
    """Return routes with observed trips and mean load below MIN_CAPACITY."""
    return [
        route_id for route_id, route in ROUTES.items()
        if route["trips"] and average_load(route_id) < MIN_CAPACITY
    ]


def assign_driver(route_id):
    """Validate the route and choose a driver using system randomness."""
    get_route(route_id)
    return secrets.choice(DRIVERS)


def sync_fleet_data(file_path="fleet.json"):
    """Write/read a UTF-8 JSON snapshot while preserving the ROUTES object.

    File and serialization errors propagate to the caller. This educational
    round trip is not an atomic or concurrent fleet storage implementation.
    """
    with open(file_path, "w", encoding="utf-8") as fleet_file:
        json.dump(ROUTES, fleet_file, indent=2, ensure_ascii=False)
    with open(file_path, encoding="utf-8") as fleet_file:
        snapshot = json.load(fleet_file)
    ROUTES.clear()
    ROUTES.update(snapshot)


def main():
    """Run a short demo and handle invalid trip data and route lookup."""
    for route_id, count in (
            ("R1", 32), ("R1", 28), ("R2", 4), ("R2", -6), ("R3", "full")):
        try:
            add_trip_log(route_id, count)
        except ValueError as error:
            print(f"Skipped invalid trip for {route_id}: {error}")
    print("Driver for R1:", assign_driver("R1"))
    print("Underused:", underused_routes())
    print("R1 average:", average_load("R1"))
    try:
        sync_fleet_data()
    except (OSError, ValueError, TypeError) as error:
        print(f"Fleet sync failed: {error}")
        return 1
    remove_route("R3")
    print("Removed R3 from the active fleet.")
    try:
        choice = input("Route to look up (Enter for R2): ").strip().upper()
    except (EOFError, KeyboardInterrupt):
        print("\nLookup cancelled.")
        return 0
    choice = choice or "R2"
    try:
        print("Trips on", choice, ":", get_route(choice)["trips"])
    except ValueError as error:
        print(error)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
