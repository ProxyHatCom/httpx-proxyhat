"""``proxyhat_proxy_url`` builds the gateway proxy URL — pure, offline, no client."""

from httpx_proxyhat import proxyhat_proxy_url


class TestProxyUrl:
    def test_geo_reflected_in_url(self):
        url = proxyhat_proxy_url(username="ph-1", password="pw", country="us", sticky=False)
        assert url == "http://ph-1-country-us:pw@gate.proxyhat.com:8080"

    def test_sticky_default_pins_session(self):
        url = proxyhat_proxy_url(username="ph-1", password="pw")
        # Default is sticky: a session id + 30m TTL is present so one IP is pinned.
        assert "-sid-" in url
        assert "-ttl-30m" in url

    def test_sticky_false_is_rotating(self):
        url = proxyhat_proxy_url(username="ph-1", password="pw", sticky=False)
        assert "-sid-" not in url
        assert "-ttl-" not in url

    def test_custom_sticky_ttl(self):
        url = proxyhat_proxy_url(username="ph-1", password="pw", sticky="2h")
        assert "-sid-" in url
        assert "-ttl-2h" in url

    def test_full_geo_targeting(self):
        url = proxyhat_proxy_url(
            username="ph-1",
            password="pw",
            country="de",
            region="berlin",
            city="berlin",
            filter="high",
            sticky=False,
        )
        assert "ph-1-country-de" in url
        assert "-region-berlin" in url
        assert "-city-berlin" in url
        assert "-filter-high" in url

    def test_http_port_and_scheme(self):
        url = proxyhat_proxy_url(username="ph-1", password="pw", sticky=False)
        assert url.startswith("http://")
        assert "@gate.proxyhat.com:8080" in url

    def test_socks5_protocol(self):
        url = proxyhat_proxy_url(username="ph-1", password="pw", protocol="socks5", sticky=False)
        assert url.startswith("socks5://")
        assert "@gate.proxyhat.com:1080" in url

    def test_credentials_are_url_encoded(self):
        # A password with URL-unsafe characters must be percent-encoded so the URL parses.
        url = proxyhat_proxy_url(username="ph-1", password="p@ss:word", sticky=False)
        assert "p%40ss%3Aword" in url
