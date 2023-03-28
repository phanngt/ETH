from typing import Type, TypeVar

T = TypeVar("T")
TypeT = Type[T]

reg = dict()


# noinspection PyPep8Naming
def Si(cls: Type[T], *, default: T = None) -> T:
    """
    Singleton Registry.

    May get WRONG if Python Event Loop closed.
    """
    if cls not in reg:
        reg[cls] = default if default is not None else cls()
    return reg[cls]
