# ansible-catalyst-center

Sprint 1 read-only foundation. From the repository root, use Python 3.12 and install `pip install -r requirements.txt ansible-core==2.19.4`.

Edit `inventory/hosts.yml` for the controller HTTPS URL and TLS verification. Group defaults in `inventory/group_vars/catalyst_center.yml` define environment, read-only mode and an empty desired-state mapping. TLS verification defaults to true; only the explicitly allowed shared sandbox endpoints may disable it. Supply CC_USERNAME and CC_PASSWORD through your shell secret manager or CI secrets, never commit them or pass them on the command line.

```sh
ansible-inventory --graph
ansible-playbook playbooks/preflight.yml --syntax-check
ansible-playbook playbooks/preflight.yml
pytest -q tests/test_preflight.py
```

The preflight playbook runs the preflight role independently; it validates inputs locally and does not yet establish controller compatibility. The master entry point is `playbooks/site.yml`. No configuration mutations are supported. Local tests use dummy credentials. Live integration is restricted to read-only sandbox API probes. See docs/test-status.md for evidence and limitations.
