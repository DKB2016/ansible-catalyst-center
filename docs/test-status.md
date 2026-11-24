# Initial integration candidate

No live tests verified yet. Shared sandbox is read-only for this candidate. Authentication and site retrieval are the initial gates. Native Ansible execution, version discovery, write lifecycle and idempotency remain untested. Do not merge to main until applicable gates pass. TLS verification is disabled only for the two named public sandbox endpoints. Production must verify TLS. Credentials must be GitHub Actions secrets, never repository content.
