import os
import requests
import pandas as pd
from io import StringIO
from datetime import datetime

# Bot tokeni va Telegram guruh ID
BOT_TOKEN = "1601071734:AAFG7H_l2vTbsi4SZ8TsnCI8Y_mKSibWdOc"
CHAT_ID = -1003719999075

# Google Jadval parametrlari
SPREADSHEET_ID = '1WgrobwCXOTSAcj0dcU8I4SziRIHHIu84FjBxe76RGkU'
GID = '1202843343'  # "qarzdorlik" varag'i
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={GID}"

EXCEL_FILE = 'qarzdorlik.xlsx'

def download_and_convert():
    print("Google Jadvaldan ma'lumotlar yuklab olinmoqda...")
    res = requests.get(CSV_URL, timeout=30)
    res.raise_for_status()

    # CSV ma'lumotlarini o'qib, Excel (.xlsx) ga yozish
    data = StringIO(res.text)
    df = pd.read_csv(data)

    with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='qarzdorlik', index=False)
    print("Excel fayl tayyorlandi.")

def send_to_telegram():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    today_str = datetime.now().strftime('%d.%m.%Y')
    caption_text = (
        f"📊 <b>Qarzdorlik bo'yicha hisobot</b>\n"
        f"🗓 Sana: <b>{today_str}</b>\n\n"
        f"<i>Google Jadvaldan avtomatik yuklab olindi.</i>"
    )

    print(f"Fayl guruhga ({CHAT_ID}) yuborilmoqda...")
    with open(EXCEL_FILE, 'rb') as doc:
        r = requests.post(
            url,
            data={
                'chat_id': CHAT_ID,
                'caption': caption_text,
                'parse_mode': 'HTML'
            },
            files={'document': doc},
            timeout=60
        )

    if r.status_code == 200:
        print("Fayl guruhga muvaffaqiyatli yetib bordi!")
    else:
        print(f"Xatolik yuz berdi: {r.status_code} - {r.text}")

def main():
    try:
        download_and_convert()
        send_to_telegram()
    except Exception as e:
        print(f"Jarayonda xatolik: {e}")
    finally:
        if os.path.exists(EXCEL_FILE):
            os.remove(EXCEL_FILE)

if __name__ == '__main__':
    main()
