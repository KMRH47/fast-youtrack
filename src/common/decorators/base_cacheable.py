from abc import ABC, abstractmethod
from stores.config_store import ConfigStore

class Cacheable(ABC):
    """Base class for objects that support caching via ConfigStore."""
    
    @property
    @abstractmethod
    def _config_store(self) -> ConfigStore:
        """The config store used for caching."""
        pass 