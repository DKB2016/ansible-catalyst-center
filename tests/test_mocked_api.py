"""Mock the existing live API fixture without network or real credentials."""
import importlib.util
from pathlib import Path
from unittest.mock import Mock

import pytest
import requests


@pytest.fixture
def api(monkeypatch):
    # Locate the integration module by its existing fixture contract.
    candidates = []
    for path in Path(__file__).parent.glob("test_*.py"):
        if path != Path(__file__) and "def test_read_capability(client, path):" in path.read_text():
            candidates.append(path)
    assert len(candidates) == 1
    spec = importlib.util.spec_from_file_location("mocked_live_contract", candidates[0])
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setenv("CC_HOST", "https://sandboxdnac.cisco.com")
    monkeypatch.setenv("CC_USERNAME", "dummy")
    monkeypatch.setenv("CC_PASSWORD", "dummy")
    monkeypatch.setenv("CC_VERIFY", "true")
    session = Mock(spec=requests.Session())
    session.headers = {}
    session.post.return_value.status_code = 200
    session.post.return_value.json.return_value = {"Token": "mock-token"}
    session.get.return_value.status_code = 200
    session.get.return_value.json.return_value = {"response": []}
    monkeypatch.setattr(requests, "Session", lambda: session)
    return module, session


def test_mocked_read_success(api):
    module, session = api
    fixture = module.client.__wrapped__()
    client = next(fixture)
    try:
        module.test_read_capability(client, "/dna/intent/api/v1/site")
        session.post.assert_called_once_with(
            "https://sandboxdnac.cisco.com/dna/system/api/v1/auth/token",
            auth=("dummy", "dummy"), timeout=30,
        )
        session.get.assert_called_once_with(
            "https://sandboxdnac.cisco.com/dna/intent/api/v1/site", timeout=30,
        )
        assert session.headers == {"X-Auth-Token": "mock-token"}
        assert session.verify is True
    finally:
        fixture.close()


@pytest.mark.parametrize("status", [401, 403, 500])
def test_mocked_auth_failure(api, status):
    module, session = api
    session.post.return_value.status_code = status
    with pytest.raises(AssertionError):
        next(module.client.__wrapped__())
    session.get.assert_not_called()


@pytest.mark.parametrize("status,payload", [(403, {}), (200, {}), (500, {})])
def test_mocked_read_failure(api, status, payload):
    module, session = api
    session.get.return_value.status_code = status
    session.get.return_value.json.return_value = payload
    with pytest.raises(AssertionError):
        module.test_read_capability((session, "https://sandboxdnac.cisco.com"),
                                    "/dna/intent/api/v1/site")
    session.post.assert_not_called()


def test_mocked_unknown_host_rejected(api, monkeypatch):
    module, session = api
    monkeypatch.setenv("CC_HOST", "https://other.example")
    with pytest.raises(AssertionError):
        next(module.client.__wrapped__())
    session.post.assert_not_called()
    session.get.assert_not_called()
