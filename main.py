import os
import requests
from fastapi import FastAPI, Request

app = FastAPI()

TOKEN = os.environ["BOT_TOKEN"]
TELEGRAM_API = f"https://api.telegram.org/bot{TOKEN}"

REPLY = """سلام 👋
پیام شما دریافت شد. در اولین فرصت پاسخ خواهم داد."""

replied_users = set()


@app.get("/")
def home():
    return {"status": "running"}


@app.post("/telegram")
async def telegram_webhook(request: Request):

    update = await request.json()

    message = update.get("business_message")

    if not message:
        return {"ok": True}

    business_connection_id = message.get("business_connection_id")
    chat = message.get("chat")

    if not business_connection_id or not chat:
        return {"ok": True}

    chat_id = chat["id"]

    # اگر قبلاً به این شخص جواب داده‌ایم، دوباره جواب نده
    if chat_id in replied_users:
        return {"ok": True}

    data = {
        "business_connection_id": business_connection_id,
        "chat_id": chat_id,
        "text": REPLY
    }

    requests.post(
        f"{TELEGRAM_API}/sendMessage",
        json=data,
        timeout=10
    )

    replied_users.add(chat_id)

    return {"ok": True}
