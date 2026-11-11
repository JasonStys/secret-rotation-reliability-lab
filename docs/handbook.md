# Secret Rotation Reliability Lab handbook

By Jason Stys.

Rehearse credential rotation, overlap and recovery with explicit lifecycle evidence and genuine isolated service tests. Reports do not expose secret values or authorize changes to live credentials.

Bind consumer acknowledgements to secret generations and inspect drain/expiry/replay queues; patch the actual OpenBao build and fail closed for its unused incompatible Okta integration.

Makes rotation completion evidence explicit and removes known dependency risks without pretending unsupported authentication still works.

## Read the documentation

| Edition | Audience and contents |
| --- | --- |
| [project-guide.docx](reports/project-guide.docx) | User and developer guide: purpose, current usage, design, boundaries and source references. |

The editable Markdown remains the maintenance source. The Word files are readable editions. See [publication identities and review](reports/publications.json) and the [documentation refresh record](reports/documentation-refresh-2026-11-09.md).

## Current usage and help

[README quick start](../README.md) is the entry point. Use the project-specific guides below before changing inputs, operating modes or deployment assumptions.

### Usage and operations

- [runbook](runbook.md)

### Design and contracts

- [architecture](architecture.md)
- [contracts](contracts.md)
- [research](research.md)
- [threat model](threat-model.md)

### Security and validation

- [testing](testing.md)
- [upstream security](upstream-security.md)

## Historical results and reproduction

The reviewed source is [`5a604a11555b38a61c4b7379729ac187ba5e86d2`](https://github.com/JasonStys/secret-rotation-reliability-lab/tree/5a604a11555b38a61c4b7379729ac187ba5e86d2). The observed functional workflow baseline is `5a604a11555b38a61c4b7379729ac187ba5e86d2`; those observations are recorded at `2026-11-10T05:25:40.628667+00:00`. They do not certify an unrun later revision.

- [Detailed recorded validation](reports/handoff-2026-11-09.md)
- [Current Actions](https://github.com/JasonStys/secret-rotation-reliability-lab/actions) records later integration checks separately.
- Preserve dated measurements and follow the existing testing guide to reproduce them; a test-source inventory alone does not establish execution.

## Practical boundaries

- Pool-drain acknowledgements and consumer codes are in-process assertions, not authentication or proof of server acceptance.
- Local overlap is a lease-time calculation, not a zero-downtime guarantee.
- The unused incompatible Okta integration fails closed; this project does not claim working Okta authentication.

## Maintaining these editions

Update the editable usage/design/test documents first. Rebuild and visually review every Word page and workbook tab before replacing an edition; verify the exact binary digests and evidence source in publications.json. Keep account data, logs with secrets, installed-app state and private test stores out of documentation. Source and release assets retain their existing security and licensing boundaries.

## Native offline application

[Practical controls, schemas, privacy, build and lifecycle](native-application.md) · [Dated candidate validation](reports/native-workbench-2026-11-11.md). Earlier Office editions retain their original source baseline.
