FROM ubuntu:22.04
LABEL maintainer="anders.svensson.46@protonmail.com"
LABEL org.opencontainers.image.authors="anders.svensson.46@protonmail.com"
LABEL org.opencontainers.image.url="https://github.com/ansv46/nfa"
LABEL org.opencontainers.image.documentation="https://github.com/ansv46/nfa/blob/main/README.md"
LABEL org.opencontainers.image.source="https://github.com/ansv46/nfa"
LABEL org.opencontainers.image.title="ansv46/nfa"
LABEL org.opencontainers.image.description="Use nfstream from Arkime."

ENV DEBIAN_FRONTEND noninteractive

WORKDIR /nfa

COPY main.py /nfa
COPY requirements.txt /nfa

RUN apt-get update --fix-missing && \
    apt-get install -qqy --no-install-recommends \
        curl \
        gcc \
        python3-dev \
        python3-pip \
        python3-venv && \
    python3 -m venv nfa && \
    . nfa/bin/activate && python3 -m pip install --no-cache-dir -U pip setuptools && \
    . nfa/bin/activate && python3 -m pip install --no-cache-dir -r requirements.txt && \
    mkdir static && cd static \
    curl -O -s https://cdn.jsdelivr.net/npm/swagger-ui-dist@3/swagger-ui-bundle.js && \
    curl -O -s https://cdn.jsdelivr.net/npm/swagger-ui-dist@3/swagger-ui.css && \
    curl -O -s https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js && \
    apt remove -y curl git && \
    apt autoremove -y && \
    apt autoclean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /nfa
CMD ["./nfa/bin/uvicorn", "main:app", "--port", "5001", "--host", "*"]
EXPOSE 5001
