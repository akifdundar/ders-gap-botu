import requests
from telegram import Bot
import asyncio
import json
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
USER_ID = os.getenv("TELEGRAM_USER_ID")
URL = "https://obs.itu.edu.tr/public/DersProgram/DersProgramSearch?ProgramSeviyeTipiAnahtari=LS&dersBransKoduId=3&__RequestVerificationToken=CfDJ8GA9ZslBoIJKsvYzqTcEbYuJ_hC5ShuSU96rmHeK6tGeLViTQa4MD9OJRCjnlPvgMZS88WnC4yfwOFoEMLHNiha-q_0M7NC9FCw98pDn-4j0qrvH7z3CLrNDNKJUIfJ-agU3EBk62XMEh9t0FHvgkzg"

CRN_TO_CHECK = [""]

async def fetch_course_by_crn(crn):
    try:
        response = requests.get(URL) 
        response.raise_for_status() 

        data = response.json() 
        ders_program_list = data.get("dersProgramList", [])

        for ders in ders_program_list:
            if ders.get("crn") == crn:
                capacity = ders.get("kontenjan")
                enrolled = ders.get("ogrenciSayisi")

                if capacity is not None and enrolled is not None:  # Kontrol ekle
                    remaining = capacity - enrolled
                    return remaining > 0
                else:
                    print(f"CRN {crn} için kontenjan veya öğrenci sayısı bilgisi bulunamadı.")
                    return None

        return None 

    except requests.exceptions.RequestException as e:
        print(f"İstek hatası: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"JSON ayrıştırma hatası: {e}. Yanıt: {response.text}") #Yanıtı da yazdır
        return None
    except Exception as e:
        print(f"Beklenmedik bir hata oluştu: {e}")
        return None

async def send_message(bot, message):
    await bot.send_message(chat_id=USER_ID, text=message)

async def check_periodically():
    if not TOKEN:
        print("Please set TELEGRAM_BOT_TOKEN environment variable")
        return
    bot = Bot(token=TOKEN)
    while True:
        for crn in CRN_TO_CHECK:
            available = await fetch_course_by_crn(crn)
            if available:
                await send_message(bot, f"Gap available for CRN {crn}! Be quick!")
            await asyncio.sleep(1)

        await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(check_periodically())
