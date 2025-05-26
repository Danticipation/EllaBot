import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
from backend.main import app
from backend.utils.intent_check import is_prompt_unclear

@pytest.fixture
def client():
    return TestClient(app)

@patch("backend.main.fetch_semantic_recall")
@patch("backend.main.get_llm_response", new_callable=AsyncMock)
@patch("backend.main.ThreadMemory")
@patch("backend.main.WeaviateClient")
def test_chat_endpoint_success(
    mock_weaviate_client,
    mock_thread_memory,
    mock_llm_response,
    mock_fetch_recall,
    client
):
    # Mock memory behavior
    memory_instance = MagicMock()
    memory_instance.get_messages.return_value = [{"author": "user", "message": "Hello"}]
    mock_thread_memory.return_value = memory_instance

    # Mock LLM response
    mock_llm_response.return_value = "Hi there!"
    mock_fetch_recall.return_value = [{
        "author": "user",
        "message": "What's up?",
        "timestamp": "2025-05-22T10:00:00Z"
    }]

    # Simulate Weaviate client and app state
    app.state.client = MagicMock()
    app.state.memory = memory_instance

    payload = {
        "author": "user",
        "message": "Hello, assistant!"
    }

    response = client.post("/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "context" in data
    assert "response" in data
    assert data["response"] == "Hi there!"
