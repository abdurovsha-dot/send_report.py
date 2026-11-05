import os
import asyncio
import requests
import pandas as pd
from io import StringIO
from datetime import datetime
from telethon import TelegramClient
from telethon.sessions import StringSession

# Sizning ma'lumotlaringiz
API_ID = 33493524
API_HASH = '764eff1c8982e79934f9d4a411e7630e'
# Probel va enterlarni avtomatik olib tashlaydi
raw_session = os.environ.get('SESSION_STRING', '')
SESSION_STRING = "".join(raw_session.split())

# Qabul qiluvchi shaxs
TARGET_USER = '@a1matov571'

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
    if not SESSION_STRING:
        print("XATOLIK: SESSION_STRING topilmadi!")
        return

    try:
        download_and_convert_to_excel()
    except Exception as e:
        print(f"Google Jadvalni yuklashda xatolik: {e}")
        return

    today_str = datetime.now().strftime('%d.%m.%Y')
    caption_text = (
        f"📊 <b>Qarzdorlik bo'yicha hisobot</b>\n"
        f"🗓 Sana: <b>{today_str}</b>\n\n"
        f"<i>Ushbu fayl avtomatik tarzda Google Jadvaldan olindi.</i>"
    )

    async with TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH) as client:
        try:
            print(f"Fayl yuborilmoqda: {TARGET_USER}")
            await client.send_file(
                TARGET_USER,
                EXCEL_FILE,
                caption=caption_text,
                parse_mode='html'
            )
            print("Fayl muvaffaqiyatli yuborildi!")
        except Exception as e:
            print(f"Yuborishda xatolik: {e}")
        finally:
            if os.path.exists(EXCEL_FILE):
                os.remove(EXCEL_FILE)

if __name__ == '__main__':
    asyncio.run(main())
