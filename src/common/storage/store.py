from abc import ABC, abstractmethod
from typing import Optional


class Store(ABC):
    """Abstract base class for storage operations."""

    @abstractmethod
    def read(self, key: str) -> Optional[str]:
        """Read raw data by key."""
        pass

    @abstractmethod
    def write(self, key: str, data: str) -> None:
        """Write raw data by key."""
        pass
