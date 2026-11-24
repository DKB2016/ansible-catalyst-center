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
    import json
    versions = sorted(set(re.findall(r"\b\d+\.\d+\.\d+(?:\.\d+)?\b", json.dumps(payload))))
    assert versions, "No release version found in response"
    print("Release candidates:", ", ".join(versions))
