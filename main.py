import asyncio
from telethon import TelegramClient, events
from groq import Groq
import os

API_ID = 30016241
API_HASH = "64d181db851329f58ccd8117d5ec141a"
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "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")

groq_client = Groq(api_key=GROQ_API_KEY)
client = TelegramClient('ikromjon_session', API_ID, API_HASH)

chat_history = {}
chat_counter = {}
COUNTER_LIMIT = 5

ESCALATION_MSG = "Hozir band, keyinroq o'zi javob beradi"

URGENT_WORDS = [
    "tez", "urgent", "muhim", "shoshilinch", "zarur",
    "iltimos tez", "tezroq", "hoziroq", "darhol",
    "срочно", "важно", "быстро"
]

SYSTEM_PROMPT = """Sen Ikromjon Odilov, 36 yoshli o'zbek erkaksan. Telegram'da do'stlaring senga yozganda, sen o'zing javob berayotgandek tabiiy va samimiy yoz.

MUHIM QOIDALAR:
1. DOIM "siz" bilan murojat qil — hech qachon "sen" dema
2. Qisqa yoz — 1 dan 3 gacha gap, ortiq emas
3. O'zbek tilida yoz, hech qachon boshqa tilda emas
4. Tabiiy so'zlar ishlat: "ha", "xo'p", "mayli", "bo'ladi", "ko'ramiz"
5. Gohida "..." ishlat — masalan "Keyinroq ko'ramiz..."
6. Hech qachon o'zingni AI yoki bot deb aytma
7. Bilmasang yoki noaniq bo'lsa: "Keyinroq aniqlab beraman" de
8. Suhbatni davom ettirishga harakat qil — gohida savol ham ber

SALOMLASHISH USLUBI:
- "Assalomu alaykum" → "Vaalaykum assalom, yaxshimisiz?"
- "Salom" → "Salom, yaxshimisiz?"
- "Qalaysiz" → "Yaxshi, o'zingiz-chi?"
- "Nima qilyapsiz" → "Ishlayman, nimalar gap?"

ROZI BO'LISH:
- "Xo'p, bo'ladi"
- "Ha, mayli"
- "Ko'ramiz"
- "Bo'ladi, keyinroq gaplashamiz"

BILMAGANINGDA:
- "Keyinroq aniqlab beraman"
- "Hozir aytolmayman, ko'ramiz"
- "Keyinroq gaplashamiz bu haqda"

ESLATMA: Hech qachon uzoq va rasmiy yozma. Ikromjon oddiy, samimiy, qisqa yozadi."""


def is_urgent(text: str) -> bool:
    text_lower = text.lower()
    return any(word in text_lower for word in URGENT_WORDS)


@client.on(events.NewMessage(incoming=True))
async def handler(event):
    if not event.is_private:
        return
    if event.out:
        return

    user_message = event.text
    if not user_message or not user_message.strip():
        return

    chat_id = event.chat_id

    # Counter yangilash
    if chat_id not in chat_counter:
        chat_counter[chat_id] = 0
    chat_counter[chat_id] += 1

    print(f"[{chat_id}] Xabar #{chat_counter[chat_id]}: {user_message[:50]}")

    # 1. Shoshilinch tekshiruv
    if is_urgent(user_message):
        await event.reply("Hozir ko'raman")
        print(f"[{chat_id}] SHOSHILINCH xabar")
        return

    # 2. Counter limiti
    if chat_counter[chat_id] >= COUNTER_LIMIT:
        await event.reply(ESCALATION_MSG)
        chat_counter[chat_id] = 0
        print(f"[{chat_id}] Eskalatsiya — counter reset")
        return

    # 3. Tarix
    if chat_id not in chat_history:
        chat_history[chat_id] = []

    history = chat_history[chat_id]
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    # 4. Groq javob
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            max_tokens=60,
            temperature=0.4
        )
        reply_text = response.choices[0].message.content
    except Exception as e:
        print(f"Groq xatosi: {e}")
        reply_text = "Keyinroq javob beraman"

    await event.reply(reply_text)
    print(f"[{chat_id}] Javob: {reply_text[:50]}")

    # 5. Tarixga qo'shish
    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": reply_text})
    chat_history[chat_id] = history[-6:]


async def main():
    await client.start()
    print("✅ Ikromjon bot ishga tushdi!")
    await client.run_until_disconnected()


asyncio.run(main())
