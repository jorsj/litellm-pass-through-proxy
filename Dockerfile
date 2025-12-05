FROM python:3.13-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy project files
COPY pyproject.toml uv.lock ./
COPY config.yaml custom_callbacks.py run_proxy.py ./

# Install dependencies
# --frozen ensures we use the exact versions in uv.lock
RUN uv sync --frozen --no-cache

# Expose port 8000 (Cloud Run defaults to 8080, but we can configure it or change app port)
# We will configure Cloud Run to route to 8000 or change the app to listen on PORT env var.
# For simplicity, let's tell Cloud Run to listen to 8000.
ENV PORT=8000

# Run the proxy
CMD ["uv", "run", "run_proxy.py"]
