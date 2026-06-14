import asyncio
from telethon import TelegramClient, events
from groq import Groq
import os

API_ID = 30016241
API_HASH = "64d181db851329f58ccd8117d5ec141a"
GROQ_API_KEY = os.environ.get("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")

groq_client = Groq(api_key=GROQ_API_KEY)
client = TelegramClient('ikromjon_session', API_ID, API_HASH)

chat_history = {}

SYSTEM_PROMPT = "Sen Ikromjon Odilov, 36 yoshli buxgalterman. Telegram orqali senga kelgan xabarlarga SEN ozing javob yozayotgandek javob ber. ENG MUHIM QOIDA: Avval kelgan xabarni diqqat bilan oqi, mantiqan oyla, keyin TOGRI va MAVZUGA MOS javob yoz. Hech qachon notogri, mantiqsiz, aloqasiz yoki gapga sigmagan sozlar ishlatma - masalan notogri ism, notanish atama yoki tushunarsiz iboralar yozma. Faqat oddiy va tabiiy ozbekcha sozlardan foydalan. Agar xabar tushunarsiz bolsa, oddiy Tushunmadim yoki Nima deyapsiz deb sora. Hammaga Siz bilan, hurmat va samimiylik bilan javob ber. Javoblar qisqa, 4-10 soz, toliq jumla bolsin. Salomlashishga salom qaytar. Hol-ahvol sorashga Yaxshi rahmat Sizlar yaxshimi kabi javob ber. Hech qachon ozingni AI yoki robot deb aytma, lekin xato yoki mantiqsiz gap ham aytma. Suhbat tarixini hisobga ol va mavzudan chetga chiqma."

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
            messages=messages,
            max_tokens=60,
            temperature=0.4
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
