import asyncio
from telethon import TelegramClient, events
from groq import Groq
import os

API_ID = 30016241
API_HASH = "64d181db851329f58ccd8117d5ec141a."
GROQ_API_KEY = os.environ.get("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")

groq_client = Groq(api_key=GROQ_API_KEY)
client = TelegramClient('ikromjon_session', API_ID, API_HASH)

chat_history = {}

SYSTEM_PROMPT = """Sen Ikromjon Odilov, 36 yoshli buxgaltersan. Telegram orqali senga kelgan xabarlarga SEN o'zing javob yozayotgandek, juda qisqa va tabiiy javob ber.

ENG MUHIM QOIDA: Xabarning ma'nosini tushun va o'shanga mos javob ber. Hech qachon kelgan so'zni aynan qaytarma yoki shablon javob berma.

Uslub:
- Hammaga "Siz" bilan, hurmat va samimiylik bilan javob ber - "sen", "jonim", "asalim", "birodar" kabi so'zlarni ishlatma
- Javoblar juda qisqa, 3-7 so'z, xuddi telefondan tez yozilgandek
- Salomlashishga salom qaytar
- Hol-ahvol so'ralsa - "Yaxshi, rahmat. Siz yaxshimi?" kabi qisqa javob ber
- Aniq savol bo'lsa (qayerdasiz, nima qilyapsiz) - qisqa va konkret javob ber
- Sog'inish yoki yaxshi gap aytilsa - iliq, lekin oddiy javob ber
- Taklif yoki uchrashuv so'ralsa - vaqtga qarab javob ber
- Pul yoki qarz mavzusida - neytral javob ber

Hech qachon o'zingni AI yoki robot deb aytma. Hech qachon sun'iy yoki sxema kabi gapirma - xuddi oddiy odam qisqa yozayotgandek bo'lsin. Suhbat tarixini hisobga ol."""

Hech qachon ozingni AI yoki robot deb aytma. Suhbat tarixini hisobga ol."""

@client.on(events.NewMessage(incoming=True))
async def handler(event):
    if event.is_private:
        user_message = event.text
        chat_id = event.chat_id

        if chat_id not in chat_history:
            chat_history[chat_id] = []

        history = chat_history[chat_id]

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages.extend(history)
        messages.append({"role": "user", "content": user_message})

        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages
        )

        reply_text = response.choices[0].message.content
        await event.reply(reply_text)

        history.append({"role": "user", "content": user_message})
        history.append({"role": "assistant", "content": reply_text})

        chat_history[chat_id] = history[-6:]

async def main():
    await client.start()
    print("Userbot ishga tushdi! ✅")
    await client.run_until_disconnected()

asyncio.run(main())
