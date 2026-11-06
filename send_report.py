import os
import asyncio
import requests
import pandas as pd
from io import StringIO
from datetime import datetime
from telethon import TelegramClient
from telethon.sessions import StringSession

# GitHub Secrets'dan ma'lumotlarni olish
API_ID = int(os.environ.get('API_ID', 0))
API_HASH = os.environ.get('API_HASH', '').strip()
raw_session = os.environ.get('SESSION_STRING', '')
SESSION_STRING = "".join(raw_session.split())
TARGET_USER = os.environ.get('TARGET_USER', '').strip()

# Google Jadval parametrlari
SPREADSHEET_ID = '1WgrobwCXOTSAcj0dcU8I4SziRIHHIu84FjBxe76RGkU'
GID = '1202843343'  # "qarzdorlik" sahifasi
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={GID}"

EXCEL_FILE = 'qarzdorlik.xlsx'

def download_and_convert_to_excel():
    print("Google Jadvaldan ma'lumotlar yuklab olinmoqda...")
    response = requests.get(CSV_URL, timeout=30)
    response.raise_for_status()

    data = StringIO(response.text)
    df = pd.read_csv(data)

    with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='qarzdorlik', index=False)
    print(f"Jadval muvaffaqiyatli saqlandi: {EXCEL_FILE}")

async def main():
    if not API_ID or not API_HASH or not SESSION_STRING:
        print("XATOLIK: API_ID, API_HASH yoki SESSION_STRING topilmadi!")
        return

    if not TARGET_USER:
        print("XATOLIK: TARGET_USER topilmadi!")
        return

    # 1. Google Jadvaldan Excel fayl yasash
    try:
        download_and_convert_to_excel()
    except Exception as e:
        print(f"Google Jadvalni yuklashda xatolik: {e}")
        return

    # 2. Telegram orqali yuborish
    today_str = datetime.now().strftime('%d.%m.%Y')
    caption_text = (
        f"📊 <b>Qarzdorlik bo'yicha hisobot</b>\n"
        f"🗓 Sana: <b>{today_str}</b>\n\n"
        f"<i>Ushbu fayl avtomatik tarzda Google Jadvaldan olindi.</i>"
    )

    target = int(TARGET_USER) if TARGET_USER.lstrip('-').isdigit() else TARGET_USER

    try:
        async with TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH) as client:
            print(f"Fayl shaxsiy profildan yuborilmoqda: {target}")
            await client.send_file(
                target,
                EXCEL_FILE,
                caption=caption_text,
                parse_mode='html'
            )
            print("Fayl muvaffaqiyatli yuborildi!")
    except Exception as e:
        print(f"Yuborishda xatolik yuz berdi: {e}")

    # Vaqtinchalik faylni tozalash
    if os.path.exists(EXCEL_FILE):
        os.remove(EXCEL_FILE)

if __name__ == '__main__':
    asyncio.run(main())
