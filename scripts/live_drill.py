"""Real TLS OpenBao/PostgreSQL lifecycle on an acknowledged disposable Linux Docker host. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: ROOT — line 209
# variable: LABEL — line 210
# definition: output_directory — line 213
# parameter: path — line 213
# variable: original — line 215
# variable: parent — line 216
# variable: allowed — line 218
# variable: canonical — line 218
# variable: relative — line 221
# variable: part — line 223
# definition: port — line 229
# variable: connection — line 231
# definition: owned — line 236
# parameter: expected_name — line 237
# parameter: metadata — line 237
# parameter: network — line 237
# parameter: owner — line 237
# variable: name — line 240
# variable: labels — line 241
# definition: Docker — line 254
# definition: __init__ — line 257
# parameter: acknowledgment — line 257
# parameter: self — line 257
# attribute: owner — line 263
# attribute: name — line 264
# attribute: environment — line 265
# variable: key — line 267
# variable: value — line 267
# attribute: argv — line 270
# attribute: resources — line 271
# definition: call — line 273
# parameter: args — line 274
# parameter: data — line 274
# parameter: self — line 274
# parameter: timeout — line 274
# variable: result — line 277
# definition: inspect — line 289
# parameter: kind — line 289
# parameter: name — line 289
# parameter: self — line 289
# variable: raw — line 293
# variable: values — line 296
# definition: cleanup — line 302
# parameter: self — line 302
# variable: kind — line 304
# variable: name — line 304
# variable: remaining — line 307
# definition: certificate — line 322
# parameter: directory — line 322
# parameter: name — line 322
# variable: cert — line 324
# variable: key — line 324
# variable: result — line 325
# definition: tls_archive — line 354
# parameter: cert — line 354
# parameter: gid — line 354
# parameter: key — line 354
# parameter: uid — line 354
# variable: output — line 356
# variable: archive — line 357
# variable: mode — line 358
# variable: name — line 358
# variable: path — line 358
# variable: data — line 362
# variable: entry — line 363
# attribute: gid — line 364
# attribute: mode — line 364
# attribute: size — line 364
# attribute: uid — line 364
# definition: wait — line 369
# parameter: operation — line 369
# parameter: seconds — line 369
# variable: deadline — line 371
# definition: drill — line 379
# parameter: acknowledgment — line 379
# parameter: output — line 379
# variable: docker — line 381
# variable: sha — line 385
# variable: image — line 388
# variable: output — line 395
# variable: private — line 396
# variable: manager — line 399
# variable: manager_log — line 400
# variable: cases — line 401
# variable: sensitive — line 402
# variable: broker — line 403
# variable: current_case — line 404
# definition: case — line 406
# parameter: name — line 406
# parameter: operation — line 406
# variable: current_case — line 409
# variable: start — line 410
# variable: result — line 412
# variable: ca — line 421
# variable: key — line 421
# variable: db_ca — line 422
# variable: db_key — line 422
# variable: endpoint — line 423
# variable: config — line 424
# variable: manager_log — line 437
# variable: manager — line 438
# variable: anonymous — line 444
# definition: ready — line 446
# variable: initialized — line 454
# variable: root_token — line 457
# variable: unseal_key — line 457
# variable: root — line 463
# definition: tls_proof — line 476
# variable: wrong — line 478
# variable: db_name — line 487
# variable: network_name — line 487
# variable: actor_password — line 499
# variable: admin_password — line 499
# variable: env_file — line 504
# variable: identity — line 549
# variable: metadata — line 555
# variable: binding — line 556
# variable: db_port — line 561
# definition: connect — line 563
# parameter: password — line 563
# parameter: username — line 563
# definition: db_ready — line 577
# variable: connection — line 584
# definition: bootstrap — line 591
# variable: connection — line 593
# variable: auth — line 639
# variable: app_token — line 644
# variable: app — line 646
# variable: provider — line 647
# variable: broker — line 648
# definition: acl — line 650
# variable: client — line 652
# variable: method — line 652
# variable: path — line 652
# variable: payload — line 652
# variable: first — line 666
# definition: query — line 669
# parameter: lease — line 669
# variable: connection — line 671
# definition: readonly — line 676
# variable: connection — line 679
# definition: renewal — line 689
# variable: reply — line 691
# variable: second — line 700
# definition: overlap — line 703
# definition: rejects — line 713
# parameter: lease — line 713
# variable: connection — line 723
# definition: revocation — line 730
# variable: short — line 756
# definition: expiry — line 759
# definition: absent — line 764
# variable: connection — line 766
# definition: root_rotation — line 777
# variable: connection — line 779
# variable: original — line 780
# variable: connection — line 788
# variable: replacement — line 796
# variable: fresh — line 801
# definition: outage_grace — line 807
# definition: outage_expiry — line 814
# definition: recovery — line 827
# variable: recovered — line 829
# definition: identity_revocation — line 836
# variable: current — line 838
# definition: redaction — line 850
# variable: audit_path — line 853
# variable: log — line 855
# variable: value — line 856
# variable: events — line 857
# variable: line — line 857
# variable: responses — line 858
# variable: event — line 860
# variable: event — line 868
# variable: value — line 872
# variable: manager_log — line 879
# variable: manager — line 880
# variable: report — line 882
# definition: main — line 912
# variable: parser — line 914
# variable: args — line 917
# END CODE MAP

from __future__ import annotations

import argparse
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
            'storage "inmem" {}\ndisable_mlock = true\nui = false\napi_addr = '
            + json.dumps(endpoint)
            + '\nlistener "tcp" {\naddress = '
            + json.dumps("127.0.0.1:" + endpoint.rsplit(":", 1)[1])
            + "\ntls_cert_file = "
            + json.dumps(str(ca))
            + "\ntls_key_file = "
            + json.dumps(str(key))
            + "\nmax_request_size = 65536\n}\n",
            encoding="utf-8",
        )
        manager_log = (private / "manager.log").open("wb")
        manager = subprocess.Popen(
            [str(ROOT / ".tools/bao"), "server", "-config=" + str(config)],
            cwd=private,
            stdout=manager_log,
            stderr=subprocess.STDOUT,
        )
        anonymous = Transport(endpoint, ca)

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
        root = Transport(endpoint, ca, root_token)
        root.request(
            "PUT",
            "sys/audit/file",
            {
                "type": "file",
                "options": {
                    "file_path": str(private / "audit.jsonl"),
                    "log_raw": "false",
                },
            },
        )

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
        docker.call(
            ["cp", "--archive", "-", db_name + ":/tmp"],
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
        app = Transport(endpoint, ca, app_token)
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
                "PUT",
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
                "PUT", "sys/leases/revoke", {"lease_id": first.lease_id, "sync": True}
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
