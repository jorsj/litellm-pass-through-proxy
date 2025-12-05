import litellm
from litellm.integrations.custom_logger import CustomLogger

class DynamicGCPRouter(CustomLogger):
    async def async_pre_call_hook(self, user_api_key_dict, cache, data, call_type):
        """
        1. Reads 'x-gcp-project' (or similar) from headers.
        2. Overwrites the LiteLLM parameters for this specific request.
        """
        # Access headers (LiteLLM Proxy passes them in metadata["headers"])
        metadata = data.get("metadata") or {}
        raw_headers = metadata.get("headers") or {}
        
        # Normalize headers to lowercase for case-insensitive lookup
        headers = {k.lower(): v for k, v in raw_headers.items()}
        
        # Debug print to verify headers are coming through
        # print(f"DEBUG: Incoming Headers: {headers.keys()}")

        # 1. Handle Dynamic Project ID
        # Checks for 'x-gcp-project' (case-insensitive usually safe to check both)
        project_id = headers.get("x-gcp-project") or headers.get("x-gcp-project-id")
        
        if project_id:
            # Overwrite the 'vertex_project' parameter dynamically
            data["vertex_project"] = project_id
        
        # 2. Handle Dynamic Auth Token
        gcp_token = headers.get("x-gcp-token") or headers.get("authorization")
        
        if gcp_token:
            # Inject as access_token, stripping 'Bearer ' if present
            if gcp_token.lower().startswith("bearer "):
                gcp_token = gcp_token[7:] # len("Bearer ") == 7
            
            # Only set if it looks like a GCP token (simple heuristic or just pass it)
            # For now, we assume if x-gcp-token is provided, it's the access token.
            # If Authorization was used, it might be the proxy key, so be careful.
            # The user specifically asked for x-gcp-token support.
            
            if headers.get("x-gcp-token"):
                 data["access_token"] = gcp_token

        # 3. Handle Dynamic Region/Location
        location = headers.get("x-gcp-location")
        if location:
            data["vertex_location"] = location

        return data
