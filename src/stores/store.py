from abc import ABC, abstractmethod
from typing import Optional, TypeVar, Generic

T = TypeVar('T')  # Type variable for the data type

class Store(Generic[T], ABC):
    """Abstract base class for generic storage operations."""

    @abstractmethod
    def read(self, key: str) -> Optional[T]:
        """Read data by key."""
        pass

    @abstractmethod
    def write(self, key: str, data: T) -> None:
        """Write data by key."""
        pass
