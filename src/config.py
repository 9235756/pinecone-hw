"""Общая конфигурация: чтение local.env, эмбеддинги и индекс Pinecone (или mock)."""
import hashlib, json, os, pathlib
import numpy as np
from dotenv import load_dotenv

ROOT = pathlib.Path(__file__).resolve().parent.parent
load_dotenv(ROOT / "local.env")

MOCK = os.getenv("MOCK", "1") == "1"
MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
DIM = int(os.getenv("EMBEDDING_DIM", "1536"))
INDEX = os.getenv("PINECONE_INDEX", "auto-brands-memory")
NS = os.getenv("PINECONE_NAMESPACE", "cars")
TOP_K = int(os.getenv("TOP_K", "3"))
MODE = "mock" if MOCK else "real"
REPORTS = ROOT / "reports" / MODE
REPORTS.mkdir(parents=True, exist_ok=True)


def embed(texts: list[str]) -> list[list[float]]:
    """Эмбеддинги текстов. В MOCK — детерминированные векторы из хэшей слов."""
    if MOCK:
        out = []
        for t in texts:
            v = np.zeros(DIM)
            for w in t.lower().replace(",", " ").replace("—", " ").replace("?", " ").split():
                stem = w[:5]  # грубая «лемматизация» для эмуляции
                h = int(hashlib.md5(stem.encode()).hexdigest(), 16)
                v[h % DIM] += 1.0
            v /= (np.linalg.norm(v) or 1)
            out.append(v.tolist())
        return out
    from openai import OpenAI
    client = OpenAI(api_key=os.environ["PROXYAPI_KEY"], base_url=os.getenv("OPENAI_BASE_URL"))
    resp = client.embeddings.create(model=MODEL, input=texts)
    return [d.embedding for d in resp.data]


class MockIndex:
    """In-memory замена Pinecone Index (cosine), хранится в reports/mock_index.json."""
    path = ROOT / "reports" / "mock_index.json"

    def __init__(self):
        self.store = json.loads(self.path.read_text()) if self.path.exists() else {}

    def upsert(self, vectors, namespace=NS):
        ns = self.store.setdefault(namespace, {})
        for v in vectors:
            ns[v["id"]] = {"values": v["values"], "metadata": v["metadata"]}
        self.path.write_text(json.dumps(self.store))
        return {"upserted_count": len(vectors)}

    def describe_index_stats(self):
        return {"dimension": DIM,
                "namespaces": {k: {"vector_count": len(v)} for k, v in self.store.items()},
                "total_vector_count": sum(len(v) for v in self.store.values())}

    def query(self, vector, top_k=TOP_K, namespace=NS, include_metadata=True):
        q = np.array(vector)
        res = [{"id": vid, "score": float(np.dot(q, np.array(it["values"]))), "metadata": it["metadata"]}
               for vid, it in self.store.get(namespace, {}).items()]
        res.sort(key=lambda r: r["score"], reverse=True)
        return {"matches": res[:top_k]}


def get_index():
    if MOCK:
        return MockIndex()
    from pinecone import Pinecone
    pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
    return pc.Index(INDEX)
