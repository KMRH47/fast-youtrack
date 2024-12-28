import logging
from functools import wraps
from typing import TypeVar, Callable

logger = logging.getLogger(__name__)
T = TypeVar("T")


def cached_response(cache_key: str):
    """
    Decorator that calls the underlying method and caches the response.
    For lists: Caches the entire list under the cache_key
    For single items: Caches under cache_key[item_id]
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                response = func(self, *args, **kwargs)
                config = self._config_store.get("config") or {}

                if isinstance(response, list):
                    config[cache_key] = [item.model_dump() for item in response]
                elif response is not None:
                    if not args:
                        raise ValueError(f"No ID provided for caching single item in {cache_key}")
                    
                    item_id = str(args[0])

                    if cache_key not in config or not isinstance(config[cache_key], dict):
                        config[cache_key] = {}
                        
                    config[cache_key][item_id] = response.model_dump()

                self._config_store.set("config", config)
                return response
            except Exception as e:
                logger.error(f"Could not handle cache for '{cache_key}': {e}")
                raise

        return wrapper

    return decorator
