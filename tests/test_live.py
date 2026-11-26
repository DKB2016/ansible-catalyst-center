import os
import requests

def test_auth_and_sites():
    host = os.environ["CC_HOST"].rstrip("/")
    verify = os.getenv("CC_VERIFY", "true").lower() == "true"
    assert verify or host in ("https://sandboxdnac.cisco.com", "https://sandboxdnac2.cisco.com")
    response = requests.post(host + "/dna/system/api/v1/auth/token", auth=(os.environ["CC_USERNAME"], os.environ["CC_PASSWORD"]), verify=verify, timeout=30)
    assert response.status_code == 200
    token = response.json()["Token"]
    assert token
    response = requests.get(host + "/dna/intent/api/v1/site", headers={"X-Auth-Token": token}, verify=verify, timeout=30)
    assert response.status_code == 200
    assert isinstance(response.json()["response"], list)
