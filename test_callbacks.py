import pytest
from unittest.mock import MagicMock
from custom_callbacks import DynamicGCPRouter

@pytest.mark.asyncio
async def test_dynamic_gcp_router():
    router = DynamicGCPRouter()
    
    # Mock data structure passed by LiteLLM
    data = {
        "model": "vertex_ai/gemini-pro",
        "metadata": {
            "headers": {
                "x-gcp-project": "dynamic-project-id",
                "x-gcp-location": "asia-northeast1",
                "x-gcp-token": "Bearer my-secret-token"
            }
        }
    }
    
    # Run the hook
    updated_data = await router.async_pre_call_hook(
        user_api_key_dict={},
        cache=None,
        data=data,
        call_type="completion"
    )
    
    # Assertions
    assert updated_data["vertex_project"] == "dynamic-project-id"
    assert updated_data["vertex_location"] == "asia-northeast1"
    assert updated_data["access_token"] == "my-secret-token" # Should be stripped

@pytest.mark.asyncio
async def test_dynamic_gcp_router_case_insensitive():
    router = DynamicGCPRouter()
    
    data = {
        "model": "vertex_ai/gemini-pro",
        "metadata": {
            "headers": {
                "X-GCP-PROJECT-ID": "UPPERCASE-PROJECT",
            }
        }
    }
    
    updated_data = await router.async_pre_call_hook(
        {}, None, data, "completion"
    )
    
    assert updated_data["vertex_project"] == "UPPERCASE-PROJECT"
