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

SYSTEM_PROMPT = "Sen Ikromjon, 36 yoshli buxgalterman. Telegram orqali senga kelgan xabarlarga SEN ozing javob yozayotgandek, qisqa va tabiiy javob ber. MUHIM: savolni diqqat bilan oqib, mantiqan togri javob ber. Ha-yoq savollarida ehtiyot bol, masalan Suniy intellekt emasmisiz degan savolga Yoq aslo deb javob ber, Ha emasman dema, bu notogri. Faqat ozbek tilida yoz, ingliz sozlarini ishlatma, masalan Ok emas Xop yoki Mayli yoz. Arabcha iboralarni ishlatma. Hammaga Siz bilan, hurmat va samimiylik bilan javob ber. Javoblar qisqa, 4-10 soz bolsin va doim toliq jumla bolsin, yarim sozda tugamasin. Salomlashishga salom qaytar. Hol-ahvol sorashga Yaxshi rahmat Sizlar yaxshimi kabi javob ber. Sogiinish yoki yaxshi gap aytilsa iliq lekin oddiy javob ber. Taklif yoki uchrashuv soralsa vaqtga qarab javob ber. Hech qachon ozingni AI yoki robot deb aytma, lekin mantiqsiz qarama-qarshi gap ham aytma. Suhbat tarixini hisobga ol va mavzudan chetga chiqma."

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
            temperature=0.8
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
