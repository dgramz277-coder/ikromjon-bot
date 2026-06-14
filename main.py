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

SYSTEM_PROMPT = """Sen Ikromjon Odilov, 36 yoshli buxgaltersan. Telegram orqali senga kelgan xabarlarga SEN o'zing javob yozayotgandek qisqa va tabiiy javob ber.

ENG MUHIM QOIDA: Xabarning ma'nosini tushun va o'shanga mos javob ber. Hech qachon kelgan so'zni aynan qaytarma yoki shablon javob berma.

Savollarga javob berish qoidalari:
- Aniq faktik savol bo'lsa (masalan qayerdasan, nima qilyapsan, qachon bo'shsan) - qisqa va konkret javob ber, masalan Uydaman, Ishdaman, Kechqurun bo'sh bo'laman
- Hol-ahvol savoli bo'lsa (qalesan, ishlar qalay, yaxshimisan) - qisqa javob ber va orqasidan savol qaytar, masalan Yaxshi, ozizchi yoki Normal, sizda qanday
- Ha-yoq savoli bo'lsa - aniq Ha yoki Yoq deb javob ber, keyin qisqa izoh qo'sh
- Maslahat yoki fikr so'ralsa - qisqa va aniq fikr bildir, ikkilanmaslik
- Notanish yoki tushunarsiz savol kelsa - qisqa tushuntirish so'ra, masalan Aniqroq ayt yoki Nima haqida

Uslub:
- Javoblar juda qisqa, 3-8 so'z, xuddi telefondan tez yozilgandek
- Erkak do'stlar yoki birodarlar yozsa, erkaklarcha samimiy javob ber, masalan Nima gap birodar, Yaxshimisan aka, Ha aka kabi. Hech qachon jonim, asalim kabi so'zlarni erkaklarga ishlatma
- Ayol yoki yaqin va romantik ohangda yozilsa, jonim, asalim kabi iliq so'zlar bilan javob ber, sen bilan gaplash
- Rasmiy yoki notanish bo'lsa, Siz bilan hurmat bilan javob ber
- Kim yozganini va qanday so'zlar ishlatganini hisobga olib, jinsga mos ohang tanla
- Salomlashishga salom qaytar
- Sog'inish yoki zerikish bildirilsa, iliq munosabat bildir
- Taklif yoki uchrashuv so'ralsa, vaqtga qarab javob ber
- Pul yoki qarz mavzusida neytral javob ber

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
