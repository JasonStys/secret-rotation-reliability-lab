# Test strategy and reproducible validation

Created by Jason Stys. Core statement/branch coverage gate: 95%, no excluded authored core files. Docker/orchestration helpers are explicitly outside that denominator; their destructive guards receive portable tests and their full behavior receives the independent real service drill.

## Layers and oracles

- Unit/boundary: type/bool/nonfinite/size/namespace settings, clock rollback, strict expiry, capped retry, current-generation invalidation, detached statistics and complete evidence schema.
- Property/fuzz: Hypothesis explores finite TTL/elapsed boundaries; malformed/duplicate/nonfinite/UTF8/oversize API JSON cases fuzz the transport boundary without contacting external systems. This is bounded property/adversarial testing, not a claim of every fuzzing technique.
- Concurrency: 32 actual threaded consumers share one issuance. Deterministic clock/sleeper test retry time and old-generation races without modifying the system clock.
- Mock transport contract: redirects/ACL/TLS/timeout distinctions, response body suppression, verifying CA context, fixed endpoint/path and byte/time caps.
- Native integration: actual CLI/files/inert rendering plus ownership/host/tar guards on Ubuntu3.12/3.14, Windows3.14 and Intel macOS3.14.
- Live integration: 15 cases against normal TLS OpenBao and non-root real PostgreSQL. Exact SQL totals, specific write/ACL/TLS negatives, role-removal queries, healthy controls and HMAC audit fields prevent generic-error false positives. No mocks are substituted for this lane.
- Security: complete package graph advisory audits, actual source-bound database image and installed OpenBao Go-module inventory, full-history Gitleaks, actionlint/ShellCheck and security-extended CodeQL. Vulnerable dependencies are corrected, not ignored.

```bash
python -m ruff check rotation scripts tests
python -m ruff format --check rotation scripts tests
python -m mypy
python -m pytest --cov --cov-report=term-missing
python scripts/code_map.py --check
python scripts/file_guide.py --check
python scripts/validate_repo.py
python -m scripts.benchmark
```

`bash scripts/validate.sh` runs these fail-fast. All workflow actions are full-commit pinned, checkouts persist no credentials, default permission is contents:read, and only CodeQL has scoped security-events:write. PRs never get pull_request_target or deployment credentials. No Actions artifacts/caches or code-scanning database archive are uploaded. The hosted Linux lane remains required because local Docker was intentionally left unchanged.

## Evidence acceptance

Native reports/benchmarks label their actual source, platform and scope. Simulation uses virtual elapsed time and is explicitly named. Live aggregates time actual independent assertions and bind to executable-source SHA. Never claim a green result until every required current-main job is completed/success and open CodeQL alerts are checked. Historical failures are disclosed in the validation report; rerunning a known-broken old SHA is not a fix. Immutable runtime-source results are distinct from later report-only commits, which must pass the same full checks.

Benchmark: warmed cached decisions in five repeated batches, one-issuance correctness oracle and peak Python allocation. It does not estimate Big-O from timings, include TLS/DB latencies, prove production throughput or show an unmeasured speedup. See [validation](reports/validation.md) for measured results and limitations.
