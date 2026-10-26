"""Шаг 2. Тест embedding-модели: вектор для одной фразы."""
from config import embed, MODEL, REPORTS
text = "Тестовая фраза: самый надёжный японский автомобиль"
v = embed([text])[0]
nz = [round(x, 4) for x in v if x != 0][:5]
msg = (f"model={MODEL}\ntext={text}\ndimension={len(v)}\n"
       f"first_5={[round(x, 4) for x in v[:5]]}\nfirst_5_nonzero={nz}\n")
print(msg)
(REPORTS / "02_test_embedding.log").write_text(msg, encoding="utf-8")
