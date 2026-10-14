# Reviewed upstream security rebuild

Created by Jason Stys, 2026-10-14. The original official OpenBao2.7.1 binary is a historical reference only, not the accepted runtime. Its verified release archive digest remains recorded in `tools.lock.json`. Correct post-build Trivy scanning found four HIGH findings:

| Finding | Component in original binary | Published fixed version |
| --- | --- | --- |
| CVE-2026-78669 | golang.org/x/net0.58.0 | 0.60.0 |
| CVE-2026-78667 | Go stdlib1.27.1 | 1.27.2 (or1.26.9) |
| CVE-2026-78669 | Go stdlib1.27.1 | 1.27.2 (or1.26.9) |
| CVE-2026-97031 | Go stdlib1.27.1 | 1.27.2 (or1.26.9) |

The first source-filesystem scan did not inspect Go binaries; its explicit inventory requirement correctly rejected an empty result. The gate now uses post-build `rootfs` mode, requires actual Go inventory, rejects nonzero scanner status and rejects any HIGH/CRITICAL finding. No advisory, package or severity is excluded. Native regressions reject empty/advisory-bearing reports even if a mocked scanner returns zero.

The builder checks the exact upstream v2.7.1 commit `a5db72cef75c24b920ade02065b18dd8eb666bac`, requires Go1.27.2, mechanically applies `go get golang.org/x/net@v0.60.0` in an ignored disposable upstream checkout, verifies the reviewed module checksum through Go's standard checksum database, runs `go mod verify`, and builds with trimmed paths, VCS information, CGO disabled and two concurrent compiler processes. No authored contribution or issue is submitted upstream. No custom crypto or manager implementation replaces OpenBao.

This produces a **lab-maintained rebuild**, not an upstream-signed release or claimed reproducible byte-identical binary. The module tool may update related transitive modules through its normal version selection; the full resolved module metadata and compiled actual dependency graph are checked. The build receipt records exact lab/upstream SHA, toolchain, module/version/checksum, module metadata hashes and binary hash. The vulnerability receipt must bind to that same binary/current lab SHA before the drill can run. The actual rebuilt Go graph and actual derived PostgreSQL image must both pass the unchanged HIGH/CRITICAL gate, followed by real application behavior.

OpenBao remains third-party MPL-2.0 software; its copyright/license/source are preserved in the temporary checkout and linked upstream. Only this lab's authored code is MIT. No rebuilt binary is redistributed as an official release. Future vendor/toolchain advisories can still fail the gate; a point-in-time zero does not prove absence of defects or scan the whole OpenBao application source.

Sources: [Go release history](https://go.dev/doc/devel/release#go1.27.2), [x/net0.60.0](https://pkg.go.dev/golang.org/x/net@v0.60.0), [upstream source](https://github.com/openbao/openbao/tree/a5db72cef75c24b920ade02065b18dd8eb666bac), [Trivy Go coverage](https://www.trivy.dev/docs/v0.69/guide/coverage/language/golang/).
