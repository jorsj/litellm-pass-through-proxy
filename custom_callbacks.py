from litellm.integrations.custom_logger import CustomLogger
from litellm.exceptions import InvalidRequestError
import litellm
from litellm.proxy.proxy_server import UserAPIKeyAuth, DualCache
from litellm.types.utils import ModelResponseStream
from typing import Any, AsyncGenerator, Optional, Literal
import json

class DynamicGCPRouter(CustomLogger):
    async def async_pre_call_hook(self, user_api_key_dict: UserAPIKeyAuth, cache: DualCache, data: dict, call_type: Literal[
            "completion",
            "text_completion",
            "embeddings",
            "image_generation",
            "moderation",
            "audio_transcription",
    ]):
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
        print(f"DEBUG: Incoming Headers: {headers.keys()}")

        # 0. Inspect LiteLLM virtual-key metadata for downstream routing/validation.
        key_tags = getattr(user_api_key_dict, "tags", None)
        key_metadata_raw = getattr(user_api_key_dict, "metadata", None)
        if isinstance(key_metadata_raw, str):
            try:
                key_metadata = json.loads(key_metadata_raw)
            except json.JSONDecodeError:
                key_metadata = None
        else:
            key_metadata = key_metadata_raw if isinstance(key_metadata_raw, dict) else None
        key_alias = getattr(user_api_key_dict, "key_alias", None)
        print(
            "DEBUG: LiteLLM key",
            {
                "alias": key_alias,
                "tags": key_tags,
                "metadata": key_metadata,
            },
        )

        model_id = data.get("model") if isinstance(data, dict) else None
        is_vertex_model = isinstance(model_id, str) and (
            model_id.startswith("vertex_ai/") 
            or model_id.startswith("gemini-")
            or model_id.startswith("gemini_")
            or model_id.startswith("vertexai")
        )
        if is_vertex_model:
            project_id = key_metadata.get("gcp_project_id") if isinstance(key_metadata, dict) else None
            if not project_id:
                raise InvalidRequestError(
                    "Missing gcp_project_id in key metadata for Google Vertex requests.",
                    model=model_id or "vertex_ai/unknown",
                    llm_provider="vertex_ai",
                )
            
            if project_id:
                # Overwrite the 'vertex_project' parameter dynamically
                data["vertex_project"] = project_id

        return data
    
    async def async_post_call_failure_hook(
        self, 
        request_data: dict,
        original_exception: Exception, 
        user_api_key_dict: UserAPIKeyAuth,
        traceback_str: Optional[str] = None,
    ):
        pass

    async def async_post_call_success_hook(
        self,
        data: dict,
        user_api_key_dict: UserAPIKeyAuth,
        response,
    ):
        pass

    async def async_moderation_hook( # call made in parallel to llm api call
        self,
        data: dict,
        user_api_key_dict: UserAPIKeyAuth,
        call_type: Literal["completion", "embeddings", "image_generation", "moderation", "audio_transcription"],
    ):
        pass

    async def async_post_call_streaming_hook(
        self,
        user_api_key_dict: UserAPIKeyAuth,
        response: str,
    ):
        pass

    async def async_post_call_streaming_iterator_hook(
        self,
        user_api_key_dict: UserAPIKeyAuth,
        response: Any,
        request_data: dict,
    ) -> AsyncGenerator[ModelResponseStream, None]:
        """
        Passes the entire stream to the guardrail

        This is useful for plugins that need to see the entire stream.
        """
        async for item in response:
            yield item


proxy_handler_instance = DynamicGCPRouter()