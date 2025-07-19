from asyncio import Future, Semaphore, gather


async def async_gather_with_max_concurrent(
    tasks: list[Future],
    max_concurrent: int = 5,
) -> list:
    semaphore = Semaphore(max_concurrent)

    async def sem_task(task):
        async with semaphore:
            return await task

    return await gather(*(sem_task(task) for task in tasks), return_exceptions=True)
