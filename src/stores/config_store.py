import logging
import json

from abc import ABC
from typing import Dict, Any, Optional

from stores.store import Store

logger = logging.getLogger(__name__)


class ConfigStore(Store[Dict[str, Any]]):
    """Handles all persistent storage with JSON serialization."""

    def __init__(self, store: Store[str]):
        self._store = store
        self._cache: Dict[str, Any] = {}

    def read(self, key: str) -> Optional[Dict[str, Any]]:
        """Read data by key."""
        if key not in self._cache:
            raw_data = self._store.read(f"{key}.json")
            if raw_data:
                self._cache[key] = json.loads(raw_data)
            else:
                self._cache[key] = {}
        return self._cache[key]

    def write(self, key: str, data: Dict[str, Any]) -> None:
        """Write data by key."""
        try:
            current = self.read(key) or {}
            current.update(data)
            json_string = json.dumps(current, indent=2)
            self._store.write(f"{key}.json", json_string)
            self._cache[key] = current
        except Exception as e:
            logger.error(f"Error updating {key}: {e}")
            raise
