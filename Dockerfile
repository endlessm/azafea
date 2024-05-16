FROM registry.hub.docker.com/library/python:3.8-alpine3.11

RUN apk add --update --no-cache ca-certificates && \
    wget https://s3.amazonaws.com/rds-downloads/rds-combined-ca-bundle.pem -O /usr/local/share/ca-certificates/rds.crt && \
    update-ca-certificates

RUN pip install --no-cache-dir pipenv template && \
    apk add --update --no-cache \
        build-base \
        cairo-dev \
        git \
        glib-dev \
        gobject-introspection-dev \
        libffi-dev \
        postgresql-dev

RUN adduser --system --shell /sbin/nologin --home /opt/azafea azafea && \
    install -d -m 755 -o azafea /opt/azafea/src
USER azafea
WORKDIR /opt/azafea/src

COPY Pipfile.lock .
RUN pipenv install --ignore-pipfile --dev

COPY --chown=azafea:root . .

ENV VERBOSE=false \
    NUM_OF_WORKERS=1 \
    REDIS_HOST=localhost \
    REDIS_PORT=6379 \
    REDIS_PASSWORD="CHANGE ME!!" \
    REDIS_SSL=false \
    POSTGRES_HOST=localhost \
    POSTGRES_PORT=5432 \
    POSTGRES_USER=azafea \
    POSTGRES_PASSWORD="CHANGE ME!!" \
    POSTGRES_DATABASE=azafea \
    POSTGRES_SSL_MODE=allow

ENTRYPOINT ["./entrypoint", "pipenv", "run", "azafea", "-c", "/tmp/config.toml"]
CMD ["run"]
HEALTHCHECK CMD pgrep python || exit 1
