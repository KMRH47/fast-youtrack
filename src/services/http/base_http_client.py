from abc import ABC, abstractmethod
from typing import Dict, Any


class HttpClient(ABC):
    """Base interface for HTTP operations."""

    @abstractmethod
    def request(self, endpoint: str, method: str = "get", **kwargs) -> Dict[str, Any]:
        pass
