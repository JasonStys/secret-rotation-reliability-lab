# Multi-consumer generation handoff

Created by Jason Stys. A broker refresh is only one step: API workers, batch readers and report readers must each obtain the current lease, drain their own old connections and acknowledge the exact generation. The new in-process `Coordinator` tracks that distinction without changing the broker's existing retry, expiry or denial rules.

```text
python -m rotation handoff-demo --output out/consumer-handoff
```

Open `handoff.html`. This is explicitly a virtual-time simulation using the actual portable Broker/Coordinator and fictional provider, not live OpenBao/PostgreSQL evidence. It shows all three consumers accepting generation1, only the API accepting generation2, old-overlap expiry during an outage, current-lease expiry/denial, and complete generation3 recovery. Cached fallback to the same valid lease does not invent a generation. The original live TLS/permissions/revocation drill remains separate and unchanged.

`Coordinator(broker, consumers)` accepts1–32 unique nonidentifying codes. Make it the sole handoff owner of that broker. `refresh()` returns a bounded increasing generation for a different accepted lease object. `request(code)` returns `(generation, lease)` in memory and records delivery; it never acknowledges automatically. After application code drains its old owned connection pool, call `acknowledge(code, generation, lease, old_connections_drained=True)`. Unknown consumers, unrequested/stale/wrong-object generations, bool generations, undrained or replayed acknowledgement are rejected. Expired/blocked credentials cannot be requested or acknowledged. `invalidate(code, observed)` reports exact failed credentials to the broker; late old failures cannot block the current generation.

`status()` returns detached consumer work queues, requested/acknowledged generation, each consumer's accepted lifetime-window state, previous-generation overlap and current availability. It exports no username/password/token/lease ID. A fresh broker credential never implies all consumers acknowledged it. A hard provider denial blocks current handoff even before its nominal TTL; transient failure may use only the existing broker's still-valid cached fallback. Expiry/clock rollback cannot produce all-ready status.

Consumer names and drained-session acknowledgements are local in-process assertions, not authentication or proof that a database pool actually closed or a server accepted the credentials. The lifetime overlap flag is the local lease-time guard calculation, not a guarantee of server validity, session revocation or zero downtime. Production pools need their own drain/termination and new-authentication validation. No real secret is written by the coordinator and no connection pool or identity is revoked automatically. Use trusted processes/OS controls; this is not protection against the host administrator.

The finite demo writes only internally constructed allowlisted metadata and escaped scriptless HTML to a new private output directory under an existing parent. Original simulation/report contracts and all live/security gates remain unchanged. Coordinator state is bounded O(consumers), protected by a lock; no unbounded event history, background worker, external call, Docker repair or live service is introduced by the demo.
