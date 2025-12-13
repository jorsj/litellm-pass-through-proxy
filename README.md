# LiteLLM Pass-Through Proxy

## https://docs.litellm.ai/docs/proxy/quick_start

This is a lightweight proxy server using [LiteLLM](https://github.com/BerriAI/litellm) that dynamically forwards requests to different Google Cloud Platform (GCP) projects based on request headers.

## Features

- **Dynamic GCP Project:** Route requests to different GCP projects using headers.
- **Dynamic Location:** Specify the Vertex AI region/location per request.
- **Dynamic Auth:** Pass a specific GCP access token.
- **Standard API:** Fully compatible with OpenAI's Chat Completions and Image Generations API.

## Setup

1.  **Install Dependencies:**
  ```bash
  poetry install
  ```

2.  **Run the Proxy:**
  ```bash
  poetry run run-proxy
  ```
  Este comando ejecuta automáticamente `prisma generate` usando el esquema incluido en LiteLLM; solo asegúrate de que tu base de datos (`database_url` en `config.yaml`) sea accesible.
    The server will start on `http://0.0.0.0:8000`.

## GCloud Auth Setup

To use the `curl` examples below with `$(gcloud auth print-access-token)`, you need to have the Google Cloud CLI installed and authenticated.

1.  **Install Google Cloud CLI:**
    Follow the official guide: https://cloud.google.com/sdk/docs/install

2.  **Login:**
    ```bash
    gcloud auth login
    ```
    This authorizes the gcloud CLI to access Google Cloud APIs.

3.  **(Optional) Set Default Project:**
    ```bash
    gcloud config set project YOUR_PROJECT_ID
    ```

4.  **(Optional) Application Default Credentials:**
    If you prefer not to pass the token explicitly in every request (or to run the proxy with default local credentials), you can set up Application Default Credentials (ADC):
    ```bash
    gcloud auth application-default login
    ```
    This creates a credentials file that client libraries can automatically find.

    To explicitly set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable (e.g., when using a Service Account key):
    ```bash
    export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account-key.json"
    ```

## Usage

### Chat Completion

```bash
curl -X POST http://localhost:8000/chat/completions \
  -H "Content-Type: application/json" \
  -H "x-gcp-project: your-project-id" \
  -H "x-gcp-location: us-central1" \
  -H "Authorization: Bearer $(gcloud auth print-access-token)$" \
  -d '{
    "model": "gemini-2.5-flash",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

### Image Generation

```bash
curl -X POST http://localhost:8000/images/generations \
  -H "Content-Type: application/json" \
  -H "x-gcp-project: your-project-id" \
  -d '{
    "model": "imagen-3.0-generate-001",
    "prompt": "A futuristic city"
  }'
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

## Custom Callbacks from a Mounted Volume

1. Place `custom_callbacks.py` (or a package containing it) in the external directory you plan to mount, for example `/data/custom-callbacks`.
2. Mount that directory inside the container, such as `/tmp/custom-callbacks`.
3. Expose the mount to Python by setting `PYTHONPATH="/tmp/custom-callbacks:${PYTHONPATH}"` in the container environment.
4. Reference the callback in `config.yaml` using the module path, for example `callbacks: custom_callbacks.proxy_handler_instance`.
5. Restart the deployment so the proxy loads the newly mounted code.

### Kubernetes manifest snippet

```yaml
        volumeMounts:
          - name: custom-callbacks
            mountPath: /tmp/custom-callbacks
      env:
        - name: PYTHONPATH
          value: "/tmp/custom-callbacks:${PYTHONPATH}"
      volumes:
        - name: custom-callbacks
          persistentVolumeClaim:
            claimName: custom-callbacks-pvc
```

Any directory added to `PYTHONPATH` is appended to `sys.path`, which allows LiteLLM to import the callback module at runtime via `importlib.import_module`.

## Deployment

To deploy to Google Cloud Run, use the provided `deploy.sh` script:

```bash
./deploy.sh <PROJECT_ID> [REGION]
```

Example:

```bash
./deploy.sh my-gcp-project us-central1
```

This script will:
1.  Enable necessary Google Cloud APIs.
2.  Build the Docker image using Cloud Build.
3.  Deploy the service to Cloud Run.