import logging
from functools import wraps
from typing import TypeVar, Callable

logger = logging.getLogger(__name__)
T = TypeVar("T")


def cached_response(cache_key: str):
    """
    Decorator that calls the underlying method, inspects whether
    the returned data is a single item or a list, and caches
    accordingly in the config store.
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                response = func(self, *args, **kwargs)
                config = self._config_store.get("config") or {}

                if isinstance(response, list):
                    config[cache_key] = [item.model_dump() for item in response]
                else:
                    item_id = None
                    if args:
                        item_id = str(args[0])
                    if not item_id:
                        item_id = str(kwargs.get("id", "default"))

                    if cache_key not in config or not isinstance(
                        config[cache_key], dict
                    ):
                        config[cache_key] = {}

                    if response is not None:
                        config[cache_key][item_id] = response.model_dump()
                    else:
                        logger.warning(
                            f"No data to cache for {cache_key} with item ID {item_id}"
                        )

                self._config_store.set("config", config)

                return response
            except Exception as e:
                logger.error(f"Could not handle cache for '{cache_key}': {e}")
                raise

        return wrapper

    return decorator
