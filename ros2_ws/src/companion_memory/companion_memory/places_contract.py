"""Ground-truth map coordinates for tests and docs."""
from __future__ import annotations

REFERENCE_PLACES: dict[str, dict[str, float]] = {
    'kitchen': {'x': 3.2, 'y': 1.1, 'yaw': 1.57},
    'bedroom': {'x': -1.0, 'y': 4.5, 'yaw': 0.0},
    'dock': {'x': 0.0, 'y': 0.0, 'yaw': 0.0},
}
