FROM mysql:8.0.36

RUN microdnf install -y python3 \
    && microdnf clean all \
    && touch /home/flag.txt \
    && chown mysql:mysql /home/flag.txt

COPY lab/database/docker-entrypoint-initdb.d/revoke.sql /docker-entrypoint-initdb.d/10-revoke.sql
COPY lab/web/sqlitraining.sql /docker-entrypoint-initdb.d/20-schema.sql
COPY --chmod=755 lab/database/docker-entrypoint-initdb.d/gen.sh /docker-entrypoint-initdb.d/30-generate-flag.sh
