#!/usr/bin/env sh
# Jason Stys: bounded wait for owned, generated TLS fixture files, then exec the native PostgreSQL entrypoint.
# Parameters: none. Files: /tmp/server.crt and /tmp/server.key are generated/copied by the owned drill only.
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: remaining — line 8
# END CODE MAP
set -eu
remaining=300
while [ ! -s /tmp/server.crt ] || [ ! -s /tmp/server.key ]; do
    remaining=$((remaining - 1))
    [ "$remaining" -gt 0 ] || exit 1
    sleep 0.1
done
exec docker-entrypoint.sh postgres -c ssl=on -c ssl_cert_file=/tmp/server.crt -c ssl_key_file=/tmp/server.key
