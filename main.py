import asyncio
from telethon import TelegramClient, events
from groq import Groq
import os

API_ID = 30016241
API_HASH = "64d181db851329f58ccd8117d5ec141a"
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "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")

groq_client = Groq(api_key=GROQ_API_KEY)
client = TelegramClient('ikromjon_session', API_ID, API_HASH)

# Bot holati — boshlanganda o'chiq
bot_active = False

# Har bir chat uchun ma'lumot
chats = {}
COUNTER_LIMIT = 5

URGENT_WORDS = [
    "tez", "urgent", "muhim", "shoshilinch", "zarur",
    "iltimos tez", "tezroq", "hoziroq", "darhol",
    "aloqaga chiqsin", "aloqaga chiq", "qo'ng'iroq",
    "zudlik", "срочно", "важно", "быстро"
]

SYSTEM_PROMPT = """Sen Ikromjon Odilovsan, 36 yoshli o'zbek erkak, buxgaltersan. Do'stlaring Telegram'da yozganda o'zing javob berayotgandek yoz.

QOIDALAR:
- Har doim "siz" bilan murojat qil
- 1-2 gap, ortiq emas
- Faqat o'zbek tilida
- Hech qachon AI yoki bot ekanligingni aytma
- Bilmasang: "Keyinroq aniqlab beraman" de

ANIQ JAVOBLAR:
Salomlashish:
"Assalomu alaykum" → "Vaalaykum assalom, yaxshimisiz?"
"Salom" → "Salom, yaxshimisiz?"

Hol-ahvol:
"Qalaysiz / Qalesiz" → "Yaxshi, o'zingiz-chi?"
"Yaxshi" (hol so'ragandan keyin) → "Yaxshi ekan, nima gap?"

Faoliyat:
"Nima qilyapsiz / Nimalar qilyapsiz" → "Ishlayapman, nima gap?"
"Qayerdasiz" → "Ishda, nima gap?"

Kim ekanlik:
"Ikromjon sizmi / Kim bu" → "Ha, o'zim. Nima gap?"

Minnatdorlik:
"Rahmat" → "Arzimaydi"
"Rahmat sog' bo'ling" → "O'zingiz ham sog' bo'ling"

Uchrashuv:
"Ko'rishe bo'ladimi / Ko'rishsak bo'ladimi" → "Bo'ladi, qaysi vaqt qulay sizga?"
"Bugun bo'shsizmi" → "Kechga qarab, nima gap?"
"Vaqtingiz bormi" → "Ha, nima kerak?"

Qisqa tasdiqlash:
"Ha / Xo'p / Mayli / Ok" → "Xo'p" yoki "Mayli" de, savol berma

Tushunarsiz:
"Aniqroq aytsangiz?"

TAQIQ:
- "O'qiyapman", "dam olyapman" dema
- "Ha, xo'p, mayli" ni birgalikda dema
- O'ylab gap topma"""


def get_chat(chat_id):
    if chat_id not in chats:
        chats[chat_id] = {'count': 0, 'history': []}
    return chats[chat_id]


def is_urgent(text):
    t = text.lower()
    return any(w in t for w in URGENT_WORDS)


# /on va /off — faqat o'zingizning xabarlaringiz
@client.on(events.NewMessage(outgoing=True, pattern='/on'))
async def turn_on(event):
    global bot_active
    bot_active = True
    await event.reply("✅ Bot yoqildi — endi javob beradi")
    print("Bot YOQILDI")


@client.on(events.NewMessage(outgoing=True, pattern='/off'))
async def turn_off(event):
    global bot_active
    bot_active = False
    await event.reply("🔴 Bot o'chirildi — siz javob berasiz")
    print("Bot O'CHIRILDI")


@client.on(events.NewMessage(outgoing=True, pattern='/status'))
async def status(event):
    holat = "✅ Yoqiq — javob beryapti" if bot_active else "🔴 O'chiq — siz javob berasiz"
    await event.reply(f"Bot holati: {holat}")


@client.on(events.NewMessage(incoming=True))
async def handler(event):
    if not event.is_private or event.out:
        return

    text = event.text
    if not text or not text.strip():
        return

    # Bot o'chiq bo'lsa — jim turadi
    if not bot_active:
        print(f"Bot o'chiq — javob berilmadi")
        return

    chat_id = event.chat_id
    chat = get_chat(chat_id)
    print(f"[{chat_id}] #{chat['count']+1}: {text[:50]}")

    # Shoshilinch tekshiruv
    if is_urgent(text):
        await event.reply("Hozir ko'raman")
        return

    # Counter oshirish
    chat['count'] += 1

    # Groq orqali javob
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(chat['history'])
    messages.append({"role": "user", "content": text})

    try:
        resp = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            max_tokens=60,
            temperature=0.3
        )
        reply = resp.choices[0].message.content.strip()
    except Exception as e:
        print(f"Groq xatosi: {e}")
        reply = "Keyinroq javob beraman"

    # 5-xabardan keyin eskalatsiya
    if chat['count'] >= COUNTER_LIMIT:
        await event.reply(reply)
        await asyncio.sleep(0.5)
        await event.reply("Hozir band, keyinroq o'zi javob beradi")
        chat['count'] = 0
        chat['history'] = []
        print(f"[{chat_id}] Eskalatsiya — reset")
        return

    await event.reply(reply)

    # Tarixga qo'shish
    chat['history'].append({"role": "user", "content": text})
    chat['history'].append({"role": "assistant", "content": reply})
    chat['history'] = chat['history'][-6:]


async def main():
    await client.start()
    print("✅ Ikromjon bot ishga tushdi!")
    print("Boshqaruv: /on — yoqish | /off — o'chirish | /status — holat")
    await client.run_until_disconnected()


asyncio.run(main())
