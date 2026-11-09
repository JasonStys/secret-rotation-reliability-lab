# Reviewed upstream security rebuild

Created by Jason Stys, 2026-10-14. The original official OpenBao2.7.1 binary is a historical reference only, not the accepted runtime. Its verified release archive digest remains recorded in `tools.lock.json`. Correct post-build Trivy scanning found four HIGH findings:

| Finding | Component in original binary | Published fixed version |
| --- | --- | --- |
| CVE-2026-78669 | golang.org/x/net0.58.0 | 0.60.0 |
| CVE-2026-78667 | Go stdlib1.27.1 | 1.27.2 (or1.26.9) |
| CVE-2026-78669 | Go stdlib1.27.1 | 1.27.2 (or1.26.9) |
| CVE-2026-97031 | Go stdlib1.27.1 | 1.27.2 (or1.26.9) |

The first source-filesystem scan did not inspect Go binaries; its explicit inventory requirement correctly rejected an empty result. The gate now uses post-build `rootfs` mode, requires actual Go inventory, rejects nonzero scanner status and rejects any HIGH/CRITICAL finding. No advisory, package or severity is excluded. Native regressions reject empty/advisory-bearing reports even if a mocked scanner returns zero.

On 2026-10-22, the unchanged live binary scanner detected the newly published
HIGH finding CVE-2026-111943 in Go1.27.2. The accepted compiler pin is now
Go1.27.3, which includes the upstream crypto/x509 certificate-trust correction.
The original scan record is retained as point-in-time history, not current proof.
The fresh actual-binary scan and full lifecycle drill must pass on this revision;
no scanner finding is excluded or severity gate weakened.

The builder checks the exact upstream v2.7.1 commit `a5db72cef75c24b920ade02065b18dd8eb666bac`, requires Go1.27.3, mechanically applies `go get golang.org/x/net@v0.60.0` in an ignored disposable upstream checkout, verifies the reviewed module checksum through Go's standard checksum database, runs `go mod verify`, and builds with trimmed paths, VCS information, CGO disabled and two concurrent compiler processes. No authored contribution or issue is submitted upstream. No custom crypto or manager implementation replaces OpenBao.

This produces a **lab-maintained rebuild**, not an upstream-signed release or claimed reproducible byte-identical binary. The module tool may update related transitive modules through its normal version selection; the full resolved module metadata and compiled actual dependency graph are checked. The build receipt records exact lab/upstream SHA, toolchain, module/version/checksum, module metadata hashes and binary hash. The vulnerability receipt must bind to that same binary/current lab SHA before the drill can run. The actual rebuilt Go graph and actual derived PostgreSQL image must both pass the unchanged HIGH/CRITICAL gate, followed by real application behavior.

OpenBao remains third-party MPL-2.0 software; its copyright/license/source are preserved in the temporary checkout and linked upstream. Only this lab's authored code is MIT. No rebuilt binary is redistributed as an official release. Future vendor/toolchain advisories can still fail the gate; a point-in-time zero does not prove absence of defects or scan the whole OpenBao application source.

Sources: [Go release history](https://go.dev/doc/devel/release#go1.27.3), [CVE-2026-111943](https://www.cve.org/CVERecord?id=CVE-2026-111943), [x/net0.60.0](https://pkg.go.dev/golang.org/x/net@v0.60.0), [upstream source](https://github.com/openbao/openbao/tree/a5db72cef75c24b920ade02065b18dd8eb666bac), [Trivy Go coverage](https://www.trivy.dev/docs/v0.69/guide/coverage/language/golang/).

## November 9 maintained dependency update

The unchanged actual-binary gate found CVE-2026-116587 in jose/v3.0.5 (no patched v3), jose/v4.1.4 (fixed4.1.6), and x/net0.60.0 (fixed0.62.0). This is a real dependency failure. The new build starts from official OpenBao2.7.2 commit `9e0a0d3c3504a0a00b45e61355afac5e35c78379` and uses the maintained HashiCorp CAP0.15.0 migration from jose/v3 to jose/v4. No custom cryptography or scanner exclusion is introduced.

Exact CAP0.15.0, jose/v4.1.8 and x/net0.62.0 module archives **and go.mod checksums** are verified against reviewed standard Go checksum-database entries. Standard `go get`/`go mod tidy` selects the graph. Upstream JWT and Kubernetes authentication tests run in short mode, followed by the actual binary build. The compiled build metadata must contain each exact maintained module and checksum, contain no jose/v3 and contain no replacement module. The independent Trivy inventory/advisory gate and real TLS/PostgreSQL lifecycle drill remain mandatory; the unit fixtures do not prove native build compatibility.

The image used by the lifecycle drill also receives exact Alpine3.24 security package updates: brotli-libs1.2.1-r0, libcurl8.23.0-r0, musl/musl-utils1.2.6-r3, zlib1.4-r0. These are available versions verified from the official x86_64 APKINDEX; zlib's minimum fixed1.3.2-r1 is no longer in the current index. The immutable official base, non-root runtime, actual derived-image scan and source-bound receipt are retained. Bounded sanitized public package diagnostics expose build failures without dumping credentials or arbitrary build transcripts.

Sources: [OpenBao2.7.2](https://github.com/openbao/openbao/releases/tag/v2.7.2), [CAP0.15.0 migration](https://github.com/hashicorp/cap/releases/tag/v0.15.0), [jose advisory](https://github.com/go-jose/go-jose/security/advisories/GHSA-mgcc-cww5-fp2q), [jose4.1.8](https://github.com/go-jose/go-jose/releases/tag/v4.1.8), [x/net0.62.0](https://pkg.go.dev/golang.org/x/net@v0.62.0), [Alpine security database](https://secdb.alpinelinux.org/v3.24/main.json), [official package index](https://dl-cdn.alpinelinux.org/alpine/v3.24/main/x86_64/APKINDEX.tar.gz).
