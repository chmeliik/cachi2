import asyncio
import logging
from collections import deque
from collections.abc import Iterable
from os import PathLike
from pathlib import Path

import aiohttp
from aiohttp.client import ClientSession

CHUNK_SIZE = 8192
CONCURRENCY_LIMIT = 5

log = logging.getLogger(__name__)


def async_download_files(to_download: Iterable[tuple[str, PathLike[str]]]) -> None:
    asyncio.run(_download_files(to_download))


async def _download_files(to_download: Iterable[tuple[str, PathLike[str]]]) -> None:
    queue = deque(to_download)
    client = aiohttp.ClientSession()

    async def process_queue() -> None:
        while queue:
            url, out_path = queue.popleft()
            await _download(client, url, out_path)

    async with client:
        downloaders = [asyncio.create_task(process_queue()) for _ in range(CONCURRENCY_LIMIT)]
        try:
            await asyncio.gather(*downloaders)
        finally:
            for d in downloaders:
                d.cancel()


async def _download(client: ClientSession, url: str, out_path: PathLike[str]) -> None:
    log.debug("downloading %s", Path(out_path).name)
    async with client.get(url, raise_for_status=True) as resp:
        with open(out_path, "wb") as f:
            async for chunk in resp.content.iter_chunked(CHUNK_SIZE):
                f.write(chunk)
    log.debug("downloaded %s", Path(out_path).name)
