"""
CKS Plugin — External Constraint Discovery.

This module provides a mechanism for discovering and loading canonical
validation constraints from external packages using the ``entry_points``
machinery (``importlib.metadata``).

Plugins are discovered via the ``cks.constraints`` entry-point group.
Each entry-point must reference a callable that accepts zero arguments
and returns an iterable of `Constraint` instances.

Loaded constraints are automatically registered in the canonical global
`ConstraintRegistry`.
"""

from __future__ import annotations

import sys
from typing import Iterable, List

from .constraints.base import Constraint
from .constraints.registry import ConstraintRegistry
from .constraints import registry as _global_registry


def discover_entry_points() -> Iterable:
    """Yield every entry-point registered under the ``cks.constraints`` group."""
    try:
        from importlib.metadata import entry_points
    except ImportError:  # Python < 3.9 fallback
        from importlib_metadata import entry_points

    # Select the group; in Python ≥3.12 we can use entry_points(group=...)
    eps = entry_points()
    for ep in eps:
        if ep.group == "cks.constraints":
            yield ep


def load_constraints_from_entry_point(ep) -> List[Constraint]:
    """Call the entry-point and return the resulting constraints.

    Raises
    ------
    RuntimeError
        If the entry-point cannot be loaded or does not return an
        iterable of `Constraint` instances.
    """
    try:
        factory = ep.load()
    except Exception as exc:
        raise RuntimeError(
            f"Failed to load entry-point {ep.name!r} ({ep.value!r}): {exc}"
        ) from exc

    try:
        constraints = list(factory())
    except Exception as exc:
        raise RuntimeError(
            f"Entry-point factory {ep.name!r} raised an exception: {exc}"
        ) from exc

    for c in constraints:
        if not isinstance(c, Constraint):
            raise RuntimeError(
                f"Entry-point {ep.name!r} returned an object that is not "
                f"a Constraint: {c!r}"
            )
    return constraints


def load_external_constraints(
    registry: ConstraintRegistry | None = None,
) -> int:
    """Discover and register all external constraints.

    Parameters
    ----------
    registry : ConstraintRegistry or None
        The target registry.  If *None*, the canonical global registry
        is used.

    Returns
    -------
    int
        Number of external constraints registered.
    """
    target = registry if registry is not None else _global_registry
    count = 0
    for ep in discover_entry_points():
        try:
            constraints = load_constraints_from_entry_point(ep)
        except RuntimeError:
            # Log the error but continue with other plugins.
            print(
                f"[cks] WARNING: could not load plugin {ep.name!r} "
                f"({ep.value!r})",
                file=sys.stderr,
            )
            continue
        for constraint in constraints:
            target.register(constraint)
            count += 1
    return count


__all__ = [
    "discover_entry_points",
    "load_constraints_from_entry_point",
    "load_external_constraints",
]