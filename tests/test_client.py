"""``ProxyHatClient`` / ``ProxyHatAsyncClient`` — subclasses that route httpx through ProxyHat.

All offline: constructing an http client never connects, and the one request-path
check inspects httpx's own transport wiring rather than hitting the network.
"""

import httpx
import pytest
from conftest import patch_sdk, sub_user

from httpx_proxyhat import ProxyHatAsyncClient, ProxyHatClient


class TestSyncClient:
    def test_is_httpx_client_subclass(self):
        with ProxyHatClient(username="ph-1", password="pw") as client:
            assert isinstance(client, httpx.Client)

    def test_sticky_by_default(self):
        with ProxyHatClient(username="ph-1", password="pw", country="us") as client:
            assert "ph-1-country-us" in client.proxyhat_url
            assert "-sid-" in client.proxyhat_url
            assert "-ttl-30m" in client.proxyhat_url

    def test_rotating_when_sticky_false(self):
        with ProxyHatClient(username="ph-1", password="pw", country="de", sticky=False) as client:
            assert client.proxyhat_url == "http://ph-1-country-de:pw@gate.proxyhat.com:8080"
            assert "-sid-" not in client.proxyhat_url

    def test_proxy_is_wired_into_transport(self):
        # The deep hook: httpx builds a proxy transport whose pool points at the gateway.
        with ProxyHatClient(username="ph-1", password="pw", country="us") as client:
            mounts = list(client._mounts.values())
            assert len(mounts) == 1
            pool = mounts[0]._pool
            assert type(pool).__name__ == "HTTPProxy"
            assert pool._proxy_url.host == b"gate.proxyhat.com"
            assert pool._proxy_url.port == 8080

    def test_forwards_proxy_and_extra_kwargs_to_httpx(self, monkeypatch):
        captured = {}

        def fake_init(self, **kwargs):
            captured.update(kwargs)

        monkeypatch.setattr(httpx.Client, "__init__", fake_init)
        ProxyHatClient(
            username="ph-1",
            password="pw",
            country="gb",
            timeout=5.0,
            headers={"user-agent": "x"},
            follow_redirects=True,
        )
        assert captured["proxy"].startswith("http://ph-1-country-gb")
        assert captured["timeout"] == 5.0
        assert captured["headers"] == {"user-agent": "x"}
        assert captured["follow_redirects"] is True


class TestAsyncClient:
    async def test_is_async_client_subclass(self):
        async with ProxyHatAsyncClient(username="ph-1", password="pw") as client:
            assert isinstance(client, httpx.AsyncClient)

    async def test_sticky_by_default(self):
        async with ProxyHatAsyncClient(username="ph-1", password="pw", country="us") as client:
            assert "ph-1-country-us" in client.proxyhat_url
            assert "-sid-" in client.proxyhat_url

    async def test_rotating_when_sticky_false(self):
        async with ProxyHatAsyncClient(username="ph-1", password="pw", country="fr", sticky=False) as client:
            assert client.proxyhat_url == "http://ph-1-country-fr:pw@gate.proxyhat.com:8080"

    async def test_forwards_proxy_and_extra_kwargs_to_httpx(self, monkeypatch):
        captured = {}

        def fake_init(self, **kwargs):
            captured.update(kwargs)

        monkeypatch.setattr(httpx.AsyncClient, "__init__", fake_init)
        ProxyHatAsyncClient(username="ph-1", password="pw", country="jp", timeout=9.0)
        assert captured["proxy"].startswith("http://ph-1-country-jp")
        assert captured["timeout"] == 9.0


class TestApiKeyResolution:
    def test_client_resolves_sub_user_via_api_key(self, monkeypatch):
        patch_sdk(monkeypatch, [sub_user(proxy_username="good", proxy_password="secret")])
        with ProxyHatClient(api_key="ph_key", country="us", sticky=False) as client:
            assert client.proxyhat_url == "http://good-country-us:secret@gate.proxyhat.com:8080"

    def test_proxy_url_resolves_named_sub_user(self, monkeypatch):
        from httpx_proxyhat import proxyhat_proxy_url

        patch_sdk(
            monkeypatch,
            [sub_user(uuid="a", proxy_username="aaa"), sub_user(uuid="b", name="prod", proxy_username="bbb")],
        )
        url = proxyhat_proxy_url(api_key="ph_key", sub_user="prod", sticky=False)
        assert url.startswith("http://bbb-country-any")

    def test_client_raises_without_credentials(self, monkeypatch):
        from httpx_proxyhat import ProxyHatConfigError

        for var in ("PROXYHAT_API_KEY", "PROXYHAT_USERNAME", "PROXYHAT_PASSWORD", "PROXYHAT_SUBUSER"):
            monkeypatch.delenv(var, raising=False)
        with pytest.raises(ProxyHatConfigError):
            ProxyHatClient()
