# Primary-source research and implementation choices

Reviewed by Jason Stys on 2026-10-14. Official OpenBao release API identified v2.7.1 (2026-10-01), and official PyPI metadata identified Psycopg3.3.6; exact digests are locked. Sources inform design, not instructions or permission to mutate user systems.

- [OpenBao lease semantics](https://openbao.org/docs/concepts/lease/): inspect actual returned duration/renewability and respect expiry; operator renewal is not an assumed fixed extension.
- [Database API](https://openbao.org/docs/api/secret/databases/): dynamic credentials, custom creation/revocation and separate manager-password rotation. A dedicated manager is preferable to configuring the app with the DB administrator.
- [PostgreSQL plugin](https://openbao.org/docs/secrets/databases/postgresql/): supported dynamic roles and SCRAM connection settings; fixed reviewed SQL grants shape the example.
- [OpenBao policies](https://openbao.org/docs/concepts/policies/): default-deny paths, no wildcard config/control privileges for the application.
- [TCP TLS listener](https://openbao.org/docs/configuration/listener/tcp/): configure real TLS/trust and bounded requests, not skip-verification.
- [Initialization](https://openbao.org/docs/api/system/init/) and [unseal API](https://openbao.org/docs/api/system/unseal/): normal server bootstrap. This one-share in-memory fixture is not a production seal/recovery procedure.
- [Token API](https://openbao.org/docs/api/auth/token/): scoped finite-lived application token, explicit parent-token revocation exercise.
- [PostgreSQL password authentication](https://www.postgresql.org/docs/current/auth-password.html) and [CREATE ROLE](https://www.postgresql.org/docs/18/sql-createrole.html): SCRAM, expiry and privilege choices. Existing sessions require separate handling; successful negative authentication is not proof of session termination.
- [Official OpenBao releases](https://github.com/openbao/openbao/releases/tag/v2.7.1) and [Psycopg](https://www.psycopg.org/psycopg3/docs/): reviewed upstream binaries and native libpq driver; runtime core remains standard-library Python.
- [GitHub artifact removal](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/remove-workflow-artifacts) and [Actions billing](https://docs.github.com/en/billing/concepts/product-billing/github-actions): newest-run preservation is separate from storage billing; jobs/log summaries need not use artifact uploads.

Inference/design choice: a fixed loopback adapter plus separate ephemeral Linux integration narrows this lab's accidental-target/exfiltration surface. That is not a claim that these sources certify the implementation or make it production-ready. Self-documenting names/types explain intent; comments/docstrings explain safety assumptions, and mechanically maintained line maps provide exact navigation. Big-O analysis is structural, with independently scoped timing reports.
