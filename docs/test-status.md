# Verification ledger

## Verified baseline
GitHub Actions run 45404017981, job 138479786954: 5 passed, 5 warnings in 1.07s.
Authentication/token, site retrieval, device inventory, device count and release endpoint response passed. Exact release value not yet validated. TLS warning expected for sandbox only.

## Release policy
Always-On is read-only. Do not submit configuration mutations. Develop configuration roles using documented Cisco modules first, test schemas and mocked behavior, and keep live write validation deferred. Do not label mocked results as live passes. No production deployment or merge of unverified writable functionality.

## Deferred on-demand lab backlog
- Create/read/update/delete and cleanup for each writable resource.
- Repeat deployment and independently verify idempotency.
- Drift remediation, failure recovery and rollback.
- Administrative settings, PKI, AAA, backups, licensing and full greenfield deployment.
- Device provisioning, SWIM, PnP, wireless and SDA changes.
- Verify exact release, native collection and SDK compatibility before write tests.

## Next
Extract exact release from documented API; pin compatible native collection and SDK; test native read modules. Branch protection remains outstanding.
