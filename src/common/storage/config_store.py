from abc import ABC
from typing import Dict, Any

from .store import Store

class ConfigStore(ABC):
    """Handles configuration storage with JSON serialization."""
    
    def __init__(self, store: Store):
        self._store = store
        self._cache = {}
    
    def get(self, key: str) -> Dict[str, Any]:
        """Get configuration by key."""
        pass
    
    def set(self, key: str, data: Dict[str, Any]) -> None:
        """Set configuration by key."""
        pass 