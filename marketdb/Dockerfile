FROM python:3.12.10-bookworm AS builder

RUN set -ex \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        python3-dev \
        wget \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip setuptools gunicorn

# Set working directory
RUN mkdir -p /app
WORKDIR /app

# Add requirements (to leverage Docker cache)
ADD ./requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt --no-cache-dir

FROM python:3.12.10-bookworm AS deploy

# Copy Python environment from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages/ /usr/local/lib/python3.12/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV ENV=production

# Copy project files
WORKDIR /app
COPY . /app

# Expose port
EXPOSE 8000

# Entrypoint script
ENTRYPOINT ["./entrypoint.sh"]
