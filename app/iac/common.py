"""Common methods used for AWS project setup"""

import functools
import logging

from typing import Callable, Coroutine, Any

LOGGER = logging.getLogger(__name__)


def wait_for_resource(waiter_name: str, waiter_kwargs: dict):
    """
    Decorator to wait for an AWS resource using a provided boto3
    client and waiter before proceeding.

    Parameters
    ----------
    waiter_name : str
        The name of the waiter (e.g., 'bucket_exists').
    waiter_kwargs : dict
        Parameters to pass to waiter.wait().
    """

    def decorator(func: Callable[..., Coroutine[Any, Any, Any]]):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            client = await func(*args, **kwargs)

            waiter = client.get_waiter(waiter_name)
            LOGGER.info("Waiting for resource with waiter: %s", waiter_name)
            waiter.wait(**waiter_kwargs)
            LOGGER.info("Resource is now ready according to waiter: %s", waiter_name)

            return client

        return wrapper

    return decorator
