"""Шаг 3. Загрузка ≥20 фраз в Pinecone с metadata."""
import json
from config import ROOT, embed, get_index, NS, REPORTS
items = json.loads((ROOT / "data/phrases.json").read_text(encoding="utf-8"))
assert len(items) >= 20, "Нужно не менее 20 фраз"
vecs = embed([i["text"] for i in items])
index = get_index()
payload = [{"id": i["id"], "values": v, "metadata": {"text": i["text"], "brand": i["brand"]}}
           for i, v in zip(items, vecs)]
index.upsert(vectors=payload, namespace=NS)
stats = index.describe_index_stats()
msg = f"upserted={len(payload)} namespace={NS}\nstats={stats}\n"
print(msg)
(REPORTS / "03_upsert.log").write_text(msg, encoding="utf-8")
