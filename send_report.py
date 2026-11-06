import os
import requests
import pandas as pd
from io import StringIO
from datetime import datetime

BOT_TOKEN = os.environ.get('BOT_TOKEN', '').strip()
CHAT_ID = os.environ.get('CHAT_ID', '').strip()

SPREADSHEET_ID = '1WgrobwCXOTSAcj0dcU8I4SziRIHHIu84FjBxe76RGkU'
GID = '1202843343'
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={GID}"
EXCEL_FILE = 'qarzdorlik.xlsx'

def main():
    if not BOT_TOKEN or not CHAT_ID:
        print("XATOLIK: BOT_TOKEN yoki CHAT_ID topilmadi!")
        return

    # 1. Google Jadvaldan yuklab, Excel ga aylantirish
    print("Google Jadvaldan ma'lumotlar yuklab olinmoqda...")
    res = requests.get(CSV_URL, timeout=30)
    res.raise_for_status()

    data = StringIO(res.text)
    df = pd.read_csv(data)

    with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='qarzdorlik', index=False)
    print("Excel fayl tayyorlandi.")

    # 2. Telegram Bot orqali yuborish
    today_str = datetime.now().strftime('%d.%m.%Y')
    caption_text = f"📊 Qarzdorlik bo'yicha hisobot ({today_str})"

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    print(f"Fayl yuborilmoqda: {CHAT_ID}...")

    with open(EXCEL_FILE, 'rb') as doc:
        response = requests.post(
            url,
            data={'chat_id': CHAT_ID, 'caption': caption_text},
            files={'document': doc}
        )

    if response.status_code == 200:
        print("Fayl muvaffaqiyatli yuborildi!")
    else:
        print(f"Yuborishda xatolik: {response.text}")

    if os.path.exists(EXCEL_FILE):
        os.remove(EXCEL_FILE)

if __name__ == '__main__':
    main()
