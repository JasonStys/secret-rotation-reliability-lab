"""Real TLS OpenBao/PostgreSQL lifecycle on an acknowledged disposable Linux Docker host. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: ROOT — line 231
# variable: LABEL — line 232
# definition: FixtureTransport — line 235
# definition: request — line 238
# parameter: body — line 239
# parameter: method — line 239
# parameter: path — line 239
# parameter: self — line 239
# definition: output_directory — line 280
# parameter: path — line 280
# variable: original — line 282
# variable: parent — line 283
# variable: allowed — line 285
# variable: canonical — line 285
# variable: relative — line 288
# variable: part — line 290
# definition: port — line 296
# variable: connection — line 298
# definition: configuration — line 303
# parameter: audit_path — line 303
# parameter: ca — line 303
# parameter: endpoint — line 303
# parameter: key — line 303
# definition: owned — line 320
# parameter: expected_name — line 321
# parameter: metadata — line 321
# parameter: network — line 321
# parameter: owner — line 321
# variable: name — line 324
# variable: labels — line 325
# definition: Docker — line 338
# definition: __init__ — line 341
# parameter: acknowledgment — line 341
# parameter: self — line 341
# attribute: owner — line 347
# attribute: name — line 348
# attribute: environment — line 349
# variable: key — line 351
# variable: value — line 351
# attribute: argv — line 354
# attribute: resources — line 355
# definition: call — line 357
# parameter: args — line 358
# parameter: data — line 358
# parameter: self — line 358
# parameter: timeout — line 358
# variable: result — line 361
# variable: stderr — line 370
# variable: flags — line 371
# variable: label — line 373
# variable: phrase — line 373
# definition: inspect — line 395
# parameter: kind — line 395
# parameter: name — line 395
# parameter: self — line 395
# variable: raw — line 399
# variable: values — line 402
# definition: cleanup — line 408
# parameter: self — line 408
# variable: kind — line 410
# variable: name — line 410
# variable: remaining — line 413
# definition: certificate — line 428
# parameter: directory — line 428
# parameter: name — line 428
# variable: cert — line 430
# variable: key — line 430
# variable: result — line 431
# definition: tls_archive — line 460
# parameter: cert — line 460
# parameter: gid — line 460
# parameter: key — line 460
# parameter: uid — line 460
# variable: output — line 462
# variable: archive — line 463
# variable: mode — line 464
# variable: name — line 464
# variable: path — line 464
# variable: data — line 468
# variable: entry — line 469
# attribute: gid — line 470
# attribute: mode — line 470
# attribute: size — line 470
# attribute: uid — line 470
# definition: wait — line 475
# parameter: operation — line 475
# parameter: seconds — line 475
# variable: deadline — line 477
# definition: drill — line 485
# parameter: acknowledgment — line 485
# parameter: output — line 485
# variable: docker — line 487
# variable: sha — line 491
# variable: image — line 494
# variable: bao_scan — line 497
# variable: bao_build — line 498
# variable: binary_hash — line 499
# variable: output — line 513
# variable: private — line 514
# variable: manager — line 517
# variable: manager_log — line 518
# variable: cases — line 519
# variable: sensitive — line 520
# variable: broker — line 521
# variable: current_case — line 522
# definition: case — line 524
# parameter: name — line 524
# parameter: operation — line 524
# variable: current_case — line 527
# variable: start — line 528
# variable: result — line 530
# variable: ca — line 539
# variable: key — line 539
# variable: db_ca — line 540
# variable: db_key — line 540
# variable: endpoint — line 541
# variable: config — line 542
# variable: manager_log — line 547
# variable: manager — line 548
# variable: anonymous — line 554
# definition: ready — line 556
# variable: initialized — line 564
# variable: root_token — line 567
# variable: unseal_key — line 567
# variable: root — line 573
# variable: audit_reply — line 574
# variable: audit_data — line 575
# definition: tls_proof — line 597
# variable: wrong — line 599
# variable: current_case — line 608
# variable: db_name — line 609
# variable: network_name — line 609
# variable: actor_password — line 621
# variable: admin_password — line 621
# variable: env_file — line 626
# variable: identity — line 671
# variable: metadata — line 679
# variable: binding — line 680
# variable: db_port — line 685
# definition: connect — line 687
# parameter: password — line 687
# parameter: username — line 687
# definition: db_ready — line 701
# variable: connection — line 708
# definition: bootstrap — line 715
# variable: connection — line 717
# variable: auth — line 763
# variable: app_token — line 768
# variable: app — line 770
# variable: provider — line 771
# variable: broker — line 772
# definition: acl — line 774
# variable: client — line 776
# variable: method — line 776
# variable: path — line 776
# variable: payload — line 776
# variable: first — line 790
# definition: query — line 793
# parameter: lease — line 793
# variable: connection — line 795
# definition: readonly — line 800
# variable: connection — line 803
# definition: renewal — line 813
# variable: reply — line 815
# variable: second — line 824
# definition: overlap — line 827
# definition: rejects — line 837
# parameter: lease — line 837
# variable: connection — line 847
# definition: revocation — line 854
# variable: short — line 880
# definition: expiry — line 883
# definition: absent — line 888
# variable: connection — line 890
# definition: root_rotation — line 901
# variable: connection — line 903
# variable: original — line 904
# variable: connection — line 912
# variable: replacement — line 920
# variable: fresh — line 925
# definition: outage_grace — line 931
# definition: outage_expiry — line 938
# definition: recovery — line 951
# variable: recovered — line 953
# definition: identity_revocation — line 960
# variable: current — line 962
# definition: redaction — line 974
# variable: audit_path — line 977
# variable: log — line 979
# variable: value — line 980
# variable: events — line 981
# variable: line — line 981
# variable: responses — line 982
# variable: event — line 984
# variable: event — line 992
# variable: value — line 996
# variable: manager_log — line 1003
# variable: manager — line 1004
# variable: report — line 1006
# definition: main — line 1036
# variable: parser — line 1038
# variable: args — line 1041
# END CODE MAP

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import platform
import re
import secrets
import signal
import socket
import subprocess
import tarfile
import time
from collections.abc import Callable
from pathlib import Path
from urllib.parse import urlencode

from rotation.bao import BaoProvider, Transport
from rotation.broker import Broker
from rotation.contracts import Lease, Policy, ProviderError, Unavailable
from rotation.evidence import write_report

ROOT = Path(__file__).resolve().parents[1]
LABEL = "rotation.lab.owner"


class FixtureTransport(Transport):
    """Fixture-only safe tracing; fixed paths never contain user identities or lease IDs."""

    def request(
        self, method: str, path: str, body: dict[str, object] | None = None
    ) -> dict[str, object]:
        """Trace reviewed operation names/error categories only; no payload, token or raw response messages."""
        if path not in {
            "sys/init",
            "sys/unseal",
            "sys/audit/file",
            "sys/audit",
            "sys/audit/unapproved",
            "sys/mounts/database",
            "database/config/lab",
            "database/roles/reader",
            "sys/policies/acl/reader",
            "auth/token/create",
            "database/creds/reader",
            "database/creds/other",
            "sys/leases/revoke",
            "sys/leases/renew",
            "database/rotate-root/lab",
            "auth/token/revoke",
        }:
            raise ValueError("unknown fixture operation")
        print("FIXTURE_STEP " + method + " " + path, flush=True)
        try:
            return super().request(method, path, body)
        except ProviderError as error:
            print("FIXTURE_API_FAILURE " + path + " " + error.category, flush=True)
            print(
                "FIXTURE_RESPONSE_FACTS "
                + json.dumps(
                    {
                        "status": self.response_status,
                        "stage": self.response_stage,
                        "flags": self.response_flags,
                    }
                ),
                flush=True,
            )
            raise


def output_directory(path: Path) -> Path:
    """Canonicalize a new out/ child without symlinks, traversal, overly deep paths or unsafe filename components."""
    original = path.absolute()
    if any(parent.is_symlink() for parent in [original, *original.parents]):
        raise ValueError("symlink output refused")
    canonical, allowed = original.resolve(), (ROOT / "out").resolve()
    if canonical == allowed or not canonical.is_relative_to(allowed):
        raise ValueError("output must be a new repository out/ child")
    relative = canonical.relative_to(allowed)
    if len(relative.parts) > 3 or any(
        not re.fullmatch(r"[A-Za-z0-9_.-]{1,64}", part) for part in relative.parts
    ):
        raise ValueError("bounded safe output components required")
    return canonical


def port() -> int:
    """Allocate a concrete loopback port; readiness verifies the spawned service rather than trusting allocation alone."""
    with socket.socket() as connection:
        connection.bind(("127.0.0.1", 0))
        return int(connection.getsockname()[1])


def configuration(endpoint: str, ca: Path, key: Path, audit_path: Path) -> str:
    """Generate quoted TLS/declarative HMAC audit config without allowing unsafe API audit creation."""
    return (
        'storage "inmem" {}\ndisable_mlock = true\nui = false\napi_addr = '
        + json.dumps(endpoint)
        + '\nlistener "tcp" {\naddress = '
        + json.dumps("127.0.0.1:" + endpoint.rsplit(":", 1)[1])
        + "\ntls_cert_file = "
        + json.dumps(str(ca))
        + "\ntls_key_file = "
        + json.dumps(str(key))
        + '\nmax_request_size = 65536\n}\naudit "file" "file" {\noptions {\nfile_path = '
        + json.dumps(str(audit_path))
        + '\nlog_raw = "false"\n}\n}\n'
    )


def owned(
    metadata: dict, expected_name: str, owner: str, *, network: bool = False
) -> None:
    """Require exact generated name/label before deletion; unrelated resources cannot be removed."""
    name = metadata.get("Name", "").lstrip("/")
    labels = (
        metadata.get("Labels", {})
        if network
        else metadata.get("Config", {}).get("Labels", {})
    )
    if (
        not re.fullmatch(r"sr-[a-f0-9]{20}(?:-db|-net)?", expected_name)
        or name != expected_name
        or labels.get(LABEL) != owner
    ):
        raise ValueError("owned-resource identity mismatch")


class Docker:
    """Only the local Linux socket, random owned resources and private stdin/env-file inputs are allowed."""

    def __init__(self, acknowledgment: bool) -> None:
        """Refuse all Docker work on this Windows PC or without explicit disposable-host acknowledgement."""
        if not acknowledgment or platform.system() != "Linux":
            raise ValueError(
                "acknowledged disposable Linux host required; local Docker stays unchanged"
            )
        self.owner = secrets.token_hex(10)
        self.name = "sr-" + self.owner
        self.environment = {
            key: value
            for key, value in os.environ.items()
            if key not in {"DOCKER_CONTEXT", "DOCKER_HOST"}
        }
        self.argv = ["docker", "--host", "unix:///var/run/docker.sock"]
        self.resources: list[tuple[str, str]] = []

    def call(
        self, args: list[str], data: bytes | None = None, *, timeout: int = 60
    ) -> bytes:
        """Execute fixed argv without a shell; do not echo Docker output (it can include synthetic credentials)."""
        result = subprocess.run(
            [*self.argv, *args],
            input=data,
            capture_output=True,
            timeout=timeout,
            env=self.environment,
            check=False,
        )
        if result.returncode:
            stderr = result.stderr.lower()
            flags = [
                label
                for phrase, label in [
                    (b"permission", "permission"),
                    (b"archive", "archive"),
                    (b"mount", "mount"),
                    (b"read-only", "read-only"),
                    (b"invalid", "invalid"),
                    (b"not found", "not-found"),
                    (b"copy", "copy"),
                    (b"network", "network"),
                ]
                if phrase in stderr
            ]
            print(
                "OWNED_DOCKER_FAILURE "
                + json.dumps(
                    {"operation": args[0], "exit": result.returncode, "flags": flags}
                ),
                flush=True,
            )
            raise RuntimeError("owned Docker operation failed")
        return result.stdout

    def inspect(self, kind: str, name: str) -> dict:
        """Read exact ownership metadata, never an unbounded enumeration of user containers."""
        if kind not in {"container", "network"}:
            raise ValueError("invalid resource kind")
        raw = self.call([kind, "inspect", name])
        if len(raw) > 65536:
            raise ValueError("inspection exceeds cap")
        values = json.loads(raw)
        if not isinstance(values, list) or len(values) != 1:
            raise ValueError("resource identity missing")
        owned(values[0], name, self.owner, network=kind == "network")
        return values[0]

    def cleanup(self) -> None:
        """Remove only registered, freshly identity-checked resources; verify absence by exact owned label."""
        for kind, name in reversed(self.resources):
            self.inspect(kind, name)
            self.call([kind, "rm", *(["--force"] if kind == "container" else []), name])
            remaining = self.call(
                [
                    kind,
                    "ls",
                    "--filter",
                    f"label={LABEL}={self.owner}",
                    "--format",
                    "{{.Names}}" if kind == "container" else "{{.Name}}",
                ]
            )
            if name in remaining.decode().splitlines():
                raise RuntimeError("owned cleanup verification failed")
        self.resources.clear()


def certificate(directory: Path, name: str) -> tuple[Path, Path]:
    """Generate disposable self-signed TLS trust using the official runner's OpenSSL; key material never enters argv/logs."""
    key, cert = directory / (name + ".key"), directory / (name + ".crt")
    result = subprocess.run(
        [
            "openssl",
            "req",
            "-x509",
            "-newkey",
            "rsa:2048",
            "-nodes",
            "-days",
            "1",
            "-subj",
            "/CN=fictional-rotation-lab",
            "-addext",
            "subjectAltName=IP:127.0.0.1",
            "-keyout",
            str(key),
            "-out",
            str(cert),
        ],
        capture_output=True,
        timeout=15,
        check=False,
    )
    if result.returncode:
        raise RuntimeError("TLS fixture generation failed")
    key.chmod(0o600)
    return key, cert


