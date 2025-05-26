import pytest
from unittest.mock import MagicMock
from backend.main import fetch_semantic_recall

@pytest.fixture
def mock_weaviate_client():
    mock_client = MagicMock()
    mock_collection = MagicMock()

    # Simulate returned object structure
    mock_object = MagicMock()
    mock_object.properties = {
        "author": "user",
        "message": "Hello, world!",
        "timestamp": "2025-05-22T10:00:00Z"
    }

    mock_collection.query.near_text.return_value.objects = [mock_object]
    mock_client.collections.get.return_value = mock_collection

    return mock_client

def test_fetch_semantic_recall_returns_expected_structure(mock_weaviate_client):
    query_text = "Hello"
    results = fetch_semantic_recall(mock_weaviate_client, query_text)

    assert isinstance(results, list)
    assert len(results) == 1
    assert results[0]["author"] == "user"
    assert results[0]["message"] == "Hello, world!"
    assert "timestamp" in results[0]
