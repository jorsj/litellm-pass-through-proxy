import uvicorn
import litellm
import os
import sys

# Ensure current directory is in python path
sys.path.append(os.getcwd())

from custom_callbacks import DynamicGCPRouter
from litellm.proxy.proxy_server import app

# Register Custom Callback
# This hooks into LiteLLM's event loop
print("Registering DynamicGCPRouter...")
litellm.callbacks = [DynamicGCPRouter()]

# Set Configuration Path
os.environ["LITELLM_CONFIG_PATH"] = "./config.yaml"

if __name__ == "__main__":
    # Run the server
    # We use the 'app' object imported from proxy_server
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
