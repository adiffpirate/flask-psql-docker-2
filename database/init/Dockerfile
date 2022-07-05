FROM jbergknoff/postgresql-client

# Install netcat needed for wait-for-db
RUN apk add --update netcat-openbsd
# Copy init files
COPY entrypoint.sh /entrypoint.sh
COPY queries /queries

ENTRYPOINT ["/bin/sh", "/entrypoint.sh"]
