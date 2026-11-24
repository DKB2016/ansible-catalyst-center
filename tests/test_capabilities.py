import os
import pytest
import requests

@pytest.fixture(scope="module")
def client():
    host = os.environ["CC_HOST"].rstrip("/")
    assert host in ("https://sandboxdnac.cisco.com", "https://sandboxdnac2.cisco.com")
    session = requests.Session()
    session.verify = os.getenv("CC_VERIFY", "true").lower() == "true"
    result = session.post(host + "/dna/system/api/v1/auth/token", auth=(os.environ["CC_USERNAME"], os.environ["CC_PASSWORD"]), timeout=30)
    assert result.status_code == 200
    session.headers["X-Auth-Token"] = result.json()["Token"]
    yield session, host
    session.close()

@pytest.mark.parametrize("path", ["/dna/intent/api/v1/site", "/dna/intent/api/v1/network-device", "/dna/intent/api/v1/network-device/count"])
def test_read_capability(client, path):
    session, host = client
    result = session.get(host + path, timeout=30)
    assert result.status_code == 200
    assert "response" in result.json()

def test_version_discovery(client):
    session, host = client
    result = session.get(host + "/dna/intent/api/v1/dnac-release", timeout=30)
    assert result.status_code == 200
    payload = result.json()
    assert payload
    import re
    version = payload["response"]["installedVersion"]
    assert isinstance(version, str)
    assert re.fullmatch(r"\d+\.\d+\.\d+(?:\.\d+)?", version), "Unexpected installedVersion format"
    print("Installed Catalyst Center version:", version)


def test_installed_release_probe(client):
    session, host = client
    result = session.get(host + "/dna/system/api/v1/installedRelease", timeout=30, allow_redirects=False)
    print("Installed release HTTP status:", result.status_code)
    if result.status_code in (403, 404, 501):
        pytest.skip("Installed release endpoint unavailable")
    assert result.status_code == 200
    import re
    def inspect(value, path=""):
        if isinstance(value, dict):
            for key, item in value.items():
                inspect(item, path + "." + key)
        elif isinstance(value, list):
            for item in value:
                inspect(item, path + "[]")
        elif isinstance(value, str) and re.fullmatch(r"\d+\.\d+\.\d+(?:\.\d+)?", value):
            print("Version field:", path, value)
    inspect(result.json())
