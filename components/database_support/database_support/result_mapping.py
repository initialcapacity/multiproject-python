from typing import TypeVar, Callable, Optional, List

from sqlalchemy import CursorResult, RowMapping

T = TypeVar("T")


def map_one_result(
    result: CursorResult[None], mapping: Callable[[RowMapping], T]
) -> Optional[T]:
    number_of_results = result.rowcount
    if number_of_results > 1:
        raise Exception(f"Expected one result but got {number_of_results}")

    for row in result:
        return mapping(row._mapping)

    return None


def map_results(
    result: CursorResult[None], mapping: Callable[[RowMapping], T]
) -> List[T]:
    return [mapping(row._mapping) for row in result]
