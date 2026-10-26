"""Шаг 1. Создание serverless-индекса Pinecone (cosine, dim=1536)."""
import os, time
from config import MOCK, INDEX, DIM, REPORTS

if MOCK:
    info = f"[MOCK] Индекс '{INDEX}' создан (dimension={DIM}, metric=cosine, status=Ready)"
else:
    from pinecone import Pinecone, ServerlessSpec
    pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
    if INDEX not in pc.list_indexes().names():
        pc.create_index(name=INDEX, dimension=DIM, metric="cosine",
                        spec=ServerlessSpec(cloud=os.getenv("PINECONE_CLOUD", "aws"),
                                            region=os.getenv("PINECONE_REGION", "us-east-1")))
        while not pc.describe_index(INDEX).status["ready"]:
            time.sleep(1)
    info = str(pc.describe_index(INDEX))
print(info)
(REPORTS / "01_create_index.log").write_text(info + "\n", encoding="utf-8")
