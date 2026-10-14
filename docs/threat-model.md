# Threat model and deployment limits

Created by Jason Stys. Assets: app credentials, manager bootstrap/unseal/root token, TLS keys, database password verifier, raw audit/log data and correctness of lifecycle evidence. Authorized scope: synthetic fixture data and owned ephemeral processes/container/network on a dedicated Linux CI runner.

## Boundaries and controls

- Token exfiltration through URLs/proxies/redirects: fixed numeric loopback HTTPS, standard CA/hostname verification, bounded responses, no redirects or implicit environment proxies. Wrong-trust negative is specific TLS failure.
- Stale/expired/revoked credentials: conservative monotonic lifetime, post-retry guard, transient-only fallback, cache invalidation on ACL/TLS/malformed data, exact-generation invalidation. Token revocation cascades leases and is actually tested.
- Privilege escalation: fixed read-only SQL grants and default-deny HCL; actual WRITE and config/other-role/revoke negatives with healthy controls. No user SQL, external URLs or arbitrary uploaded programs are executed.
- Fixture escape/destruction: Linux/ack guard before any Docker call, fixed local socket, exact ownership labels/names before removal, owned internal bridge with no published DB port, checked private in-subnet IP/verify-full TLS, non-root/capability-dropped/read-only container, tmpfs/memory/CPU/PID bounds and deadlines. The manager API remains loopback-only. No host mounts, privileged container, host network, broad prune, shared-resource delete or local Docker repair.
- Dependency tampering: immutable action commits/base image digest, exact hash-locked package graphs, official hash-verified binaries, actual built-image/OpenBao module vulnerability checks, Gitleaks history, workflow/shell lint and security-extended CodeQL. No ignored advisories or weakened gates.
- Report injection/leakage: exact allowlisted schema, escaped inert HTML, CSP default-src none, no scripts/forms/remote assets. Full private logs and generated credential files remain ignored; workflow storage/upload is absent.

## Explicit non-goals / residual risk

This is not hardened public hosting, a multitenant secrets product, production identity federation, MFA, HA, auto-unseal, sealed storage recovery, remote database/provider support, connection-pool draining, a zero-loss/zero-downtime SLA or a compliance attestation. OpenBao's one-share/in-memory bootstrap and `disable_mlock` are lab conveniences. A loopback/native OpenBao process is not a container sandbox; it runs as the trusted runner account and has a workflow-level timeout, not a per-process memory cap. The ephemeral SQL administrator and Docker daemon are trusted operators. Root/host administrators and code with access to the same process can read memory/private working files. Python cannot promise immutable-string zeroization.

Changing a password/VALID UNTIL is not evidence that an existing connection was killed. The sample closes each SQL connection; production needs a real pool lifecycle and explicit session termination/privilege handling where appropriate. TLS trust is generated and self-signed for the fixture, not public PKI. Permission modes are Unix defense in depth, not Windows ACL encryption. Point-in-time scans cannot prove absence of future vulnerabilities or replace an independent audit. Before production adaptation, revisit each of these gaps instead of deploying this fixture unchanged.
