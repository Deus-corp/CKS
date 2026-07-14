from .registry import registry
from .builtin import BUILTIN_CONSTRAINTS

for constraint in BUILTIN_CONSTRAINTS:
    registry.register(constraint)

__all__ = [
    "registry",
    "BUILTIN_CONSTRAINTS",
]