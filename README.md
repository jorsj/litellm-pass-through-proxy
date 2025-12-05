# LiteLLM Pass-Through Proxy

This is a lightweight proxy server using [LiteLLM](https://github.com/BerriAI/litellm) that dynamically forwards requests to different Google Cloud Platform (GCP) projects based on request headers.

## Features

- **Dynamic GCP Project:** Route requests to different GCP projects using headers.
- **Dynamic Location:** Specify the Vertex AI region/location per request.
- **Dynamic Auth:** Pass a specific GCP access token.
- **Standard API:** Fully compatible with OpenAI's Chat Completions and Image Generations API.

## Setup

1.  **Install Dependencies:**
    ```bash
    uv sync
    ```

2.  **Run the Proxy:**
    ```bash
    uv run run_proxy.py
    ```
    The server will start on `http://0.0.0.0:8000`.

## Usage

### Chat Completion

```bash
curl -X POST http://localhost:8000/chat/completions \
  -H "Content-Type: application/json" \
  -H "x-gcp-project: your-project-id" \
  -H "x-gcp-location: us-central1" \
  -H "Authorization: Bearer optional-proxy-key" \
  -d 
  {
    "model": "gemini-2.5-flash",
    "messages": [{"role": "user", "content": "Hello!"}]
  }
```

### Image Generation

```bash
curl -X POST http://localhost:8000/images/generations \
  -H "Content-Type: application/json" \
  -H "x-gcp-project: your-project-id" \
  -d 
  {
    "model": "imagen-3.0-generate-001",
    "prompt": "A futuristic city"
  }
```

### Custom Headers

- `x-gcp-project` (or `x-gcp-project-id`): The Google Cloud Project ID to use for Vertex AI.
- `x-gcp-location`: The region (e.g., `us-central1`, `europe-west1`).
- `x-gcp-token`: (Optional) A raw GCP access token to use for authentication. If provided, it overrides the default environment credentials.

## Configuration

The proxy is configured via `config.yaml`. You can add more models there if needed. The current config includes:
- `gemini-3-pro-preview`
- `gemini-2.5-flash`
- `imagen-3.0-generate-001`