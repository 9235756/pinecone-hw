"""Шаг 5 (бонус). Telegram-бот: сообщение -> поиск по векторной памяти -> top-3."""
import asyncio, os
from aiogram import Bot, Dispatcher, types
from config import embed, get_index, NS, TOP_K

bot = Bot(os.environ["TELEGRAM_BOT_TOKEN"])
dp = Dispatcher()
index = get_index()

@dp.message()
async def answer(msg: types.Message):
    res = index.query(vector=embed([msg.text])[0], top_k=TOP_K, namespace=NS, include_metadata=True)
    text = "\n".join(f"{m['id']} ({m['score']:.2f}): {m['metadata']['text']}" for m in res["matches"])
    await msg.answer(text or "Ничего не найдено")

if __name__ == "__main__":
    print("Бот запущен. Ctrl+C — остановить.")
    asyncio.run(dp.start_polling(bot))
