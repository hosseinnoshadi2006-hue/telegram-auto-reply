import os
import requests
from fastapi import FastAPI, Request

app = FastAPI()

TOKEN = os.environ["BOT_TOKEN"]
TELEGRAM_API = f"https://api.telegram.org/bot{TOKEN}"

CHANNEL = "@dentor_consultt"

REPLY = """دانش آموز عزیز سلام😍
از اینکه تیم ما رو انتخاب کردی سپاسگزاریم❤️
مطمئن باش پشیمون نمیشی😉

لطفا قبل از رزرو جلسه رایگان و دریافت برنامه ریزی شخصی خودتون، این لیست رو پر کن تا بتونیم بهتر بشناسیمت
🌱🌱🌱🌱🌱🌱🌱🌱
1⃣اسم
2⃣پایه
3⃣مدرسه + نوع مدرسه ( دولتی، غیردولتی، نمونه دولتی، استعداد درخشان )
4⃣شهر محل تحصیل و سکونت

5⃣رشته هدف
6⃣دلیل انتخاب این هدف

7⃣آخرین معدل
8⃣درس نقطه قوت و نقطه ضعف
9⃣رنج حدودی درصد ها و نمرات
🔟میانگین ساعت مطالعه و تعداد تستی که تا الان داشتین

1⃣1⃣سابقه داشتن مشاور
2⃣1⃣انتظارات از مشاور
3⃣1⃣چیز خاصی که فکر میکنی باید به مشاورت بگی
4⃣1⃣روحیات شخصی و مشکلات مطالعاتی
5⃣1⃣وضعیت والدین چطوره؟ پیگیری میکنن و اهمیت میدن؟

🟢از چه طریقی با ما آشنا شدین؟"""

JOIN_MESSAGE = """برای دریافت اطلاعات مشاوره و رزرو یک جلسه رایگان ، ابتدا عضو کانال ما شوید و سپس "مشاوره" رو ارسال کنید 👇"""


@app.get("/")
def home():
    return {"status": "running"}


def check_membership(user_id):
    response = requests.get(
        f"{TELEGRAM_API}/getChatMember",
        params={
            "chat_id": CHANNEL,
            "user_id": user_id
        },
        timeout=10
    )

    result = response.json()

    if not result.get("ok"):
        return False

    status = result["result"]["status"]

    return status in ["creator", "administrator", "member"]


def send_message(business_connection_id, chat_id, text, reply_markup=None):
    data = {
        "business_connection_id": business_connection_id,
        "chat_id": chat_id,
        "text": text
    }

    if reply_markup:
        data["reply_markup"] = reply_markup

    requests.post(
        f"{TELEGRAM_API}/sendMessage",
        json=data,
        timeout=10
    )


@app.post("/telegram")
async def telegram_webhook(request: Request):

    update = await request.json()

    message = update.get("business_message")

    if not message:
        return {"ok": True}

    business_connection_id = message.get("business_connection_id")
    chat = message.get("chat")
    text = message.get("text", "")

    if not business_connection_id or not chat:
        return {"ok": True}

    # فقط پیام‌هایی که «مشاوره» دارند
    if "مشاوره" not in text:
        return {"ok": True}

    chat_id = chat["id"]

    # بررسی عضویت شخص در کانال
    is_member = check_membership(chat_id)

    if not is_member:

        keyboard = {
            "inline_keyboard": [
                [
                    {
                        "text": "عضویت در کانال 📢",
                        "url": "https://t.me/dentor_consultt"
                    }
                ]
            ]
        }

        send_message(
            business_connection_id,
            chat_id,
            JOIN_MESSAGE,
            keyboard
        )

        return {"ok": True}

    # اگر عضو کانال بود
    send_message(
        business_connection_id,
        chat_id,
        REPLY
    )

    return {"ok": True}
