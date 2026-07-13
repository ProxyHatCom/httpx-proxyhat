"""Fetch your exit IP through ProxyHat with httpx — sync and async.

Set PROXYHAT_API_KEY (or PROXYHAT_USERNAME / PROXYHAT_PASSWORD) first:

    export PROXYHAT_API_KEY=ph_your_api_key
    python examples/basic.py
"""

import asyncio

from httpx_proxyhat import ProxyHatAsyncClient, ProxyHatClient


def sync_example() -> None:
    # Sticky by default: one US residential IP pinned for the whole client.
    with ProxyHatClient(country="us") as client:
        print("sync :", client.proxyhat_url.split("@")[-1])
        print("       ", client.get("https://api.ipify.org?format=json").json())


async def async_example() -> None:
    # Rotating: a fresh residential IP per new connection.
    async with ProxyHatAsyncClient(country="de", sticky=False) as client:
        r = await client.get("https://api.ipify.org?format=json")
        print("async:", r.json())


if __name__ == "__main__":
    sync_example()
    asyncio.run(async_example())
