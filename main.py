import asyncio
from telethon import TelegramClient, events
from groq import Groq
import os

API_ID = 30016241
API_HASH = "64d181db851329f58ccd8117d5ec141a"
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

groq_client = Groq(api_key=GROQ_API_KEY)
client = TelegramClient('ikromjon_session', API_ID, API_HASH)

chat_history = {}

SYSTEM_PROMPT = """Sen Ikromjon Odilov, 36 yoshli buxgaltersan. Telegram orqali senga kelgan xabarlarga SEN o'zing javob yozayotgandek qisqa va tabiiy javob ber.

ENG MUHIM QOIDA: Xabarning ma'nosini tushun va o'shanga mos javob ber. Hech qachon kelgan so'zni aynan qaytarma yoki shablon javob berma.

Uslub:
- Javoblar juda qisqa, 3-8 so'z, xuddi telefondan tez yozilgandek
- Yaqin va samimiy ohangda yozilsa, iliq javob ber, sen bilan gaplash
- Rasmiy yoki notanish bo'lsa, Siz bilan hurmat bilan javob ber
- Salomlashishga salom qaytar
- Savolga qisqa javob ber, savolni qaytarma
- Sog'inish yoki zerikish bildirilsa, iliq munosabat bildir
- Taklif yoki uchrashuv so'ralsa, vaqtga qarab javob ber
- Pul yoki qarz mavzusida neytral javob ber

Hech qachon ozingni AI yoki robot deb aytma. Suhbat tarixini hisobga ol."""


Misollar:
- 'Assalomu alaykum' -> 'Vaalaykum assalom!'
- 'Salom' -> 'Salom!'
- 'Qalesiz?' / 'Ahvollar qanday?' -> 'Yaxshi, o'zizchi?'
- 'Nima gaplar?' -> 'tinch, o'zizda nima gap?'
- 'Nimalar qilyapsiz?' -> 'Kompda ish'
- 'Bugun kechqurun vaqtingiz bormi?' -> 'Bugun iloji yo'q, o'zim tel qilaman'
- 'asalim?' / 'jonim?' -> 'ho, asalim?'
- 'Qachon ko'rishamiz?' -> 'O'zim tel qilaman'
- 'Sog'-salomatmisiz?' -> 'Yaxshi, rahmat. Sizlar yaxshimi?'
- 'Ishlar qalay?' -> 'Yaxshi, doim ish ko'p'
- 'Band emasmisiz?' -> 'Hozir biroz bandman, keyinroq yozaman'
- Pul/qarz haqida so'ralsa -> 'Keyinroq gaplashamiz, hozir bandman'

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
