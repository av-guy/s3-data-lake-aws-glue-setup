"""Common methods used for AWS project setup"""

import asyncio
import functools
import logging

from typing import Callable, Coroutine, Any
from mypy_boto3_glue import GlueClient

LOGGER = logging.getLogger(__name__)


async def wait_for_glue_database(
    client: GlueClient, database_name: str, delay: int = 5, max_attempts: int = 20
) -> None:
    """
    Manually wait for a Glue database to become available.

    Parameters
    ----------
    client : GlueClient
        Boto3 client for Glue operations.
    database_name : str
        Name of the Glue database to wait for.
    delay : int, optional
        Delay between attempts in seconds.
    max_attempts : int, optional
        Maximum number of attempts to wait.

    Notes
    -----
    Method is necessary as waiter does not exist for database_created.
    """
    for attempt in range(max_attempts):
        try:
            client.get_database(Name=database_name)
            LOGGER.info("Glue database '%s' is now available.", database_name)
            return
        except client.exceptions.EntityNotFoundException:
            LOGGER.debug(
                "Database '%s' not ready yet, sleeping %s seconds (attempt %s/%s)...",
                database_name,
                delay,
                attempt + 1,
                max_attempts,
            )
            await asyncio.sleep(delay)

    raise TimeoutError(f"Timed out waiting for Glue database: {database_name}")


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
