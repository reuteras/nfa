FROM debian:13.1
LABEL maintainer="anders.svensson.46@protonmail.com"
LABEL org.opencontainers.image.authors="anders.svensson.46@protonmail.com"
LABEL org.opencontainers.image.url="https://github.com/ansv46/nfa"
LABEL org.opencontainers.image.documentation="https://github.com/ansv46/nfa/blob/main/README.md"
LABEL org.opencontainers.image.source="https://github.com/ansv46/nfa"
LABEL org.opencontainers.image.title="ansv46/nfa"
LABEL org.opencontainers.image.description="Use nfstream from Arkime."

ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

RUN apt-get update --fix-missing && \
    apt-get install -qqy --no-install-recommends \
        ca-certificates=20250101 \
        curl=8.12.0-1 \
        gcc=4:14.2.0-1 \
        git=1:2.48.0-1 \
        python3-dev=3.12.7-1 \
        python3-pip=24.3.1+dfsg-1 \
        python3-venv=3.12.7-1 && \
    git clone --depth 1 --branch main https://github.com/reuteras/nfa.git /app && \
    cd /app && \
    rm -rf .git* && \
    mkdir tmp && \
    python3 -m venv .venv && \
    .venv/bin/python3 -m pip install --no-cache-dir -U pip==24.3.1 setuptools==75.6.0 && \
    .venv/bin/python3 -m pip install --no-cache-dir . && \
    mkdir static && cd static && \
    curl -O -s https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.18.2/swagger-ui-bundle.js && \
    curl -O -s https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.18.2/swagger-ui.css && \
    curl -O -s https://cdn.jsdelivr.net/npm/redoc@2.1.5/bundles/redoc.standalone.js && \
    cd /app && \
    useradd -u 1000 -M -s /bin/bash nfa && \
    chown -R nfa:nfa /app && \
    apt-get remove -y gcc git && \
    apt-get autoremove -y && \
    apt-get autoclean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
USER nfa
EXPOSE 5001
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5001/docs || exit 1
CMD ["./.venv/bin/uvicorn", "main:app", "--port", "5001", "--host", "0.0.0.0"]
