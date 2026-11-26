"""Local-only tests: preflight performs no controller requests."""
import json
import os
import subprocess

import pytest


@pytest.mark.parametrize("overrides,valid", [
    ({}, True),
    ({"cc_require_compatibility": False}, True),
    ({"cc_require_compatibility": "true"}, False),
    ({"cc_require_compatibility": True}, False),
    ({"cc_require_compatibility": True, "cc_expected_release": "2.3.7.9"}, False),
    ({"cc_expected_release": "2.3.7.9"}, True),
    ({"cc_expected_release": "3.1.3"}, True),
    ({"cc_expected_release": "latest"}, False),
    ({"cc_expected_release": 2379}, False),
    ({"cc_expected_release": ""}, False),
    ({"cc_preflight_probe": "true"}, False),
    ({"cc_preflight_probe": 1}, False),
    ({"cc_preflight_probe": False}, True),
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
        assert "not_requested" in output
        assert "unverified" in output
    else:
        assert "Report local validation evidence" not in output


def test_probe_structure():
    from pathlib import Path

    import yaml

    tasks = yaml.safe_load(Path("roles/catalyst_center_preflight/tasks/main.yml").read_text())
    names = [task["name"] for task in tasks]
    assert len(names) == len(set(names))
    probe = next(task for task in tasks if task["name"] == "Probe controller connectivity")
    requests = [task for task in probe["block"] if "ansible.builtin.uri" in task]
    assert [task["ansible.builtin.uri"]["method"] for task in requests] == ["POST", "GET", "GET"]
    assert requests[0]["ansible.builtin.uri"]["url"].endswith("/auth/token")
    for task in requests:
        assert task["no_log"] is True
        assert task["ansible.builtin.uri"]["follow_redirects"] == "none"
    assert len(probe["rescue"]) == 1


@pytest.mark.parametrize("overrides,valid", [
    ({}, True),
    ({"cc_mode": "write"}, False),
    ({"cc_desired_state": {"sites": []}}, False),
])
def test_master_read_only(overrides, valid):
    env = dict(os.environ, CC_USERNAME="dummy-user", CC_PASSWORD="dummy-secret")
    result = subprocess.run(
        ["ansible-playbook", "playbooks/site.yml", "-e", json.dumps(overrides)],
        env=env, capture_output=True, text=True, timeout=60,
    )
    output = result.stdout + result.stderr
    assert "dummy-secret" not in output
    assert (result.returncode == 0) == valid, output
    assert "Obtain authentication token" not in output or "skipping:" in output
    if valid:
        assert "not_requested" in output
        assert "changed=0" in output
        assert "failed=0" in output
    else:
        assert "Report local validation evidence" not in output


@pytest.mark.parametrize("count,valid", [(0, True), (12, True), (-1, False), (1.5, False), (True, False), ("12", False), (None, False)])
def test_inventory_count_contract(count, valid):
    from pathlib import Path
    from jinja2 import Environment, StrictUndefined
    import yaml

    tasks = yaml.safe_load(Path("roles/catalyst_center_preflight/tasks/main.yml").read_text())
    probe = next(task for task in tasks if task["name"] == "Probe controller connectivity")
    task = next(task for task in probe["block"] if task["name"] == "Validate inventory response")
    env = Environment(undefined=StrictUndefined)
    context = {"cc_preflight_count": {"json": {"response": count}}}
    assert all(env.compile_expression(expr)(**context) for expr in task["ansible.builtin.assert"]["that"]) == valid


@pytest.mark.parametrize("token,valid", [("token", True), (" ", False), ("", False), (None, False), (123, False)])
def test_auth_token_contract(token, valid):
    from pathlib import Path
    from jinja2 import Environment, StrictUndefined
    import yaml

    tasks = yaml.safe_load(Path("roles/catalyst_center_preflight/tasks/main.yml").read_text())
    probe = next(task for task in tasks if task["name"] == "Probe controller connectivity")
    task = next(task for task in probe["block"] if task["name"] == "Validate authentication response")
    env = Environment(undefined=StrictUndefined)
    context = {"cc_preflight_auth": {"json": {"Token": token}}}
    assert all(env.compile_expression(expr)(**context) for expr in task["ansible.builtin.assert"]["that"]) == valid


@pytest.mark.parametrize("release,expected,valid", [
    ("2.3.7.9", "2.3.7.9", True),
    ("3.723.75300", "2.3.7.9", False),
    ("2.3.7.6", "2.3.7.9", False),
])
def test_release_expectation_contract(release, expected, valid):
    from pathlib import Path
    from jinja2 import Environment, StrictUndefined
    import yaml

    tasks = yaml.safe_load(Path("roles/catalyst_center_preflight/tasks/main.yml").read_text())
    probe = next(task for task in tasks if task["name"] == "Probe controller connectivity")
    task = next(task for task in probe["block"] if task["name"] == "Validate release against explicit deployment expectation")
    env = Environment(undefined=StrictUndefined)
    context = {"cc_expected_release": expected, "cc_preflight_release": {"json": {"response": {"installedVersion": release}}}}
    assert all(env.compile_expression(expr)(**context) for expr in task["ansible.builtin.assert"]["that"]) == valid


@pytest.mark.parametrize("expected,release", [
    ("2.3.7.9", "2.3.7.9"),
    ("3.1.3.0", "3.1.3.0"),
])
def test_native_compatibility_gate_fails_closed(expected, release):
    from pathlib import Path
    import yaml

    tasks = yaml.safe_load(Path("roles/catalyst_center_preflight/tasks/main.yml").read_text())
    probe = next(task for task in tasks if task["name"] == "Probe controller connectivity")
    # Execute the actual gate with a matched release but no verified native stack.
    gate = next(task for task in probe["block"] if task["name"] == "Reject unverified native compatibility when required")
    import tempfile
    with tempfile.TemporaryDirectory() as directory:
        play = Path(directory) / "gate.yml"
        play.write_text(yaml.safe_dump([{
            "name": "Exercise native compatibility gate",
            "hosts": "localhost",
            "gather_facts": False,
            "vars": {"cc_require_compatibility": True, "cc_expected_release": expected,
                     "cc_preflight_release": {"json": {"response": {"installedVersion": release}}}},
            "tasks": [gate],
        }]))
        result = subprocess.run(
            ["ansible-playbook", "-i", "localhost,", "-c", "local", str(play)],
            capture_output=True, text=True, timeout=60,
        )
        assert result.returncode != 0
        assert "Native collection and SDK compatibility has not been verified" in result.stdout
