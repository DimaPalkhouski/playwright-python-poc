"""Thin wrapper around allpairspy for pairwise test data generation."""
from __future__ import annotations

from typing import Any

from allpairspy import AllPairs


def generate_pairwise(parameters: dict[str, list[Any]]) -> list[dict[str, Any]]:
    """Generate pairwise combinations from a parameter dict.

    Args:
        parameters: Mapping of parameter name to list of possible values.

    Returns:
        List of dicts, each representing one pairwise test case.

    Example::

        cases = generate_pairwise({
            "state": ["CA", "TX"],
            "age": [25, 45],
            "coverage": ["basic", "premium"],
        })
        # Returns ~4 cases instead of 2×2×2=8 exhaustive cases.
    """
    keys = list(parameters.keys())
    values = list(parameters.values())
    return [dict(zip(keys, case)) for case in AllPairs(values)]
