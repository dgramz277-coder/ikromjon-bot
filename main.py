import asyncio
from telethon import TelegramClient, events
from groq import Groq
import os

API_ID = 30016241
API_HASH = "64d181db851329f58ccd8117d5ec141a"
GROQ_API_KEY = os.environ.get("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")

groq_client = Groq(api_key=GROQ_API_KEY)
client = TelegramClient('ikromjon_session', API_ID, API_HASH)

@client.on(events.NewMessage(incoming=True))
async def handler(event):
    print(f"XABAR KELDI: {event.text} | Private: {event.is_private}")
    if event.is_private:
        user_message = event.text
        print(f"XABAR KELDI: {user_message}")
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Sen Ikromjon Odilov, 36 yoshli buxgaltersan. Odamlar yozganda xuddi o'zing yozgandek qisqa javob ber. Misollar: 'Assalomu alaykum' kelsa -> 'Vaalaykum assalom!'; 'Salom' kelsa -> 'Salom!'; 'Qalesiz?' kelsa -> 'Yaxshi, o'zizchi?'; 'Nima gaplar?' kelsa -> 'Kompda ish, nima gap?'; 'Nimalar qilyapsiz?' kelsa -> 'Kompda ish'; 'Kechga vaqtingiz bormi?' kelsa -> 'Bugun iloji yo'q, o'zim tel qilaman'; 'Qachon ko'rishamiz?' kelsa -> 'O'zim tel qilaman'. Hech qachon robot kabi uzun javob berma. 1 jumladan oshirma."},
                {"role": "user", "content": user_message}
            ]
        )
        await event.reply(response.choices[0].message.content)

async def main():
    await client.start()
    print("Userbot ishga tushdi! ✅")
    await client.run_until_disconnected()

asyncio.run(main())
