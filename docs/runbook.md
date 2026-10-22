# Runbook: safe local demonstration and owned live exercise

Author/contact: Jason Stys, [GitHub](https://github.com/JasonStys). Start with README's offline commands; `python -m rotation --help` explains demo/report usage. No user account or external API key is needed.

## Disposable Linux live run

Do not run on this PC or a shared/production host. Required: dedicated Linux x86_64 Docker daemon at `/var/run/docker.sock`, Git, OpenSSL, Python3.14, Go1.27.3, network for reviewed dependency/source/image/scanner downloads. The fixture later uses only loopback/internal-network traffic. See [upstream security rebuild](upstream-security.md); this is not an official OpenBao release binary.

```bash
python -m pip install --require-hashes -r requirements-integration.lock
python scripts/build_bao.py
python scripts/scanners.py trivy
python scripts/bao_check.py
python scripts/image_check.py
python -m scripts.live_drill --output out/live-example --ack-disposable-docker
python -m rotation report out/live-example/report/report.json
```

The image receipt must match the current Git SHA. Run only reviewed committed source; regenerate maps/file guide before committing. The drill creates one randomly named internal network and one non-root database container, with a native owned OpenBao child process and new private output folder. Generated TLS trust is transferred as a precisely owned two-file tar, never an arbitrary artifact extraction. Neither secrets nor their values occur in process argv. A private database env file is used for initial fixture setup and Docker's trusted administrator can inspect it. Real driver connections use password kwargs, SCRAM and verify-full TLS.

The drill stops/resumes only its actual manager process handle for outage injection. It invalidates old credentials deliberately in its disposable database. Normal/failure cleanup checks exact name+owner label before removal, verifies absence, and terminates its owned process. It does **not** prune Docker, delete arbitrary output, restore production state or change any Windows Docker configuration. `out/.../private/` remains ignored and should not be shared. Do not upload raw logs to troubleshoot.

## Failure handling

| Symptom | Safe next action |
| --- | --- |
| Local sandbox temp-directory access error | Set TEMP/TMP to a new workspace-local temporary folder for that command, or use a new `--basetemp` under `out/`. Do not weaken host protections. |
| Wrong TLS trust | Confirm the generated CA/path/loopback endpoint belongs to this exact run. Never use a skip-verify flag. |
| SQLSTATE42501 | Expected only in the deliberate write negative; otherwise inspect the fixed role/grant configuration privately. |
| Denied/malformed provider response | Fail closed; check policy/schema. Do not add wildcard ACL or silently reuse the cache. |
| Manager unavailable | Valid cache can last only until its conservative guard; then refuse work. Recovery must issue a new identity. |
| Existing output | Choose a new directory; reports never overwrite data. |
| Image receipt/source mismatch or security advisory | Rebuild/review the exact source/dependencies. Do not skip the scan. |
| Owned cleanup failure | Stop. Identify the exact random owner label/name; inspect it before manual scoped recovery. Never use `docker system prune` or broad deletion. |

Production incident adaptation requires authenticated operational identity, emergency exact-lease/token revocation, consumer cache/pool invalidation, existing-session control, audit retention, restored fresh-credential positive controls and an approved rollback plan. Those are a runbook design, not authorization for this lab to act on a real service.

## Storage

CI intentionally creates zero Actions artifacts/caches. Case aggregates are in job text, selected safe results in `docs/reports/`. Raw credentials/audit data are never uploaded. Check current account storage before Actions work and ask for fresh cleanup approval. Deletion of old workflow runs is irreversible in the ordinary GitHub UI; archive/verify all obtainable results first and preserve newest workflow/active runs. Prior approval is not recurring authorization.
