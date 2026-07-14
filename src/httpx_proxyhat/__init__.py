"""httpx-proxyhat — route httpx requests through ProxyHat residential proxies."""

from httpx_proxyhat._resolve import ProxyHatConfigError, resolve_credentials
from httpx_proxyhat.client import (
    ProxyHatAsyncClient,
    ProxyHatClient,
    proxyhat_proxy_url,
)

__all__ = [
    "ProxyHatAsyncClient",
    "ProxyHatClient",
    "ProxyHatConfigError",
    "proxyhat_proxy_url",
    "resolve_credentials",
]
__version__ = "0.1.1"
