<!-- File: docs/reports/portfolio-sync-2026-10-22.md; Purpose: certificate-bundle security repair and evidence by Jason Stys. -->

# Certificate bundle maintenance — 2026-10-22

By Jason Stys. The live audit identified PYSEC-2026-4320 in certifi 2026.7.22. This branch advances that resolved transitive package to the reported fixed release 2026.10.19 and replaces both distribution SHA-256 pins with the reviewed package hashes. No audit exclusion, ignored advisory, test weakening, runtime data or account change is included.

Native validation also detected CVE-2026-111943 in the actual rebuilt OpenBao
binary's Go1.27.2 standard library. The build specification and CI compiler now
require the upstream fixed Go1.27.3. The same actual-inventory HIGH/CRITICAL
scanner and complete TLS/database lifecycle acceptance remain mandatory. See
[the upstream security rebuild](../upstream-security.md) for source references
and the distinction between this lab-maintained build and an official release.

The complete existing native CI and code-scanning workflows validate the exact integration head before a normal merge; main is checked again afterward. [Actions](https://github.com/JasonStys/secret-rotation-reliability-lab/actions) provides revision-specific results. The private full portfolio audit and archived old run evidence remain on the owner's PC, not in this public repository. Existing historical/audit references are preserved.
