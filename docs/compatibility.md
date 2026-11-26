# Compatibility candidates

Source: https://github.com/cisco-en-programmability/catalystcenter-ansible and https://developer.cisco.com/docs/catalyst-center/ansible/

| Appliance | Collection | SDK |
|---|---|---|
| 2.3.7.6 | 1.0.0 | 2.3.7.6.2 |
| 2.3.7.9 | 2.1.4 | 2.3.7.9.5 |
| 3.1.3.0 | 2.2.2 | 3.1.3.0.1 |
| 3.1.6.0 | 2.10.2 | 3.1.3.6.x |
| 3.2.3.0 | 2.11.0 | 3.2.3.0.x |

These are upstream recommendations, not locally verified combinations. Select exact SDK patch after appliance version discovery; verify installation and live native reads before closing compatibility issues. Python 3.12 is the initial CI controller target.
