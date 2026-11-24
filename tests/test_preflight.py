"""Local-only tests: preflight performs no controller requests."""
import json
import os
import subprocess

import pytest


@pytest.mark.parametrize("overrides,valid", [
    ({}, True),
    ({"cc_mode": "READ_ONLY"}, False),
    ({"cc_mode": True}, False),
    ({"cc_host": "http://sandboxdnac.cisco.com"}, False),
    ({"cc_host": "https://sandboxdnac.cisco.com.evil.example"}, False),
    ({"cc_host": "https://sandboxdnac.cisco.com/path"}, False),
    ({"cc_host": "https://sandboxdnac.cisco.com:443"}, False),
    ({"cc_environment": "production", "cc_mode": "write"}, False),
    ({"cc_desired_state": None}, False),
    ({"cc_mode": "write"}, False),
    ({"cc_host": "https://sandboxdnac.cisco.com@evil.example"}, False),
    ({"cc_host": "https://other.example"}, False),
    ({"cc_verify": "false"}, False),
    ({"cc_desired_state": {"sites": []}}, False),
    ({"cc_desired_state": []}, False),
    ({"cc_environment": "unknown"}, False),
    ({"cc_username": ""}, False),
    ({"cc_password": " "}, False),
])
def test_preflight(overrides, valid):
    env = dict(os.environ, CC_USERNAME="dummy-user", CC_PASSWORD="dummy-secret")
    result = subprocess.run(
        ["ansible-playbook", "playbooks/preflight.yml", "-e", json.dumps(overrides)],
        env=env, capture_output=True, text=True, timeout=60,
    )
    output = result.stdout + result.stderr
    assert "dummy-secret" not in output
    assert (result.returncode == 0) == valid, output
    if valid:
        assert "failed=0" in output
        assert "changed=0" in output
