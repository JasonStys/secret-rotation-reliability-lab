# Jason Stys: derived non-root-only PostgreSQL lab image; remove unused vulnerable root-switch helper.
# BASE: exact official PostgreSQL image digest below. Runtime user: postgres; no root entrypoint path supported.
FROM postgres:18-alpine@sha256:77f585114c32fbca283dc835b0596f4e52b51b4c6662d7810b2f4084f60a1873
USER root
# gosu is only used by the upstream entrypoint when started as root; this lab always starts as postgres.
# This removes the unused component rather than ignoring its vulnerability findings.
# Published Alpine security updates remain strict exact package pins; scan the actual resulting image.
RUN apk add --no-cache --upgrade \
      brotli-libs=1.2.1-r0 \
      libcurl=8.23.0-r0 \
      musl=1.2.6-r3 \
      musl-utils=1.2.6-r3 \
      zlib=1.4-r0 \
    && rm /usr/local/bin/gosu
USER postgres


COPY ops/start-postgres.sh /start-postgres.sh
ENTRYPOINT ["sh", "/start-postgres.sh"]
