from typing import TypeVar, Optional, cast
from unittest import TestCase

T = TypeVar("T")


def unwrap(t: TestCase, maybe_none: Optional[T]) -> T:
    t.assertIsNotNone(maybe_none)
    return cast(T, maybe_none)
