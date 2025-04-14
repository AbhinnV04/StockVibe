import time
import requests
from ..logger import get_logger

logger = get_logger("decorator.retry")


def retry_with_backoff(max_retries=3, base_delay=1):
    """Decorator to retry a function with exponential backoff."""

    def decorator(func):
        def wrapper(*args, **kwargs):
            delay = base_delay
            for attempts in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except requests.exceptions.RequestException as e:
                    logger.error(
                        f"Request failed: {e}, attempt {attempts + 1}/{max_retries}"
                    )
                    time.sleep(delay)
                    delay *= 2
            raise Exception(f"Max retries exceeded for {func.__name__}")

        return wrapper

    return decorator
