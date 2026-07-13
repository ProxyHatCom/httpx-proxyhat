"""httpx clients that route through the ProxyHat residential gateway.

``httpx`` takes a single ``proxy=`` URL on ``httpx.Client`` / ``httpx.AsyncClient``.
``ProxyHatClient`` / ``ProxyHatAsyncClient`` are thin subclasses that resolve your
ProxyHat credentials, build the gateway proxy URL with the official ``proxyhat``
SDK's targeting grammar, and hand it to ``proxy=`` — so every request the client
makes goes through a residential IP.

**Sticky by default.** A ProxyHat sticky username carries a session id, so one
residential IP is pinned for the whole client's lifetime (cookies, TLS session
and fingerprint stay coherent). Pass ``sticky=False`` for a *rotating* client: a
stable username with no session id, which makes the gateway hand out a fresh
residential IP per new connection.

``proxyhat_proxy_url(...)`` returns the raw proxy URL string for wiring httpx
(or anything that speaks the proxy-URL convention) by hand.
"""

from __future__ import annotations

from typing import Any

import httpx
from proxyhat import build_connection_url

from httpx_proxyhat._resolve import resolve_credentials

# Sticky by default: pin one residential IP for the client's lifetime. Renewed as
# the client works; override with any TTL string ("2h") or turn off with False.
DEFAULT_STICKY = "30m"


def proxyhat_proxy_url(
    *,
    api_key: str | None = None,
    username: str | None = None,
    password: str | None = None,
    sub_user: str | None = None,
    country: str | None = None,
    region: str | None = None,
    city: str | None = None,
    sticky: bool | str | None = DEFAULT_STICKY,
    filter: str | None = None,
    protocol: str = "http",
) -> str:
    """Build a ProxyHat gateway proxy URL for ``httpx``.

    Resolves credentials (an ``api_key`` auto-picks an active sub-user, or pass
    ``username``/``password``) and returns a URL like
    ``http://<user>-country-us-sid-<id>-ttl-30m:<pass>@gate.proxyhat.com:8080``.
    Pass it to ``proxy=`` on ``httpx.Client`` / ``httpx.AsyncClient`` yourself, or
    let :class:`ProxyHatClient` / :class:`ProxyHatAsyncClient` do it for you.

    Sticky vs rotating:

    - ``sticky="30m"`` (default) or ``sticky=True`` pins one residential IP.
    - ``sticky=False`` (or ``None``) rotates: a fresh IP per new connection.
    - ``sticky="2h"`` sets a custom session lifetime.

    Geo/quality targeting: ``country`` (ISO code or ``"any"``), ``region``,
    ``city``, ``filter`` (AI IP-quality tier). ``protocol`` is ``"http"`` (default)
    or ``"socks5"`` (needs ``httpx[socks]`` installed to actually connect).
    """
    user, pw = resolve_credentials(
        api_key=api_key,
        username=username,
        password=password,
        sub_user=sub_user,
    )
    return build_connection_url(
        username=user,
        password=pw,
        country=country,
        region=region,
        city=city,
        sticky=sticky,
        filter=filter,
        protocol=protocol,
    )


class ProxyHatClient(httpx.Client):
    """A ``httpx.Client`` that sends every request through ProxyHat.

    Drop-in for ``httpx.Client``: it builds the gateway proxy URL from your
    ProxyHat credentials + targeting and passes it to ``proxy=``. Sticky by
    default (one pinned residential IP for the client's lifetime); pass
    ``sticky=False`` to rotate. Any extra keyword arguments (``timeout``,
    ``headers``, ``follow_redirects``, ``verify``, …) are forwarded to
    ``httpx.Client`` unchanged.

    ```python
    from httpx_proxyhat import ProxyHatClient

    with ProxyHatClient(country="us") as client:   # sticky US residential IP
        r = client.get("https://api.ipify.org")
    ```

    The resolved proxy URL is available as ``client.proxyhat_url``.
    """

    def __init__(
        self,
        *,
        api_key: str | None = None,
        username: str | None = None,
        password: str | None = None,
        sub_user: str | None = None,
        country: str | None = None,
        region: str | None = None,
        city: str | None = None,
        sticky: bool | str | None = DEFAULT_STICKY,
        filter: str | None = None,
        protocol: str = "http",
        **httpx_kwargs: Any,
    ) -> None:
        proxy_url = proxyhat_proxy_url(
            api_key=api_key,
            username=username,
            password=password,
            sub_user=sub_user,
            country=country,
            region=region,
            city=city,
            sticky=sticky,
            filter=filter,
            protocol=protocol,
        )
        self.proxyhat_url = proxy_url
        super().__init__(proxy=proxy_url, **httpx_kwargs)


class ProxyHatAsyncClient(httpx.AsyncClient):
    """A ``httpx.AsyncClient`` that sends every request through ProxyHat.

    The async twin of :class:`ProxyHatClient` — same arguments, same
    sticky-by-default behaviour, forwards extra kwargs to ``httpx.AsyncClient``.

    ```python
    from httpx_proxyhat import ProxyHatAsyncClient

    async with ProxyHatAsyncClient(country="de", sticky=False) as client:
        r = await client.get("https://api.ipify.org")   # rotating DE IP
    ```

    The resolved proxy URL is available as ``client.proxyhat_url``.
    """

    def __init__(
        self,
        *,
        api_key: str | None = None,
        username: str | None = None,
        password: str | None = None,
        sub_user: str | None = None,
        country: str | None = None,
        region: str | None = None,
        city: str | None = None,
        sticky: bool | str | None = DEFAULT_STICKY,
        filter: str | None = None,
        protocol: str = "http",
        **httpx_kwargs: Any,
    ) -> None:
        proxy_url = proxyhat_proxy_url(
            api_key=api_key,
            username=username,
            password=password,
            sub_user=sub_user,
            country=country,
            region=region,
            city=city,
            sticky=sticky,
            filter=filter,
            protocol=protocol,
        )
        self.proxyhat_url = proxy_url
        super().__init__(proxy=proxy_url, **httpx_kwargs)
