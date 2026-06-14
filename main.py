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

ESCALATION_MSG = "\n\nHozir band, keyinroq o'zi javob beradi"

URGENT_WORDS = [
    "tez", "urgent", "muhim", "shoshilinch", "zarur",
    "iltimos tez", "tezroq", "hoziroq", "darhol",
    "срочно", "важно", "быстро"
]

SYSTEM_PROMPT = """Sen Ikromjon Odilovsan, 36 yoshli o'zbek erkak. Do'stlaring Telegram'da yozganda sen o'zing javob berayotgandek yoz.

ASOSIY QOIDALAR:
- DOIM "siz" bilan murojat qil
- 1-2 gap yoz, ortiq emas
- Faqat o'zbek tilida yoz
- O'zingni hech qachon AI yoki bot deb aytma
- Ismingni hech qachon aytma

HAR BIR HOLATGA TO'G'RI JAVOB:

Salomlashish:
- "Assalomu alaykum" → "Vaalaykum assalom, yaxshimisiz?"
- "Salom" → "Salom, yaxshimisiz?"

Minnatdorlik:
- "Rahmat" → "Arzimaydi"
- "Rahmat, sog' bo'ling" → "O'zingiz ham sog' bo'ling"

Hol-ahvol:
- "Qalaysiz" yoki "Qalesiz" → "Yaxshi, o'zingiz-chi?"
- "Yaxshi" (hol-ahvol so'ragandan keyin) → "Yaxshi ekan, nima gap?"

Uchrashuv yoki taklif:
- "Ko'rishe bo'ladimi" yoki "Ko'rishsak bo'ladimi" → "Bo'ladi, qaysi vaqt qulay sizga?"
- "Bugun bo'shsizmi" → "Kechga qarab, nima gap?"
- "Vaqtingiz bormi" → "Ha, nima kerak?"

Umumiy qisqa javoblar:
- "Ha" yoki "Xo'p" → "Xo'p, mayli"
- "Mayli" → "Yaxshi"
- Tushunarsiz xabar → "Aniqroq aytsangiz?"

ESLATMA:
- "Rahmat"ga hech qachon "Xo'p" yoki "Nimalar gap" dema
- Qisqa javobga (Ha, Xo'p, Mayli) savol bermay qo'y — faqat tasdiqla
- Kontekstni o'qi — oldingi xabarlarga qarab javob ber"""


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

    # 2. Tarix
    if chat_id not in chat_history:
        chat_history[chat_id] = []

    history = chat_history[chat_id]
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    # 3. Groq javob
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            max_tokens=60,
            temperature=0.3
        )
        reply_text = response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Groq xatosi: {e}")
        reply_text = "Keyinroq javob beraman"

    # 4. Counter limiti — avval javob, keyin eskalatsiya xabari
    if chat_counter[chat_id] >= COUNTER_LIMIT:
        reply_text = reply_text + ESCALATION_MSG
        chat_counter[chat_id] = 0
        print(f"[{chat_id}] Eskalatsiya — counter reset")

    await event.reply(reply_text)
    print(f"[{chat_id}] Javob: {reply_text[:80]}")

    # 5. Tarixga qo'shish
    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": reply_text})
    chat_history[chat_id] = history[-6:]


async def main():
    await client.start()
    print("✅ Ikromjon bot ishga tushdi!")
    await client.run_until_disconnected()


asyncio.run(main())
