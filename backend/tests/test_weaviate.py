# test_weaviate.py
from weaviate import WeaviateClient
from weaviate.connect import ConnectionParams
import os

WEAVIATE_URL = os.getenv("WEAVIATE_URL", "http://localhost:8080")

client = WeaviateClient(
    connection_params=ConnectionParams.from_url(
        WEAVIATE_URL,
        grpc_port=50051
    )
)
client.connect()
print("✅ Connected to Weaviate.")
