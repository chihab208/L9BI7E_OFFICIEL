from config import BOT_TOKEN, ADMIN_ID
import os

# تقدر تستعمل القيم هنا لاحقًا إذا حبيت تربطها
print(f"Running bot with token: {BOT_TOKEN}")
print(f"Admin ID: {ADMIN_ID}")

# تشغيل السورس الأصلي
os.system("python app.py")