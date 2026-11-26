# Offline installation (Sprint 1 candidate)

Prepare on an internet-connected Linux host matching the disconnected target's architecture, OS ABI and Python 3.12. Use a clean virtual environment. Do not transfer credentials, inventories containing secrets, or pip configuration.

## Prepare the current read-only baseline

From the repository root:

```sh
python3.12 -m venv .build-venv
. .build-venv/bin/activate
mkdir -p offline/wheels offline/collections
python -m pip download --only-binary=:all: --dest offline/wheels -r requirements.txt ansible-core==2.19.4 ansible-lint==25.9.2
(cd offline && find wheels collections -type f -print0 | sort -z | xargs -0 sha256sum > SHA256SUMS)
```

A missing compatible wheel is a build failure, not permission to silently use an sdist. Review dependencies and hashes before transfer. The manifest detects corruption; authenticate the manifest via your approved transfer/signing process.

## Native collection extension (not yet accepted)

After issues #2–4 establish the exact compatible collection and SDK versions, add the pinned SDK to the wheel download command and download the pinned collection and its dependencies:

```sh
ansible-galaxy collection download -r requirements.yml -p offline/collections
```

The requirements.yml in this example is a future pinned collection manifest, not a file currently provided by the baseline. Regenerate SHA256SUMS after adding artifacts. Do not select versions based solely on the internal controller build number.

## Install on the disconnected host

```sh
(cd offline && sha256sum -c SHA256SUMS)
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip --isolated install --no-index --find-links=offline/wheels -r requirements.txt ansible-core==2.19.4 ansible-lint==25.9.2
python -m pip check
ansible-inventory --graph
ansible-playbook playbooks/site.yml --syntax-check
pytest -q tests/test_preflight.py tests/test_mocked_api.py
```

Once native artifacts are approved, install from the generated local manifest:

```sh
(cd offline/collections && ansible-galaxy collection install --offline -r requirements.yml)
ansible-galaxy collection list
```

Run in an environment with outbound networking disabled to independently establish offline behavior. Record Python version, architecture, manifest digest, installed versions and test results. The baseline instructions are not proof of native compatibility or a verified air-gapped installation.