def tls_archive(key: Path, cert: Path, uid: int, gid: int) -> bytes:
    """Build an in-memory two-file tar with exact generated names/ownership; never extract user-supplied archives."""
    output = io.BytesIO()
    with tarfile.open(fileobj=output, mode="w") as archive:
        for path, name, mode in [
            (key, "server.key", 0o600),
            (cert, "server.crt", 0o644),
        ]:
            data = path.read_bytes()
            entry = tarfile.TarInfo(name)
            entry.size, entry.uid, entry.gid, entry.mode = len(data), uid, gid, mode
            archive.addfile(entry, io.BytesIO(data))
    return output.getvalue()


def wait(operation: Callable[[], bool], seconds: float = 30) -> None:
    """Bounded eventual-state polling; negative assertions elsewhere do not accept unrelated failures."""
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if operation():
            return
        time.sleep(0.1)
    raise RuntimeError("bounded readiness deadline exceeded")


def drill(output: Path, acknowledgment: bool) -> dict:
    """Exercise fifteen real lifecycle oracles; only validated safe aggregate data is printed/saved."""
    docker = Docker(acknowledgment)
    import psycopg
    from psycopg import sql

    sha = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, timeout=5
    ).strip()
    image = json.loads(
        (ROOT / ".tools/postgres-image.json").read_text(encoding="utf-8")
    )
    bao_scan = json.loads((ROOT / ".tools/bao-scan.json").read_text(encoding="utf-8"))
    bao_build = json.loads((ROOT / ".tools/bao-build.json").read_text(encoding="utf-8"))
    binary_hash = hashlib.sha256((ROOT / ".tools/bao").read_bytes()).hexdigest()
    if (
        bao_scan["source_sha"] != sha
        or bao_build["source_sha"] != sha
        or bao_scan["binary_sha256"] != binary_hash
        or bao_build["binary_sha256"] != binary_hash
        or bao_scan["high_critical"] != 0
        or bao_scan["go_packages_scanned"] <= 0
    ):
        raise ValueError("current-source scanned/rebuilt manager receipt required")
    if image["source_sha"] != sha or not re.fullmatch(
        r"sha256:[a-f0-9]{64}", image["image_id"]
    ):
        raise ValueError("current-source scanned image receipt required")
    output = output_directory(output)
    private = output / "private"
    output.absolute().mkdir(parents=True, exist_ok=False, mode=0o700)
    private.mkdir(mode=0o700)
    manager: subprocess.Popen | None = None
    manager_log = None
    cases = []
    sensitive: list[str] = []
    broker = None
    current_case = "bootstrap"

    def case(name: str, operation: Callable[[], None]) -> None:
        """Time one independent real assertion and emit allowlisted metrics only, never raw exception content."""
        nonlocal current_case
        current_case = name
        start = time.perf_counter()
        operation()
        result = {
            "name": name,
            "passed": True,
            "duration_ms": round((time.perf_counter() - start) * 1000, 3),
        }
        cases.append(result)
        print("CASE " + json.dumps(result), flush=True)

    try:
        key, ca = certificate(private, "manager")
        db_key, db_ca = certificate(private, "database")
        endpoint = "https://127.0.0.1:" + str(port())
        config = private / "server.hcl"
        config.write_text(
            configuration(endpoint, ca, key, private / "audit.jsonl"),
            encoding="utf-8",
        )
        manager_log = (private / "manager.log").open("wb")
        manager = subprocess.Popen(
            [str(ROOT / ".tools/bao"), "server", "-config=" + str(config)],
            cwd=private,
            stdout=manager_log,
            stderr=subprocess.STDOUT,
        )
        anonymous = FixtureTransport(endpoint, ca)

        def ready() -> bool:
            """Check actual initialization endpoint, not merely a listening port; safe transient failures retry."""
            try:
                return anonymous.request("GET", "sys/init")["initialized"] is False
            except ProviderError:
                return False

        wait(ready)
        initialized = anonymous.request(
            "POST", "sys/init", {"secret_shares": 1, "secret_threshold": 1}
        )
        root_token, unseal_key = initialized["root_token"], initialized["keys"][0]
        sensitive.extend([root_token, unseal_key])
        assert (
            anonymous.request("POST", "sys/unseal", {"key": unseal_key})["sealed"]
            is False
        )
        root = FixtureTransport(endpoint, ca, root_token)
        audit_reply = root.request("GET", "sys/audit")
        audit_data = audit_reply.get("data", audit_reply)
        assert isinstance(audit_data, dict) and audit_data["file/"]["type"] == "file"
        assert audit_data["file/"]["options"]["file_path"] == str(
            private / "audit.jsonl"
        )
        try:
            root.request(
                "POST",
                "sys/audit/unapproved",
                {
                    "type": "file",
                    "options": {"file_path": str(private / "forbidden.jsonl")},
                },
            )
        except ProviderError:
            assert (
                root.response_status == 400
                and "audit-api-disabled" in root.response_flags
            )
        else:
            raise AssertionError("unsafe API audit creation accepted")

        def tls_proof() -> None:
            """A different trusted certificate must specifically fail certificate verification, never just time out."""
            wrong = Transport(endpoint, db_ca)
            try:
                wrong.request("GET", "sys/init")
            except ProviderError as error:
                assert error.category == "tls" and not error.retryable
            else:
                raise AssertionError("wrong TLS trust accepted")

        case("tls", tls_proof)
        current_case = "bootstrap"
        db_name, network_name = docker.name + "-db", docker.name + "-net"
        docker.call(
            [
                "network",
                "create",
                "--internal",
                "--label",
                LABEL + "=" + docker.owner,
                network_name,
            ]
        )
        docker.resources.append(("network", network_name))
        admin_password, actor_password = (
            secrets.token_urlsafe(24),
            secrets.token_urlsafe(24),
        )
        sensitive.extend([admin_password, actor_password])
        env_file = private / "database.env"
        env_file.write_text(
            "POSTGRES_DB=lab\nPOSTGRES_USER=postgres\nPOSTGRES_PASSWORD="
            + admin_password
            + "\nPOSTGRES_HOST_AUTH_METHOD=scram-sha-256\n",
            encoding="utf-8",
        )
        env_file.chmod(0o600)
        docker.call(
            [
                "run",
                "--detach",
                "--name",
                db_name,
                "--label",
                LABEL + "=" + docker.owner,
                "--network",
                network_name,
                "--publish",
                "127.0.0.1::5432",
                "--read-only",
                "--cap-drop",
                "ALL",
                "--security-opt",
                "no-new-privileges",
                "--user",
                "postgres",
                "--memory",
                "256m",
                "--cpus",
                "1",
                "--pids-limit",
                "128",
                "--tmpfs",
                "/var/lib/postgresql:rw,noexec,nosuid,size=134217728,uid=70,gid=70,mode=700",
                "--tmpfs",
                "/var/run/postgresql:rw,noexec,nosuid,size=16777216,uid=70,gid=70,mode=700",
                "--tmpfs",
                "/tmp:rw,noexec,nosuid,size=16777216,uid=70,gid=70,mode=700",
                "--env-file",
                str(env_file),
                image["image_id"],
            ]
        )
        docker.resources.append(("container", db_name))
        identity = docker.call(["exec", db_name, "id", "-u"]).decode().strip()
        assert identity == "70"
        # Docker cp cannot write tmpfs mounts. Transfer only our two generated files
        # through stdin to tar running as the already verified non-root container user.
        docker.call(
            ["exec", "-i", db_name, "tar", "-xpf", "-", "-C", "/tmp"],
            tls_archive(db_key, db_ca, 70, 70),
        )
        metadata = docker.inspect("container", db_name)
        binding = metadata["NetworkSettings"]["Ports"]["5432/tcp"][0]
        assert (
            binding["HostIp"] == "127.0.0.1"
            and docker.inspect("network", network_name)["Internal"] is True
        )
        db_port = int(binding["HostPort"])

        def connect(username: str, password: str):
            """Use real SCRAM and verify-full TLS; passwords are kwargs, never command-line arguments."""
            return psycopg.connect(
                host="127.0.0.1",
                port=db_port,
                dbname="lab",
                user=username,
                password=password,
                sslmode="verify-full",
                sslrootcert=str(db_ca),
                connect_timeout=2,
                autocommit=True,
            )

        def db_ready() -> bool:
            """Do not accept the temporary initdb server; ensure main PostgreSQL PID1 before setup."""
            if b"postgres" not in docker.call(
                ["exec", db_name, "sh", "-c", "tr '\\000' ' ' < /proc/1/cmdline"]
            ):
                return False
            try:
                with connect("postgres", admin_password) as connection:
                    return connection.execute("SELECT 1").fetchone() == (1,)
            except psycopg.OperationalError:
                return False

        wait(db_ready)

        def bootstrap() -> None:
            """Create a non-superuser manager and fictional inventory with explicit grant options."""
            with connect("postgres", admin_password) as connection:
                connection.execute(
                    sql.SQL(
                        "CREATE ROLE bao_manager LOGIN CREATEROLE NOSUPERUSER NOCREATEDB PASSWORD {}"
                    ).format(sql.Literal(actor_password))
                )
                connection.execute((ROOT / "sql/seed.sql").read_text(encoding="utf-8"))
                assert connection.execute(
                    "SELECT rolcreaterole, rolsuper, rolcreatedb FROM pg_roles WHERE rolname='bao_manager'"
                ).fetchone() == (True, False, False)
            root.request("POST", "sys/mounts/database", {"type": "database"})
            root.request(
                "POST",
                "database/config/lab",
                {
                    "plugin_name": "postgresql-database-plugin",
                    "allowed_roles": ["reader"],
                    "connection_url": f"postgresql://{{{{username}}}}:{{{{password}}}}@127.0.0.1:{db_port}/lab?"
                    + urlencode({"sslmode": "verify-full", "sslrootcert": str(db_ca)}),
                    "username": "bao_manager",
                    "password": actor_password,
                    "password_authentication": "scram-sha-256",
                },
            )
            root.request(
                "POST",
                "database/roles/reader",
                {
                    "db_name": "lab",
                    "default_ttl": "20s",
                    "max_ttl": "60s",
                    "creation_statements": [
                        'CREATE ROLE "{{name}}" WITH LOGIN PASSWORD \'{{password}}\' VALID UNTIL \'{{expiration}}\'; GRANT CONNECT ON DATABASE lab TO "{{name}}"; GRANT USAGE ON SCHEMA public TO "{{name}}"; GRANT SELECT ON public.inventory TO "{{name}}";'
                    ],
                    "revocation_statements": [
                        'REVOKE ALL ON public.inventory FROM "{{name}}"; REVOKE ALL ON SCHEMA public FROM "{{name}}"; REVOKE ALL ON DATABASE lab FROM "{{name}}"; DROP ROLE "{{name}}";'
                    ],
                },
            )
            root.request(
                "PUT",
                "sys/policies/acl/reader",
                {"policy": (ROOT / "ops/reader.hcl").read_text(encoding="utf-8")},
            )

        case("bootstrap", bootstrap)
        auth = root.request(
            "POST",
            "auth/token/create",
            {"policies": ["reader"], "no_default_policy": True, "ttl": "5m"},
        )["auth"]
        app_token = auth["client_token"]
        sensitive.append(app_token)
        app = FixtureTransport(endpoint, ca, app_token)
        provider = BaoProvider(app)
        broker = Broker(provider, Policy(attempts=1))

        def acl() -> None:
            """Anonymous/scoped tokens must receive specific 403 denials for unauthorized role/config/revoke paths."""
            for client, method, path, payload in [
                (anonymous, "GET", "database/creds/reader", None),
                (app, "GET", "database/config/lab", None),
                (app, "GET", "database/creds/other", None),
                (app, "POST", "sys/leases/revoke", {"lease_id": "fictional"}),
            ]:
                try:
                    client.request(method, path, payload)
                except ProviderError as error:
                    assert error.category == "denied"
                else:
                    raise AssertionError("least-privilege denial absent")

        case("acl", acl)
        first = broker.get()
        sensitive.append(first.password)

        def query(lease: Lease) -> None:
            """Open/close an actual short-lived connection and validate exact fictional product totals."""
            with connect(lease.username, lease.password) as connection:
                assert connection.execute(
                    "SELECT count(*), sum(quantity) FROM inventory"
                ).fetchone() == (2, 19)

        def readonly() -> None:
            """Prove SELECT works and INSERT is specifically denied by PostgreSQL SQLSTATE 42501."""
            query(first)
            with connect(first.username, first.password) as connection:
                try:
                    connection.execute("INSERT INTO inventory VALUES (3,'forbidden',1)")
                except psycopg.errors.InsufficientPrivilege as error:
                    assert error.sqlstate == "42501"
                else:
                    raise AssertionError("read-only role accepted a write")

        case("readonly", readonly)

        def renewal() -> None:
            """Use actual returned TTL, not requested increment, and prove credentials still authorize fresh SQL."""
            reply = root.request(
                "POST",
                "sys/leases/renew",
                {"lease_id": first.lease_id, "increment": "30s"},
            )
            assert 0 < reply["lease_duration"] <= 60
            query(first)

        case("renewal", renewal)
        second = broker.get(force=True)
        sensitive.append(second.password)

        def overlap() -> None:
            """New and old credentials both work during controlled handoff; roles/passwords differ."""
            assert (
                second.username != first.username and second.password != first.password
            )
            query(first)
            query(second)

        case("overlap", overlap)

        def rejects(lease: Lease) -> bool:
            """Only actual PostgreSQL authentication SQLSTATE rejection counts, not network/TLS failure."""
            try:
                with connect(lease.username, lease.password):
                    return False
            except psycopg.OperationalError as error:
                if error.sqlstate in {"28P01", "28000"}:
                    return True
                # libpq can omit SQLSTATE during authentication; independently prove the exact role was dropped.
                if error.sqlstate is None:
                    with connect("postgres", admin_password) as connection:
                        return connection.execute(
                            "SELECT count(*) FROM pg_roles WHERE rolname=%s",
                            (lease.username,),
                        ).fetchone() == (0,)
                raise

        def revocation() -> None:
            """Revoke the exact former lease, confirm role removal and verify new credentials still work."""
            root.request(
                "POST", "sys/leases/revoke", {"lease_id": first.lease_id, "sync": True}
            )
            wait(lambda: rejects(first))
            query(second)
            broker.invalidate(first)
            assert broker.get() is second

        case("revocation", revocation)
        root.request(
            "POST",
            "database/roles/reader",
            {
                "db_name": "lab",
                "default_ttl": "4s",
                "max_ttl": "60s",
                "creation_statements": [
                    'CREATE ROLE "{{name}}" WITH LOGIN PASSWORD \'{{password}}\' VALID UNTIL \'{{expiration}}\'; GRANT CONNECT ON DATABASE lab TO "{{name}}"; GRANT USAGE ON SCHEMA public TO "{{name}}"; GRANT SELECT ON public.inventory TO "{{name}}";'
                ],
                "revocation_statements": [
                    'REVOKE ALL ON public.inventory FROM "{{name}}"; REVOKE ALL ON SCHEMA public FROM "{{name}}"; REVOKE ALL ON DATABASE lab FROM "{{name}}"; DROP ROLE "{{name}}";'
                ],
            },
        )
        short = provider.issue()
        sensitive.append(short.password)

        def expiry() -> None:
            """Prove a real short-TTL credential initially works, then loses authentication/role access."""
            query(short)
            wait(lambda: rejects(short), 15)

            def absent() -> bool:
                """Independently wait for exact role deletion; PostgreSQL VALID UNTIL can reject before manager cleanup."""
                with connect("postgres", admin_password) as connection:
                    return connection.execute(
                        "SELECT count(*) FROM pg_roles WHERE rolname=%s",
                        (short.username,),
                    ).fetchone() == (0,)

            wait(absent, 10)
            query(second)

        case("expiry", expiry)

        def root_rotation() -> None:
            """Rotate the dedicated manager password, reject its original login, and prove subsequent issuance still works."""
            with connect("postgres", admin_password) as connection:
                original = connection.execute(
                    "SELECT rolpassword FROM pg_authid WHERE rolname='bao_manager'"
                ).fetchone()
            root.request("POST", "database/rotate-root/lab")
            try:
                with connect("bao_manager", actor_password):
                    raise AssertionError("old manager password still accepted")
            except psycopg.OperationalError:
                with connect("postgres", admin_password) as connection:
                    assert connection.execute("SELECT 1").fetchone() == (1,)
                    assert (
                        connection.execute(
                            "SELECT rolpassword FROM pg_authid WHERE rolname='bao_manager'"
                        ).fetchone()
                        != original
                    )
            replacement = provider.issue()
            sensitive.append(replacement.password)
            query(replacement)

        case("root_rotation", root_rotation)
        fresh = broker.get(force=True)
        sensitive.append(fresh.password)
        # This new short lease is deliberately 4s; one bounded timeout permits a valid fallback, then expires.
        assert manager.poll() is None
        manager.send_signal(signal.SIGSTOP)

        def outage_grace() -> None:
            """During a real stopped-manager outage, a still-valid cached credential works for fresh SQL."""
            assert broker.get(force=True) is fresh
            query(fresh)

        case("outage_grace", outage_grace)

        def outage_expiry() -> None:
            """After the conservative deadline, manager timeout cannot return expired cached credentials."""
            time.sleep(max(0, fresh.started_at + fresh.ttl - time.monotonic()))
            try:
                broker.get()
            except Unavailable:
                pass
            else:
                raise AssertionError("outage reused expired lease")

        case("outage_expiry", outage_expiry)
        manager.send_signal(signal.SIGCONT)

        def recovery() -> None:
            """An unpaused real manager issues a new usable identity, not the old failed generation."""
            recovered = broker.get()
            sensitive.append(recovered.password)
            assert recovered.username != fresh.username
            query(recovered)

        case("recovery", recovery)

        def identity_revocation() -> None:
            """Revoke the real application token: cascade its database lease and prove Broker drops its cached identity."""
            current = broker.get()
            root.request("POST", "auth/token/revoke", {"token": app_token})
            wait(lambda: rejects(current), 15)
            try:
                broker.get(force=True)
            except Unavailable:
                assert broker.stats()["denials"] == 1
            else:
                raise AssertionError("revoked application token reused credentials")

        case("identity_revocation", identity_revocation)

        def redaction() -> None:
            """Audit credential responses are HMACed; known tokens/passwords cannot occur in either private manager log."""
            manager_log.flush()
            audit_path = private / "audit.jsonl"
            assert audit_path.stat().st_size < 8 * 1024 * 1024
            log = audit_path.read_text(encoding="utf-8")
            assert all(value not in log for value in sensitive)
            events = [json.loads(line) for line in log.splitlines()]
            responses = [
                event
                for event in events
                if event["type"] == "response"
                and isinstance(
                    event.get("response", {}).get("data", {}).get("password"), str
                )
            ]
            assert responses and all(
                event["response"]["data"]["password"].startswith("hmac-sha256:")
                for event in responses
            )
            assert all(
                value not in (private / "manager.log").read_text(encoding="utf-8")
                for value in sensitive
            )

        case("redaction", redaction)
        manager.terminate()
        manager.wait(timeout=10)
        manager_log.close()
        manager_log = None
        manager = None
        case("cleanup", docker.cleanup)
        report = {
            "schema": 1,
            "mode": "live",
            "source_sha": sha,
            "cases": cases,
            "metrics": broker.stats(),
        }
        write_report(report, output / "report")
        print("LIVE_REPORT " + json.dumps(report), flush=True)
        return report
    except Exception as error:
        # Allowlisted identifiers/types only. No provider/database exception string, traceback, env or DSN dump.
        print(
            f"DRILL_FAILED case={current_case} type={type(error).__name__}", flush=True
        )
        raise RuntimeError(
            "live exercise failed; private diagnostics not published"
        ) from None
    finally:
        if manager is not None:
            if manager.poll() is None:
                manager.send_signal(signal.SIGCONT)
                manager.terminate()
                manager.wait(timeout=10)
        if manager_log is not None:
            manager_log.close()
        if docker.resources:
            docker.cleanup()


def main() -> int:
    """Require opt-in host acknowledgement and unique output; controlled failures cannot publish partial success."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--ack-disposable-docker", action="store_true")
    args = parser.parse_args()
    try:
        drill(args.output.absolute(), args.ack_disposable_docker)
    except (ValueError, RuntimeError, OSError, subprocess.SubprocessError):
        print(
            "Live drill refused/failed. Check safe case/type markers; no credentials are logged."
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
