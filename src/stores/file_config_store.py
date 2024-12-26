import json
import logging

from typing import Any, Dict

from common.storage.config_store import ConfigStore

logger = logging.getLogger(__name__)


class FileConfigStore(ConfigStore):
    def get(self, key: str) -> Dict[str, Any]:
        """Get JSON configuration."""
        if key in self._cache:
            return self._cache[key]

        data = self._store.read(f"{key}.json") or "{}"
        try:
            content = json.loads(data)
            self._cache[key] = content
            return content
        except json.JSONDecodeError:
            return {}

    def set(self, key: str, data: Dict[str, Any]) -> None:
        """Set JSON configuration."""
        try:
            current = self.get(key)
            current.update(data)
            json_string = json.dumps(current, indent=2, ensure_ascii=False)
            self._store.write(f"{key}.json", json_string)
            self._cache[key] = current
        except Exception as e:
            logger.error(f"Error updating config {key}: {e}")
            raise
