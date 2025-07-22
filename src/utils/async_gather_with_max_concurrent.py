from asyncio import Future, Semaphore, gather
from loguru import logger
from typing import Any, List


async def async_gather_with_max_concurrent(
    tasks: list[Future],
    max_concurrent: int = 5,
    task_name: str = "TASK_NAME",
) -> List[Any]:
    """
    Runs tasks concurrently with a limit on maximum simultaneous tasks.
    Logs the start and end of all tasks, and logs any exceptions per task.

    Args:
        tasks (list[Future]): List of awaitable objects (coroutines/futures).
        max_concurrent (int): Maximum number of concurrent tasks.

    Returns:
        List of results or exceptions from each task.
    """
    if not tasks:
        logger.warning(
            f"[{task_name}] No tasks provided to async_gather_with_max_concurrent."
        )
        return []

    semaphore = Semaphore(max_concurrent)

    async def sem_task(idx, task):
        async with semaphore:
            try:
                logger.debug(f"[{task_name}] Task {idx}: started.")
                result = await task
                logger.debug(f"[{task_name}] Task {idx}: completed.")
                return result
            except Exception as exc:
                logger.error(
                    f"[{task_name}] Task {idx}: failed with exception: {exc}",
                    exc_info=True,
                )
                # show the traceback
                logger.exception(f"[{task_name}] Task {idx} raised an exception.")
                return exc  # Still return the exception to keep gather's output aligned

    logger.info(
        f"[{task_name}] Running {len(tasks)} tasks with max_concurrent={max_concurrent}."
    )
    results = await gather(
        *(sem_task(i, t) for i, t in enumerate(tasks)), return_exceptions=True
    )
    logger.info(f"[{task_name}] All tasks have completed.")
    return results
