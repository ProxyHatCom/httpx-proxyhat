# httpx-proxyhat

Route [httpx](https://github.com/encode/httpx) requests through [ProxyHat](https://proxyhat.com?utm_source=github&utm_medium=readme&utm_campaign=httpx) residential proxies — drop-in sync and async clients with a sticky residential IP pinned for the client's lifetime, plus geo-targeting and rotation.

[![CI](https://github.com/ProxyHatCom/httpx-proxyhat/actions/workflows/ci.yml/badge.svg)](https://github.com/ProxyHatCom/httpx-proxyhat/actions/workflows/ci.yml)
[![Compatible with httpx latest](https://github.com/ProxyHatCom/httpx-proxyhat/actions/workflows/compat.yml/badge.svg)](https://github.com/ProxyHatCom/httpx-proxyhat/actions/workflows/compat.yml)
[![PyPI](https://img.shields.io/pypi/v/httpx-proxyhat)](https://pypi.org/project/httpx-proxyhat/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> [!TIP]
> **Recommended proxies — [ProxyHat](https://proxyhat.com?utm_source=github&utm_medium=readme&utm_campaign=httpx&utm_content=callout) residential IPs.** Every feature in this package is tested end-to-end against ProxyHat and works great. First-class integration; also works with any proxy, or none.


## Why

Scraping or hitting APIs straight from a datacenter IP gets you flagged, rate-limited and blocked. `httpx` has first-class proxy support (`proxy=` on `Client` / `AsyncClient`), and this package wires ProxyHat's residential IPs (50M+ across 148+ countries) into it — one pinned residential IP per client by default, so cookies and TLS sessions stay coherent while you work. `ProxyHatClient` / `ProxyHatAsyncClient` are drop-in subclasses of `httpx.Client` / `httpx.AsyncClient`: same API, every request routed. No fork, no boilerplate.

## Install

```bash
pip install httpx-proxyhat
```

For a SOCKS5 gateway, install the httpx SOCKS extra too:

```bash
pip install "httpx-proxyhat[socks]"
```

## Quick start

```python
from httpx_proxyhat import ProxyHatClient

# An API key auto-selects an active residential sub-user:
with ProxyHatClient(api_key="ph_your_api_key", country="us") as client:
    r = client.get("https://api.ipify.org?format=json")
    print(r.json())   # a US residential IP, pinned for the whole client
```

Async is identical:

```python
from httpx_proxyhat import ProxyHatAsyncClient

async with ProxyHatAsyncClient(country="de") as client:
    r = await client.get("https://api.ipify.org?format=json")
```

Get an API key at [proxyhat.com](https://proxyhat.com?utm_source=github&utm_medium=readme&utm_campaign=httpx).

Already wiring httpx yourself? Grab the raw proxy URL:

```python
import httpx
from httpx_proxyhat import proxyhat_proxy_url

proxy = proxyhat_proxy_url(country="gb", sticky="1h")
# -> "http://<user>-country-gb-sid-<id>-ttl-1h:<pass>@gate.proxyhat.com:8080"

with httpx.Client(proxy=proxy) as client:
    client.get("https://example.com")
```

## Credentials

Pass them explicitly or via environment variables — options win over env:

| Option | Env var | Notes |
|---|---|---|
| `api_key` | `PROXYHAT_API_KEY` | Auto-selects an active sub-user with remaining traffic |
| `sub_user` | `PROXYHAT_SUBUSER` | Pick a specific sub-user by uuid or name (with an API key) |
| `username` | `PROXYHAT_USERNAME` | Explicit gateway `proxy_username` (skips the API) |
| `password` | `PROXYHAT_PASSWORD` | Explicit gateway `proxy_password` |

## Targeting

Every option is accepted by `ProxyHatClient`, `ProxyHatAsyncClient` and `proxyhat_proxy_url`:

```python
ProxyHatClient(
    protocol="http",        # or "socks5" (needs the [socks] extra)
    country="us",           # ISO code or "any" (default)
    region="california",
    city="new_york",
    filter="high",          # AI IP-quality tier
    sticky="30m",           # client lifetime (default); sticky=False rotates
    timeout=30.0,           # any extra kwarg is forwarded to httpx.Client
    headers={"user-agent": "my-scraper/1.0"},
    follow_redirects=True,
)
```

### Sticky IP per client (default)

A client typically makes many requests against the same site — paging, following links, keeping a login. If the exit IP changed mid-session the site would see a user teleporting between cities and block it. So this package is **sticky by default**: one residential IP is pinned for the whole client (`sticky="30m"`, renewed as you work), so cookies, TLS sessions and fingerprint stay coherent. The resolved URL is on `client.proxyhat_url`.

Want a fresh IP on **every** connection instead (e.g. many independent one-shot fetches)? Turn stickiness off:

```python
from httpx_proxyhat import ProxyHatClient

with ProxyHatClient(country="us", sticky=False) as client:   # rotating residential IP
    for url in urls:
        client.get(url)
```

Set a custom lifetime with `sticky="2h"`.

## How it works

`proxyhat_proxy_url(...)` resolves your gateway credentials (via the official [`proxyhat`](https://pypi.org/project/proxyhat/) SDK — an API key auto-picks an active sub-user, or pass `username`/`password`), then builds the proxy URL: the host is the ProxyHat gateway (`gate.proxyhat.com:8080`, or `:1080` for SOCKS5) and the username carries ProxyHat's targeting grammar (`<user>-country-us-sid-<id>-ttl-30m`). `ProxyHatClient` / `ProxyHatAsyncClient` build that URL and pass it to httpx's `proxy=` parameter, so every request the client makes is tunnelled through a residential IP. A sticky username (with a session id) pins one IP for the client's lifetime; a rotating one (no session id) makes the gateway hand out a fresh IP per new connection.

## License

MIT © [ProxyHat](https://proxyhat.com)
