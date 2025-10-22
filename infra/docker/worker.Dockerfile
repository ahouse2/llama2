# syntax=docker/dockerfile:1.6

## Builder stage for Prefect worker runtime
FROM python:3.11-slim-bookworm AS builder

ENV POETRY_VERSION=1.8.3 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    VIRTUAL_ENV=/opt/venv \
    POETRY_NO_INTERACTION=1

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        build-essential \
        curl \
        git \
        libgl1 \
        libglib2.0-0 \
        libjpeg62-turbo \
        liblept5 \
        libpng16-16 \
        libpoppler-cpp-dev \
        libpq-dev \
        libsm6 \
        libtesseract-dev \
        libxext6 \
        libxrender1 \
        pkg-config \
        poppler-utils \
        tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv "$VIRTUAL_ENV" \
    && "$VIRTUAL_ENV/bin/pip" install --upgrade pip setuptools wheel \
    && "$VIRTUAL_ENV/bin/pip" install "poetry==${POETRY_VERSION}"

ENV PATH="$VIRTUAL_ENV/bin:$PATH"
WORKDIR /build

COPY apps/backend/pyproject.toml apps/backend/poetry.lock ./
RUN poetry export --with api --without-hashes --format requirements.txt --output requirements.txt
RUN pip install --no-deps --upgrade -r requirements.txt

COPY apps/backend/app ./app

RUN mkdir -p /runtime/bin /runtime/lib /runtime/share/tessdata \
    && cp /usr/bin/tesseract /runtime/bin/ \
    && cp -a /usr/share/tesseract-ocr/tessdata /runtime/share/ \
    && cp /usr/lib/x86_64-linux-gnu/libtesseract.so* /runtime/lib/ \
    && cp /usr/lib/x86_64-linux-gnu/liblept.so* /runtime/lib/ \
    && cp /usr/lib/x86_64-linux-gnu/libpng16.so* /runtime/lib/ \
    && cp /usr/lib/x86_64-linux-gnu/libjpeg.so* /runtime/lib/ \
    && cp /usr/lib/x86_64-linux-gnu/libopenjp2.so* /runtime/lib/ \
    && cp /usr/lib/x86_64-linux-gnu/libtiff.so* /runtime/lib/ \
    && cp /usr/lib/x86_64-linux-gnu/libwebp.so* /runtime/lib/ \
    && cp /usr/lib/x86_64-linux-gnu/libwebpmux.so* /runtime/lib/ \
    && cp /usr/lib/x86_64-linux-gnu/libwebpdemux.so* /runtime/lib/ \
    && cp /usr/lib/x86_64-linux-gnu/libharfbuzz.so* /runtime/lib/ \
    && cp /usr/lib/x86_64-linux-gnu/libGL.so* /runtime/lib/ \
    && cp /usr/lib/x86_64-linux-gnu/libglib-2.0.so* /runtime/lib/ \
    && cp /usr/lib/x86_64-linux-gnu/libsm.so* /runtime/lib/ \
    && cp /usr/lib/x86_64-linux-gnu/libXext.so* /runtime/lib/ \
    && cp /usr/lib/x86_64-linux-gnu/libXrender.so* /runtime/lib/ \
    && cp /usr/lib/x86_64-linux-gnu/libstdc++.so* /runtime/lib/ \
    && cp /usr/lib/x86_64-linux-gnu/libgomp.so* /runtime/lib/ \
    && cp /usr/lib/x86_64-linux-gnu/libquadmath.so* /runtime/lib/ \
    && cp /usr/lib/x86_64-linux-gnu/libopenblasp*.so* /runtime/lib/

FROM gcr.io/distroless/python3-debian12

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:$PATH" \
    LD_LIBRARY_PATH="/opt/runtime/lib:/usr/lib/x86_64-linux-gnu"

WORKDIR /srv/app

COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /build/app ./app
COPY --from=builder /runtime/bin/tesseract /usr/bin/tesseract
COPY --from=builder /runtime/share/tessdata /usr/share/tessdata
COPY --from=builder /runtime/lib /opt/runtime/lib

USER nonroot

ENV PREFECT_API_URL="https://prefect.discovery.local/api" \
    PREFECT_LOGGING_LEVEL=INFO \
    PREFECT_WORK_QUEUE="discovery-default"

ENTRYPOINT ["prefect", "agent", "start", "--work-queue", "discovery-default"]
