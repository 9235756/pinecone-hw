"""Шаг 4. Поиск по смыслу: 5 уникальных запросов -> отчёт Markdown + JSON."""
import json, time
from config import embed, get_index, NS, TOP_K, REPORTS, MODE
QUERIES = [
    "Какая машина подойдёт для поездок по лесу и грязи?",
    "Посоветуй автомобиль на электричестве",
    "Нужна недорогая и экономичная машина",
    "Какой бренд делает самые безопасные автомобили?",
    "Хочу быстрый спортивный автомобиль",
]
index = get_index()
if MODE == "real":
    time.sleep(5)  # serverless-индексу нужно несколько секунд после upsert
lines = [f"# Отчёт поиска по смыслу (режим={MODE}, top_k={TOP_K})\n"]
dump = []
for q in QUERIES:
    matches = index.query(vector=embed([q])[0], top_k=TOP_K, namespace=NS, include_metadata=True)["matches"]
    lines += [f"\n## Запрос: «{q}»\n", "| # | ID | score | Текст |", "|---|----|-------|-------|"]
    for n, m in enumerate(matches, 1):
        lines.append(f"| {n} | {m['id']} | {m['score']:.4f} | {m['metadata']['text']} |")
        print(f"{q[:45]:<45} -> {m['id']} {m['score']:.4f} {m['metadata']['text']}")
    dump.append({"query": q, "matches": [{"id": m["id"], "score": round(m["score"], 4),
                                          "text": m["metadata"]["text"]} for m in matches]})
(REPORTS / "search_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
(REPORTS / "search_results.json").write_text(json.dumps(dump, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\nОтчёт сохранён: {REPORTS / 'search_report.md'}")
