#!/usr/bin/env bash
# Verify the baseline wheelhouse without using a package index.
set -euo pipefail
cd "$(dirname "$0")/.."
bundle="$(realpath "${1:-offline}")"
(cd "$bundle" && sha256sum --strict -c SHA256SUMS)
venv="$(mktemp -d)"
trap 'rm -rf "$venv"' EXIT
python3.12 -m venv "$venv"
export PATH="$venv/bin:$PATH"
export PIP_CONFIG_FILE=/dev/null
python -m pip --isolated install --no-index --find-links="$bundle/wheels" \
  -r requirements.txt ansible-core==2.19.4 ansible-lint==25.9.2
python -m pip check
ansible-inventory --graph
ansible-playbook playbooks/site.yml --syntax-check
python -m pytest -q tests/test_preflight.py tests/test_mocked_api.py
