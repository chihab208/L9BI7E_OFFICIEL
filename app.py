import os
import sys
import json
import time
import shutil
import zipfile
import hashlib
import signal
import subprocess
import threading
from datetime import datetime, timedelta
from io import BytesIO

import requests
import psutil
import urllib3
from flask import (
    Flask, request, redirect, session, jsonify,
    render_template_string, send_from_directory, send_file, Response, abort
)

                                 
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

                                                                
BASE_DIR        = os.path.dirname(os.path.abspath(__file__))
LONELY_SOURCE   = os.path.join(BASE_DIR, 'xL9BI7E')
BOTS_STORAGE    = os.path.join(BASE_DIR, 'bots_storage')
USERS_STORAGE   = os.path.join(BOTS_STORAGE, 'users')
DATABASE_DIR    = os.path.join(BASE_DIR, 'database')

os.makedirs(LONELY_SOURCE, exist_ok=True)
os.makedirs(BOTS_STORAGE,  exist_ok=True)
os.makedirs(USERS_STORAGE, exist_ok=True)
os.makedirs(DATABASE_DIR,  exist_ok=True)

USERS_FILE   = os.path.join(DATABASE_DIR, 'users.json')
BOTS_FILE    = os.path.join(DATABASE_DIR, 'bots.json')
LINKS_FILE   = os.path.join(DATABASE_DIR, 'links.json')
PLAYERS_FILE = os.path.join(DATABASE_DIR, 'players.json')

VERIFY_API_URL = "https://api-jwt-alli-ff-v2.vercel.app/get"


from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

ENCRYPTION_KEY = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
ENCRYPTION_IV  = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])

def fs_encrypt_packet(plain_text, key=ENCRYPTION_KEY, iv=ENCRYPTION_IV):
    plain_text_bytes = bytes.fromhex(plain_text)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    cipher_text = cipher.encrypt(pad(plain_text_bytes, AES.block_size))
    return cipher_text.hex()

def fs_decrypt_packet(cipher_text, key=ENCRYPTION_KEY, iv=ENCRYPTION_IV):
    cipher_text_bytes = bytes.fromhex(cipher_text)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plain_text = unpad(cipher.decrypt(cipher_text_bytes), AES.block_size)
    return plain_text.hex()

def fs_Encrypt_ID(number):
    number = int(number)
    encoded_bytes = []
    while True:
        byte = number & 0x7F
        number >>= 7
        if number:
            byte |= 0x80
        encoded_bytes.append(byte)
        if not number:
            break
    return bytes(encoded_bytes).hex()

def fs_encrypt_api(plain_text):  return fs_encrypt_packet(plain_text)
def fs_decrypt_api(cipher_text): return fs_decrypt_packet(cipher_text)

def fs_TOKEN_MAKER(OLD_ACCESS_TOKEN, NEW_ACCESS_TOKEN, OLD_OPEN_ID, NEW_OPEN_ID, uid):
    data = bytes.fromhex(
        '1a13323032352d31312d32362030313a35313a3238220966726565206669726528013a07312e3132302e314232416e64726f6964204f532039202f204150492d3238202850492f72656c2e636a772e32303232303531382e313134313333294a0848616e6468656c64520c4d544e2f537061636574656c5a045749464960800a68d00572033234307a2d7838362d3634205353453320535345342e3120535345342e32204156582041565832207c2032343030207c20348001e61e8a010f416472656e6f2028544d292036343092010d4f70656e474c20455320332e329a012b476f6f676c657c36323566373136662d393161372d343935622d396631362d303866653964336336353333a2010e3137362e32382e3133392e313835aa01026172b201203433303632343537393364653836646134323561353263616164663231656564ba010134c2010848616e6468656c64ca010d4f6e65506c7573204135303130ea014063363961653230386661643732373338623637346232383437623530613361316466613235643161313966616537343566633736616334613065343134633934f00101ca020c4d544e2f537061636574656cd2020457494649ca03203161633462383065636630343738613434323033626638666163363132306635e003b5ee02e8039a8002f003af13f80384078004a78f028804b5ee029004a78f029804b5ee02b00404c80401d2043d2f646174612f6170702f636f6d2e6474732e667265656669726574682d66705843537068495636644b43376a4c2d574f7952413d3d2f6c69622f61726de00401ea045f65363261623933353464386662356662303831646233333861636233333439317c2f646174612f6170702f636f6d2e6474732e667265656669726574682d66705843537068495636644b43376a4c2d574f7952413d3d2f626173652e61706bf00406f804018a050233329a050a32303139313139303236a80503b205094f70656e474c455332b805ff01c00504e005be7eea05093372645f7061727479f205704b717348543857393347646347335a6f7a454e6646775648746d377171316552554e6149444e67526f626f7a4942744c4f695943633459367a767670634943787a514632734f453463627974774c7334785a62526e70524d706d5752514b6d654f35766373386e51594268777148374bf805e7e4068806019006019a060134a2060134b2062213521146500e590349510e460900115843395f005b510f685b560a6107576d0f0366'
    )
    data = data.replace(OLD_OPEN_ID.encode(),     NEW_OPEN_ID.encode())
    data = data.replace(OLD_ACCESS_TOKEN.encode(), NEW_ACCESS_TOKEN.encode())
    d = fs_encrypt_api(data.hex())
    Final_Payload = bytes.fromhex(d)

    headers = {
        "Host": "loginbp.ggpolarbear.com",
        "X-Unity-Version": "2018.4.11f1",
        "Accept": "*/*",
        "Authorization": "Bearer",
        "ReleaseVersion": "OB52",
        "X-GA": "v1 1",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
        "Content-Type": "application/x-www-form-urlencoded",
        "Content-Length": str(len(Final_Payload)),
        "User-Agent": "Free%20Fire/2019118692 CFNetwork/3826.500.111.2.2 Darwin/24.4.0",
        "Connection": "keep-alive"
    }
    URL = "https://loginbp.ggpolarbear.com/MajorLogin"
    RESPONSE = requests.post(URL, headers=headers, data=Final_Payload, verify=False)
    if RESPONSE.status_code == 200:
        if len(RESPONSE.text) < 10: return False
        BASE64_TOKEN = RESPONSE.text[RESPONSE.text.find("eyJhbGciOiJIUzI1NiIsInN2ciI6IjEiLCJ0eXAiOiJKV1QifQ"):-1]
        second_dot_index = BASE64_TOKEN.find(".", BASE64_TOKEN.find(".") + 1)
        BASE64_TOKEN = BASE64_TOKEN[:second_dot_index + 44]
        return BASE64_TOKEN
    print(f"MajorLogin failed with status: {RESPONSE.status_code}")
    return False

def fs_fetch_jwt_token_direct(uid, password):
    try:
        url = "https://100067.connect.garena.com/oauth/guest/token/grant"
        headers = {
            "Host": "100067.connect.garena.com",
            "User-Agent": "GarenaMSDK/4.0.19P4(G011A ;Android 9;en;US;)",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "close",
        }
        data = {
            "uid": f"{uid}", "password": f"{password}",
            "response_type": "token", "client_type": "2",
            "client_secret": "", "client_id": "100067",
        }
        response = requests.post(url, headers=headers, data=data, verify=False)
        print(f"📩 استجابة Garena API: {response.text}")
        data = response.json()
        if "access_token" not in data or "open_id" not in data:
            print(f"❌ مفاتيح مفقودة في الاستجابة: {data}"); return None
        NEW_ACCESS_TOKEN = data['access_token']
        NEW_OPEN_ID      = data['open_id']
        OLD_ACCESS_TOKEN = "c69ae208fad72738b674b2847b50a3a1dfa25d1a19fae745fc76ac4a0e414c94"
        OLD_OPEN_ID      = "4306245793de86da425a52caadf21eed"
        token = fs_TOKEN_MAKER(OLD_ACCESS_TOKEN, NEW_ACCESS_TOKEN, OLD_OPEN_ID, NEW_OPEN_ID, uid)
        if token:
            print(f"✅ تم توليد التوكن بنجاح: {token[:50]}...")
            return token
        print("❌ فشل توليد التوكن"); return None
    except Exception as e:
        print(f"⚠️ خطأ أثناء جلب التوكن مباشرة: {e}"); return None

def fs_get_player_info(uid):
    try:
        res = requests.get(f"http://5.175.178.221:6005/get?uid={uid}", timeout=10, verify=False)
        if res.status_code == 200:
            data = res.json()
            if "AccountInfo" in data:
                info = data["AccountInfo"]
                return (info.get("AccountName", "غير معروف"),
                        info.get("AccountRegion", "N/A"),
                        info.get("AccountLevel", "N/A"))
        return "غير معروف", "N/A", "N/A"
    except Exception as e:
        print(f"⚠️ Error fetching info for {uid}: {e}")
        return "غير معروف", "N/A", "N/A"

def fs_send_friend_request(token, player_id):
    enc_id = fs_Encrypt_ID(player_id)
    payload = f"08a7c4839f1e10{enc_id}1801"
    encrypted_payload = fs_encrypt_api(payload)
    url = "https://clientbp.ggblueshark.com/RequestAddingFriend"
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Unity-Version": "2018.4.11f1", "X-GA": "v1 1",
        "ReleaseVersion": "OB52",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Dalvik/2.1.0 (Linux; Android 9)",
        "Connection": "Keep-Alive", "Accept-Encoding": "gzip"
    }
    try:
        r = requests.post(url, headers=headers, data=bytes.fromhex(encrypted_payload), timeout=15, verify=False)
        if r.status_code == 200:
            if "BR_FRIEND_NOT_SAME_REGION" in r.text:
                return False, "لا يمكن إضافة اللاعب لأنه ليس في نفس منطقتك (السيرفر)"
            return True, "تم إرسال طلب الصداقة بنجاح!"
        if r.status_code == 400:
            if "BR_FRIEND_NOT_SAME_REGION" in r.text:
                return False, "لا يمكن إضافة اللاعب لأنه ليس في نفس منطقتك (السيرفر)"
            return False, "خطأ في الطلب - قد يكون اللاعب من منطقة مختلفة"
        if r.status_code == 401: return False, "التوكن غير صالح أو منتهي الصلاحية"
        if r.status_code == 404: return False, "اللاعب غير موجود أو خطأ في الاتصال بنقطة النهاية"
        return False, f"فشل إرسال الطلب. كود الخطأ: {r.status_code}"
    except Exception as e:
        return False, f"حدث خطأ أثناء إرسال الطلب: {str(e)}"

def fs_remove_friend(token, player_id):
    enc_id = fs_Encrypt_ID(player_id)
    payload = f"08a7c4839f1e10{enc_id}1802"
    encrypted_payload = fs_encrypt_api(payload)
    url = "https://clientbp.ggblueshark.com/RemoveFriend"
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Unity-Version": "2018.4.11f1", "X-GA": "v1 1",
        "ReleaseVersion": "OB52",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Dalvik/2.1.0 (Linux; Android 9)",
        "Connection": "Keep-Alive", "Accept-Encoding": "gzip"
    }
    try:
        r = requests.post(url, headers=headers, data=bytes.fromhex(encrypted_payload), timeout=15, verify=False)
        if r.status_code == 200: return True, "تم الحذف بنجاح!"
        if r.status_code == 401: return False, "التوكن غير صالح أو منتهي الصلاحية"
        if r.status_code == 400:
            server_error = r.text.strip()
            if server_error: return False, f"فشل الحذف. استجابة السيرفر: {server_error}"
            return False, "فشل الحذف. تحقق من الحمولة Protobuf"
        if r.status_code == 404: return False, "اللاعب غير موجود في قائمة الأصدقاء"
        return False, f"فشل الحذف. كود الخطأ: {r.status_code}"
    except Exception as e:
        return False, f"حدث خطأ أثناء الحذف: {str(e)}"
                                                                
                                                                
STATIC_CSS = "@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap');\n\n* {\n    margin: 0;\n    padding: 0;\n    box-sizing: border-box;\n    font-family: 'Cairo', sans-serif;\n}\n\n:root {\n    --primary: #00ff88;\n    --primary-dark: #00cc6a;\n    --secondary: #ff00aa;\n    --danger: #ff3366;\n    --warning: #ffaa00;\n    --success: #00ff88;\n    --dark: #0a0a0a;\n    --darker: #050505;\n    --card: #1a1a1a;\n    --card-hover: #222222;\n    --text: #ffffff;\n    --text-dim: #aaaaaa;\n    --border: #333333;\n}\n\nbody {\n    background: linear-gradient(135deg, var(--darker), var(--dark));\n    color: var(--text);\n    min-height: 100vh;\n    position: relative;\n}\n\nbody::before {\n    content: '';\n    position: fixed;\n    top: 0;\n    left: 0;\n    width: 100%;\n    height: 100%;\n    background: \n        radial-gradient(circle at 20% 30%, rgba(0, 255, 136, 0.03) 0%, transparent 50%),\n        radial-gradient(circle at 80% 70%, rgba(255, 0, 170, 0.03) 0%, transparent 50%);\n    pointer-events: none;\n    z-index: 0;\n}\n\n.container {\n    max-width: 1400px;\n    margin: 0 auto;\n    padding: 20px;\n    position: relative;\n    z-index: 1;\n}\n\n.sidebar {\n    position: fixed;\n    top: 20px;\n    right: 20px;\n    width: 60px;\n    background: var(--card);\n    border-radius: 30px;\n    padding: 15px 0;\n    border: 1px solid var(--border);\n    z-index: 1000;\n    transition: all 0.3s;\n    overflow: hidden;\n}\n\n.sidebar:hover {\n    width: 220px;\n    background: var(--card-hover);\n    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);\n}\n\n.sidebar .menu-item {\n    display: flex;\n    align-items: center;\n    padding: 12px 20px;\n    color: var(--text-dim);\n    text-decoration: none;\n    transition: all 0.3s;\n    white-space: nowrap;\n    position: relative;\n}\n\n.sidebar .menu-item i {\n    font-size: 24px;\n    margin-left: 15px;\n    width: 30px;\n    text-align: center;\n}\n\n.sidebar .menu-item span {\n    opacity: 0;\n    transition: opacity 0.3s;\n}\n\n.sidebar:hover .menu-item span {\n    opacity: 1;\n}\n\n.sidebar .menu-item:hover {\n    background: linear-gradient(90deg, transparent, rgba(0, 255, 136, 0.1));\n    color: var(--primary);\n}\n\n.sidebar .menu-item.active {\n    color: var(--primary);\n    border-right: 3px solid var(--primary);\n}\n\n.sidebar .divider {\n    height: 1px;\n    background: var(--border);\n    margin: 10px 0;\n}\n\n.sidebar-title {\n    color: #888;\n    font-size: 0.8rem;\n    padding: 10px 20px 5px;\n    text-transform: uppercase;\n    letter-spacing: 1px;\n    opacity: 0;\n    transition: opacity 0.3s;\n}\n\n.sidebar:hover .sidebar-title {\n    opacity: 1;\n}\n\n.menu-item.quick-link {\n    background: rgba(255, 255, 255, 0.03);\n    border-right: 2px solid transparent;\n}\n\n.menu-item.quick-link:hover {\n    background: rgba(0, 255, 136, 0.1);\n    border-right-color: var(--primary);\n}\n\n.menu-item.quick-link i {\n    color: var(--primary);\n}\n\n.floating-menu {\n    position: fixed;\n    top: 20px;\n    left: 20px;\n    background: var(--card);\n    border-radius: 50px;\n    padding: 10px;\n    border: 1px solid var(--border);\n    z-index: 1000;\n    display: flex;\n    gap: 10px;\n    box-shadow: 0 5px 20px rgba(0, 0, 0, 0.3);\n}\n\n.floating-menu button {\n    width: 50px;\n    height: 50px;\n    border-radius: 50%;\n    border: none;\n    background: var(--darker);\n    color: var(--primary);\n    font-size: 20px;\n    cursor: pointer;\n    transition: all 0.3s;\n}\n\n.floating-menu button:hover {\n    background: var(--primary);\n    color: var(--dark);\n    transform: scale(1.1);\n}\n\n.quick-links {\n    position: fixed;\n    bottom: 20px;\n    left: 20px;\n    display: flex;\n    flex-direction: column;\n    gap: 10px;\n    z-index: 1000;\n}\n\n.quick-link {\n    width: 50px;\n    height: 50px;\n    background: var(--card);\n    border-radius: 50%;\n    display: flex;\n    align-items: center;\n    justify-content: center;\n    color: var(--primary);\n    text-decoration: none;\n    font-size: 24px;\n    border: 1px solid var(--border);\n    transition: all 0.3s;\n    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);\n}\n\n.quick-link:hover {\n    transform: scale(1.1) translateX(-10px);\n    background: var(--primary);\n    color: var(--dark);\n    border-color: var(--primary);\n}\n\n.login-card {\n    background: var(--card);\n    border-radius: 30px;\n    padding: 40px;\n    max-width: 450px;\n    margin: 100px auto;\n    border: 1px solid var(--border);\n    text-align: center;\n    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5);\n}\n\n.login-card .logo i {\n    font-size: 60px;\n    color: var(--primary);\n    margin-bottom: 20px;\n}\n\n.login-card .logo h1 {\n    font-size: 3rem;\n    background: linear-gradient(135deg, var(--primary), var(--secondary));\n    -webkit-background-clip: text;\n    -webkit-text-fill-color: transparent;\n    margin-bottom: 10px;\n}\n\n.login-card .input-group {\n    text-align: right;\n    margin-bottom: 20px;\n}\n\n.login-card .input-group label {\n    display: block;\n    margin-bottom: 8px;\n    color: var(--text-dim);\n}\n\n.login-card .input-group input {\n    width: 100%;\n    padding: 15px;\n    background: var(--darker);\n    border: 2px solid var(--border);\n    border-radius: 12px;\n    color: var(--text);\n    transition: all 0.3s;\n}\n\n.login-card .input-group input:focus {\n    outline: none;\n    border-color: var(--primary);\n}\n\n.btn-login {\n    width: 100%;\n    padding: 15px;\n    background: linear-gradient(135deg, var(--primary), var(--secondary));\n    border: none;\n    border-radius: 12px;\n    color: var(--dark);\n    font-weight: 900;\n    font-size: 1.2rem;\n    cursor: pointer;\n    transition: all 0.3s;\n}\n\n.btn-login:hover {\n    transform: translateY(-2px);\n    box-shadow: 0 10px 30px rgba(0, 255, 136, 0.3);\n}\n\n.error {\n    background: rgba(255, 51, 102, 0.1);\n    border: 1px solid var(--danger);\n    color: var(--danger);\n    padding: 15px;\n    border-radius: 12px;\n    margin-bottom: 20px;\n}\n\n.footer-text {\n    margin-top: 30px;\n    color: var(--text-dim);\n}\n\n.welcome-section {\n    margin-bottom: 30px;\n    background: var(--card);\n    border-radius: 20px;\n    padding: 25px;\n    border: 1px solid var(--border);\n}\n\n.welcome-section h1 {\n    font-size: 2.5rem;\n    margin-bottom: 10px;\n    color: var(--primary);\n}\n\n.user-stats {\n    display: flex;\n    gap: 20px;\n    color: var(--text-dim);\n    flex-wrap: wrap;\n}\n\n.user-stats span i {\n    color: var(--primary);\n    margin-left: 5px;\n}\n\n.section-header {\n    display: flex;\n    justify-content: space-between;\n    align-items: center;\n    margin-bottom: 20px;\n}\n\n.section-header h2 {\n    color: var(--primary);\n    font-size: 1.8rem;\n}\n\n.section-header h2 i {\n    margin-left: 10px;\n}\n\n.btn-create {\n    background: linear-gradient(135deg, var(--primary), var(--secondary));\n    color: var(--dark);\n    padding: 12px 25px;\n    border-radius: 12px;\n    text-decoration: none;\n    font-weight: 900;\n    transition: all 0.3s;\n    border: none;\n    cursor: pointer;\n    display: inline-flex;\n    align-items: center;\n    gap: 8px;\n}\n\n.btn-create:hover {\n    transform: translateY(-2px);\n    box-shadow: 0 10px 30px rgba(0, 255, 136, 0.3);\n}\n\n.bots-grid {\n    display: grid;\n    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));\n    gap: 20px;\n}\n\n.bot-card {\n    background: var(--card);\n    border-radius: 25px;\n    padding: 25px;\n    border: 1px solid var(--border);\n    position: relative;\n    transition: all 0.3s;\n    cursor: pointer;\n}\n\n.bot-card:hover {\n    transform: translateY(-5px);\n    border-color: var(--primary);\n    box-shadow: 0 10px 30px rgba(0, 255, 136, 0.1);\n}\n\n.bot-card .status {\n    position: absolute;\n    top: 20px;\n    right: 20px;\n    width: 12px;\n    height: 12px;\n    border-radius: 50%;\n}\n\n.bot-card .status.running {\n    background: var(--success);\n    box-shadow: 0 0 20px var(--success);\n}\n\n.bot-card .status.stopped {\n    background: var(--danger);\n    box-shadow: 0 0 20px var(--danger);\n}\n\n.bot-card .bot-icon {\n    width: 60px;\n    height: 60px;\n    background: linear-gradient(135deg, var(--primary), var(--secondary));\n    border-radius: 20px;\n    display: flex;\n    align-items: center;\n    justify-content: center;\n    margin-bottom: 20px;\n    font-size: 30px;\n    color: var(--dark);\n}\n\n.bot-card h3 {\n    font-size: 1.5rem;\n    margin-bottom: 10px;\n    color: var(--primary);\n}\n\n.bot-card .bot-id {\n    color: var(--text-dim);\n    font-size: 0.9rem;\n    margin-bottom: 20px;\n    padding-bottom: 20px;\n    border-bottom: 1px solid var(--border);\n}\n\n.bot-card .bot-actions {\n    display: flex;\n    gap: 10px;\n}\n\n.btn-start, .btn-stop, .btn-restart, .btn-delete {\n    flex: 1;\n    padding: 10px;\n    border: none;\n    border-radius: 10px;\n    font-weight: 600;\n    cursor: pointer;\n    transition: all 0.3s;\n}\n\n.btn-start {\n    background: var(--success);\n    color: var(--dark);\n}\n\n.btn-stop {\n    background: var(--danger);\n    color: white;\n}\n\n.btn-restart {\n    background: var(--warning);\n    color: var(--dark);\n}\n\n.btn-delete {\n    background: transparent;\n    border: 1px solid var(--danger);\n    color: var(--danger);\n}\n\n.btn-start:hover, .btn-stop:hover, .btn-restart:hover, .btn-delete:hover {\n    transform: translateY(-2px);\n    filter: brightness(1.2);\n}\n\n.btn-delete:hover {\n    background: var(--danger);\n    color: white;\n}\n\n.empty-state {\n    text-align: center;\n    padding: 60px;\n    background: var(--card);\n    border-radius: 30px;\n    border: 1px solid var(--border);\n}\n\n.empty-state i {\n    font-size: 80px;\n    color: var(--text-dim);\n    margin-bottom: 20px;\n}\n\n.empty-state h3 {\n    color: var(--text-dim);\n    margin-bottom: 10px;\n}\n\n.empty-state p {\n    color: var(--text-dim);\n    margin-bottom: 20px;\n}\n\n.stats-grid {\n    display: grid;\n    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));\n    gap: 20px;\n    margin-bottom: 40px;\n}\n\n.stat-card {\n    background: var(--card);\n    border-radius: 20px;\n    padding: 25px;\n    border: 1px solid var(--border);\n    text-align: center;\n    transition: all 0.3s;\n}\n\n.stat-card:hover {\n    border-color: var(--primary);\n    box-shadow: 0 10px 30px rgba(0, 255, 136, 0.1);\n}\n\n.stat-card i {\n    font-size: 40px;\n    color: var(--primary);\n    margin-bottom: 10px;\n}\n\n.stat-value {\n    display: block;\n    font-size: 2.5rem;\n    font-weight: 900;\n    color: var(--primary);\n    margin-bottom: 5px;\n}\n\n.stat-label {\n    display: block;\n    color: var(--text-dim);\n    font-size: 0.9rem;\n}\n\n.users-table {\n    background: var(--card);\n    border-radius: 20px;\n    border: 1px solid var(--border);\n    overflow: hidden;\n    margin-bottom: 30px;\n}\n\n.users-table table {\n    width: 100%;\n    border-collapse: collapse;\n}\n\n.users-table thead {\n    background: linear-gradient(90deg, rgba(0, 255, 136, 0.1), rgba(255, 0, 170, 0.1));\n}\n\n.users-table th {\n    padding: 15px;\n    text-align: right;\n    color: var(--primary);\n    font-weight: 900;\n    border-bottom: 1px solid var(--border);\n}\n\n.users-table td {\n    padding: 15px;\n    border-bottom: 1px solid var(--border);\n    color: var(--text);\n}\n\n.users-table tbody tr:hover {\n    background: rgba(0, 255, 136, 0.05);\n}\n\n.users-table .expired {\n    color: var(--danger);\n}\n\n.btn-icon {\n    width: 35px;\n    height: 35px;\n    border-radius: 8px;\n    border: none;\n    background: rgba(0, 255, 136, 0.1);\n    color: var(--primary);\n    cursor: pointer;\n    transition: all 0.3s;\n    font-size: 14px;\n    margin: 0 2px;\n}\n\n.btn-icon:hover {\n    background: var(--primary);\n    color: var(--dark);\n}\n\n.links-grid {\n    display: grid;\n    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));\n    gap: 20px;\n}\n\n.link-card {\n    background: var(--card);\n    border-radius: 20px;\n    padding: 20px;\n    border: 1px solid var(--border);\n    display: flex;\n    align-items: center;\n    gap: 15px;\n    transition: all 0.3s;\n}\n\n.link-card:hover {\n    border-color: var(--primary);\n    box-shadow: 0 10px 30px rgba(0, 255, 136, 0.1);\n}\n\n.link-icon {\n    width: 50px;\n    height: 50px;\n    background: linear-gradient(135deg, var(--primary), var(--secondary));\n    border-radius: 15px;\n    display: flex;\n    align-items: center;\n    justify-content: center;\n    font-size: 24px;\n    color: var(--dark);\n}\n\n.link-info {\n    flex: 1;\n}\n\n.link-info h4 {\n    color: var(--primary);\n    margin-bottom: 5px;\n}\n\n.link-info p {\n    color: var(--text-dim);\n    font-size: 0.85rem;\n}\n\n.link-card.add-link {\n    justify-content: center;\n    flex-direction: column;\n    cursor: pointer;\n    background: rgba(0, 255, 136, 0.05);\n    border: 2px dashed var(--border);\n}\n\n.link-card.add-link:hover {\n    border-color: var(--primary);\n    background: rgba(0, 255, 136, 0.1);\n}\n\n.link-card.add-link i {\n    font-size: 30px;\n    color: var(--primary);\n    margin-bottom: 10px;\n}\n\n.modal {\n    display: none;\n    position: fixed;\n    top: 0;\n    left: 0;\n    width: 100%;\n    height: 100%;\n    background: rgba(0, 0, 0, 0.8);\n    z-index: 2000;\n    align-items: center;\n    justify-content: center;\n}\n\n.modal-content {\n    background: var(--card);\n    border-radius: 20px;\n    padding: 30px;\n    max-width: 500px;\n    width: 90%;\n    border: 1px solid var(--border);\n    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.8);\n}\n\n.modal-content h3 {\n    color: var(--primary);\n    margin-bottom: 20px;\n    font-size: 1.5rem;\n}\n\n.modal-content input {\n    width: 100%;\n    padding: 12px;\n    background: var(--darker);\n    border: 1px solid var(--border);\n    border-radius: 10px;\n    color: var(--text);\n    margin-bottom: 15px;\n    transition: all 0.3s;\n}\n\n.modal-content input:focus {\n    outline: none;\n    border-color: var(--primary);\n}\n\n.form-row {\n    display: grid;\n    grid-template-columns: 1fr 1fr;\n    gap: 15px;\n}\n\n.form-row input {\n    margin-bottom: 0;\n}\n\n.modal-note {\n    color: var(--text-dim);\n    font-size: 0.85rem;\n    margin-bottom: 15px;\n}\n\n.icon-hint {\n    background: rgba(0, 255, 136, 0.05);\n    border: 1px solid var(--border);\n    border-radius: 10px;\n    padding: 10px;\n    color: var(--text-dim);\n    font-size: 0.85rem;\n    margin-bottom: 15px;\n}\n\n.modal-buttons {\n    display: flex;\n    gap: 10px;\n    margin-top: 20px;\n}\n\n.btn-save, .btn-cancel {\n    flex: 1;\n    padding: 12px;\n    border: none;\n    border-radius: 10px;\n    font-weight: 600;\n    cursor: pointer;\n    transition: all 0.3s;\n}\n\n.btn-save {\n    background: linear-gradient(135deg, var(--primary), var(--secondary));\n    color: var(--dark);\n}\n\n.btn-cancel {\n    background: transparent;\n    border: 1px solid var(--border);\n    color: var(--text-dim);\n}\n\n.btn-save:hover {\n    transform: translateY(-2px);\n    box-shadow: 0 10px 30px rgba(0, 255, 136, 0.3);\n}\n\n.btn-cancel:hover {\n    border-color: var(--primary);\n    color: var(--primary);\n}\n\n.create-bot-card {\n    background: var(--card);\n    border-radius: 25px;\n    padding: 40px;\n    max-width: 600px;\n    margin: 50px auto;\n    border: 1px solid var(--border);\n}\n\n.create-bot-card h1 {\n    color: var(--primary);\n    margin-bottom: 30px;\n    font-size: 2rem;\n}\n\n.form-group {\n    margin-bottom: 20px;\n}\n\n.form-group label {\n    display: block;\n    color: var(--text-dim);\n    margin-bottom: 8px;\n    font-weight: 600;\n}\n\n.form-group input {\n    width: 100%;\n    padding: 12px;\n    background: var(--darker);\n    border: 1px solid var(--border);\n    border-radius: 10px;\n    color: var(--text);\n    transition: all 0.3s;\n}\n\n.form-group input:focus {\n    outline: none;\n    border-color: var(--primary);\n}\n\n.btn-submit {\n    width: 100%;\n    padding: 15px;\n    background: linear-gradient(135deg, var(--primary), var(--secondary));\n    border: none;\n    border-radius: 12px;\n    color: var(--dark);\n    font-weight: 900;\n    font-size: 1.1rem;\n    cursor: pointer;\n    transition: all 0.3s;\n}\n\n.btn-submit:hover {\n    transform: translateY(-2px);\n    box-shadow: 0 10px 30px rgba(0, 255, 136, 0.3);\n}\n\n.error-message {\n    background: rgba(255, 51, 102, 0.1);\n    border: 1px solid var(--danger);\n    color: var(--danger);\n    padding: 15px;\n    border-radius: 10px;\n}\n\n.success-message {\n    background: rgba(0, 255, 136, 0.1);\n    border: 1px solid var(--success);\n    color: var(--success);\n    padding: 15px;\n    border-radius: 10px;\n}\n\n.bot-details-card {\n    background: var(--card);\n    border-radius: 25px;\n    padding: 30px;\n    border: 1px solid var(--border);\n    margin-bottom: 30px;\n}\n\n.bot-header {\n    display: flex;\n    align-items: center;\n    gap: 20px;\n    margin-bottom: 30px;\n    padding-bottom: 20px;\n    border-bottom: 1px solid var(--border);\n}\n\n.bot-icon-large {\n    width: 80px;\n    height: 80px;\n    background: linear-gradient(135deg, var(--primary), var(--secondary));\n    border-radius: 20px;\n    display: flex;\n    align-items: center;\n    justify-content: center;\n    font-size: 40px;\n    color: var(--dark);\n}\n\n.bot-info h2 {\n    color: var(--primary);\n    margin-bottom: 10px;\n}\n\n.bot-status {\n    color: var(--text-dim);\n    font-size: 0.9rem;\n}\n\n.bot-status.running {\n    color: var(--success);\n}\n\n.bot-status.stopped {\n    color: var(--danger);\n}\n\n.config-section {\n    margin-bottom: 30px;\n}\n\n.config-section h3 {\n    color: var(--primary);\n    margin-bottom: 20px;\n    font-size: 1.3rem;\n}\n\n.config-item {\n    display: flex;\n    align-items: center;\n    justify-content: space-between;\n    padding: 15px;\n    background: rgba(0, 255, 136, 0.03);\n    border-radius: 10px;\n    margin-bottom: 10px;\n    border: 1px solid var(--border);\n}\n\n.config-item .label {\n    color: var(--text-dim);\n    font-weight: 600;\n    min-width: 120px;\n}\n\n.config-item .value {\n    color: var(--primary);\n    flex: 1;\n    margin: 0 15px;\n}\n\n.btn-edit {\n    background: transparent;\n    border: 1px solid var(--primary);\n    color: var(--primary);\n    padding: 8px 15px;\n    border-radius: 8px;\n    cursor: pointer;\n    transition: all 0.3s;\n    font-size: 0.9rem;\n}\n\n.btn-edit:hover {\n    background: var(--primary);\n    color: var(--dark);\n}\n\n.control-section {\n    display: flex;\n    gap: 10px;\n    margin-bottom: 30px;\n    flex-wrap: wrap;\n}\n\n.btn-control {\n    flex: 1;\n    min-width: 120px;\n    padding: 12px;\n    border: none;\n    border-radius: 10px;\n    font-weight: 600;\n    cursor: pointer;\n    transition: all 0.3s;\n}\n\n.btn-control.btn-start {\n    background: var(--success);\n    color: var(--dark);\n}\n\n.btn-control.btn-stop {\n    background: var(--danger);\n    color: white;\n}\n\n.btn-control.btn-restart {\n    background: var(--warning);\n    color: var(--dark);\n}\n\n.btn-control.btn-delete {\n    background: transparent;\n    border: 1px solid var(--danger);\n    color: var(--danger);\n}\n\n.btn-control:hover {\n    transform: translateY(-2px);\n    filter: brightness(1.2);\n}\n\n.players-section {\n    margin-top: 30px;\n}\n\n.players-section h3 {\n    color: var(--primary);\n    margin-bottom: 20px;\n    font-size: 1.3rem;\n}\n\n.add-player-form {\n    display: flex;\n    gap: 10px;\n    margin-bottom: 20px;\n}\n\n.add-player-form input {\n    flex: 1;\n    padding: 12px;\n    background: var(--darker);\n    border: 1px solid var(--border);\n    border-radius: 10px;\n    color: var(--text);\n}\n\n.add-player-form input:focus {\n    outline: none;\n    border-color: var(--primary);\n}\n\n.add-player-form button {\n    padding: 12px 25px;\n    background: linear-gradient(135deg, var(--primary), var(--secondary));\n    border: none;\n    border-radius: 10px;\n    color: var(--dark);\n    font-weight: 600;\n    cursor: pointer;\n    transition: all 0.3s;\n}\n\n.add-player-form button:hover {\n    transform: translateY(-2px);\n    box-shadow: 0 10px 30px rgba(0, 255, 136, 0.3);\n}\n\n.players-list {\n    display: grid;\n    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));\n    gap: 15px;\n}\n\n.player-card {\n    background: rgba(0, 255, 136, 0.05);\n    border: 1px solid var(--border);\n    border-radius: 10px;\n    padding: 15px;\n    transition: all 0.3s;\n}\n\n.player-card:hover {\n    border-color: var(--primary);\n    box-shadow: 0 5px 15px rgba(0, 255, 136, 0.1);\n}\n\n.player-card .player-name {\n    color: var(--primary);\n    font-weight: 600;\n    margin-bottom: 8px;\n}\n\n.player-card .player-info {\n    color: var(--text-dim);\n    font-size: 0.85rem;\n    margin-bottom: 5px;\n}\n\n.player-card .player-actions {\n    display: flex;\n    gap: 5px;\n    margin-top: 10px;\n}\n\n.player-card .player-actions button {\n    flex: 1;\n    padding: 6px;\n    background: transparent;\n    border: 1px solid var(--danger);\n    color: var(--danger);\n    border-radius: 6px;\n    cursor: pointer;\n    font-size: 0.8rem;\n    transition: all 0.3s;\n}\n\n.player-card .player-actions button:hover {\n    background: var(--danger);\n    color: white;\n}\n\n.back-link {\n    display: inline-flex;\n    align-items: center;\n    gap: 8px;\n    color: var(--primary);\n    text-decoration: none;\n    margin-bottom: 20px;\n    transition: all 0.3s;\n}\n\n.back-link:hover {\n    transform: translateX(5px);\n}\n\n@media (max-width: 768px) {\n    .sidebar {\n        width: 50px;\n    }\n\n    .floating-menu {\n        flex-wrap: wrap;\n        max-width: 200px;\n    }\n\n    .bots-grid {\n        grid-template-columns: 1fr;\n    }\n\n    .stats-grid {\n        grid-template-columns: repeat(2, 1fr);\n    }\n\n    .users-table table {\n        font-size: 0.9rem;\n    }\n\n    .users-table th, .users-table td {\n        padding: 10px;\n    }\n\n    .modal-content {\n        width: 95%;\n    }\n\n    .create-bot-card {\n        padding: 20px;\n    }\n\n    .bot-header {\n        flex-direction: column;\n        text-align: center;\n    }\n\n    .control-section {\n        flex-direction: column;\n    }\n\n    .btn-control {\n        min-width: auto;\n    }\n}\n"

STATIC_JS = 'document.addEventListener(\'DOMContentLoaded\', function() {\n    initializeTooltips();\n    updateTimers();\n    initializeAnimations();\n    initializeForms();\n    initializeModalClose();\n});\nfunction showAddUserModal() {\n    const modal = document.getElementById(\'addUserModal\');\n    if (modal) {\n        modal.style.display = \'flex\';\n        document.getElementById(\'new_username\').value = \'\';\n        document.getElementById(\'new_password\').value = \'\';\n        document.getElementById(\'new_telegram\').value = \'\';\n        document.getElementById(\'new_days\').value = \'30\';\n        document.getElementById(\'new_max_bots\').value = \'5\';\n    }\n}\nfunction showAddLinkModal() {\n    const modal = document.getElementById(\'addLinkModal\');\n    if (modal) {\n        modal.style.display = \'flex\';\n        document.getElementById(\'link_name\').value = \'\';\n        document.getElementById(\'link_url\').value = \'\';\n        document.getElementById(\'link_icon\').value = \'fas fa-link\';\n    }\n}\nfunction closeModal(id) {\n    const modal = document.getElementById(id);\n    if (modal) {\n        modal.style.display = \'none\';\n    }\n}\nfunction initializeModalClose() {\n    const modals = document.querySelectorAll(\'.modal\');\n    modals.forEach(modal => {\n        modal.addEventListener(\'click\', function(e) {\n            if (e.target === this) {\n                this.style.display = \'none\';\n            }\n        });\n    });\n}\nfunction createUser() {\n    const username = document.getElementById(\'new_username\')?.value;\n    const password = document.getElementById(\'new_password\')?.value;\n    const days = document.getElementById(\'new_days\')?.value;\n    const max_bots = document.getElementById(\'new_max_bots\')?.value;\n    const telegram = document.getElementById(\'new_telegram\')?.value || \'\';\n    if (!username || !password) {\n        showNotification(\'الرجاء إدخال اسم المستخدم وكلمة المرور\', \'error\');\n        return;\n    }\n    if (!days || parseInt(days) < 1) {\n        showNotification(\'الرجاء إدخال مدة صحيحة\', \'error\');\n        return;\n    }\n    if (!max_bots || parseInt(max_bots) < 1) {\n        showNotification(\'الرجاء إدخال عدد بوتات صحيح\', \'error\');\n        return;\n    }\n    const data = {\n        username: username,\n        password: password,\n        telegram: telegram,\n        days: parseInt(days),\n        max_bots: parseInt(max_bots)\n    };\n    fetch(\'/create_user\', {\n        method: \'POST\',\n        headers: {\'Content-Type\': \'application/json\'},\n        body: JSON.stringify(data)\n    })\n    .then(response => response.json())\n    .then(data => {\n        if (data.success) {\n            showNotification(\'✅ تم إنشاء المستخدم بنجاح\', \'success\');\n            setTimeout(() => location.reload(), 1000);\n        } else {\n            showNotification(\'❌ \' + (data.error || \'حدث خطأ\'), \'error\');\n        }\n    })\n    .catch(error => {\n        showNotification(\'❌ خطأ في الاتصال\', \'error\');\n        console.error(\'Error:\', error);\n    });\n}\nfunction createLink() {\n    const name = document.getElementById(\'link_name\')?.value;\n    const url = document.getElementById(\'link_url\')?.value;\n    let icon = document.getElementById(\'link_icon\')?.value || \'fas fa-link\';\n    if (!name || !url) {\n        showNotification(\'الرجاء إدخال اسم الرابط والرابط\', \'error\');\n        return;\n    }\n    try {\n        new URL(url);\n    } catch {\n        showNotification(\'الرجاء إدخال رابط صحيح (يبدأ بـ http:\n        return;\n    }\n    if (!icon.startsWith(\'fa\')) {\n        icon = \'fas fa-link\';\n    }\n    const data = {\n        name: name,\n        url: url,\n        icon: icon\n    };\n    fetch(\'/add_link\', {\n        method: \'POST\',\n        headers: {\'Content-Type\': \'application/json\'},\n        body: JSON.stringify(data)\n    })\n    .then(response => response.json())\n    .then(data => {\n        if (data.success) {\n            showNotification(\'✅ تم إضافة الرابط بنجاح\', \'success\');\n            setTimeout(() => location.reload(), 1000);\n        } else {\n            showNotification(\'❌ \' + (data.error || \'حدث خطأ\'), \'error\');\n        }\n    })\n    .catch(error => {\n        showNotification(\'❌ خطأ في الاتصال\', \'error\');\n        console.error(\'Error:\', error);\n    });\n}\nfunction deleteLink(id) {\n    if (!id) return;\n    if (confirm(\'هل أنت متأكد من حذف هذا الرابط؟\')) {\n        fetch(\'/delete_link/\' + id, {method: \'POST\'})\n        .then(response => response.json())\n        .then(data => {\n            if (data.success) {\n                showNotification(\'✅ تم حذف الرابط بنجاح\', \'success\');\n                setTimeout(() => location.reload(), 1000);\n            } else {\n                showNotification(\'❌ \' + (data.error || \'حدث خطأ\'), \'error\');\n            }\n        })\n        .catch(error => {\n            showNotification(\'❌ خطأ في الاتصال\', \'error\');\n            console.error(\'Error:\', error);\n        });\n    }\n}\nfunction viewUserBots(id) {\n    if (id) {\n        window.location.href = \'/admin/user/\' + id;\n    }\n}\nfunction editUser(id) {\n    showNotification(\'قريباً - تعديل المستخدم\', \'info\');\n}\nfunction deleteUser(id) {\n    if (!id) return;\n    if (confirm(\'⚠️ هل أنت متأكد من حذف هذا المستخدم نهائياً؟\\nسيتم حذف جميع بوتاته أيضاً!\')) {\n        fetch(\'/delete_user/\' + id, {method: \'POST\'})\n        .then(response => response.json())\n        .then(data => {\n            if (data.success) {\n                showNotification(\'✅ تم حذف المستخدم بنجاح\', \'success\');\n                setTimeout(() => location.reload(), 1000);\n            } else {\n                showNotification(\'❌ \' + (data.error || \'حدث خطأ\'), \'error\');\n            }\n        })\n        .catch(error => {\n            showNotification(\'❌ خطأ في الاتصال\', \'error\');\n            console.error(\'Error:\', error);\n        });\n    }\n}\nfunction controlBot(id, action) {\n    if (!id || !action) return;\n    const btn = event?.target;\n    if (btn) {\n        btn.disabled = true;\n        const originalText = btn.innerHTML;\n        btn.innerHTML = \'<i class="fas fa-spinner fa-spin"></i> جاري...\';\n    }\n    fetch(\'/bot_action\', {\n        method: \'POST\',\n        headers: {\'Content-Type\': \'application/json\'},\n        body: JSON.stringify({bot_id: id, action: action})\n    })\n    .then(response => response.json())\n    .then(data => {\n        if (data.success) {\n            showNotification(`✅ تم ${action === \'start\' ? \'تشغيل\' : action === \'stop\' ? \'إيقاف\' : \'إعادة تشغيل\'} البوت بنجاح`, \'success\');\n            setTimeout(() => location.reload(), 1000);\n        } else {\n            if (btn) {\n                btn.disabled = false;\n                btn.innerHTML = originalText;\n            }\n            showNotification(\'❌ \' + (data.error || \'حدث خطأ\'), \'error\');\n        }\n    })\n    .catch(error => {\n        if (btn) {\n            btn.disabled = false;\n            btn.innerHTML = originalText;\n        }\n        showNotification(\'❌ خطأ في الاتصال\', \'error\');\n        console.error(\'Error:\', error);\n    });\n}\nfunction deleteBot(id) {\n    if (!id) return;\n    if (confirm(\'⚠️ هل أنت متأكد من حذف هذا البوت نهائياً؟\')) {\n        fetch(\'/delete_bot/\' + id, {method: \'POST\'})\n        .then(response => response.json())\n        .then(data => {\n            if (data.success) {\n                showNotification(\'✅ تم حذف البوت بنجاح\', \'success\');\n                setTimeout(() => {\n                    if (window.location.pathname.includes(\'/bot/\')) {\n                        window.location.href = \'/dashboard\';\n                    } else {\n                        location.reload();\n                    }\n                }, 1000);\n            } else {\n                showNotification(\'❌ \' + (data.error || \'حدث خطأ\'), \'error\');\n            }\n        })\n        .catch(error => {\n            showNotification(\'❌ خطأ في الاتصال\', \'error\');\n            console.error(\'Error:\', error);\n        });\n    }\n}\nlet currentField = \'\';\nfunction editField(field) {\n    currentField = field;\n    const modal = document.getElementById(\'editModal\');\n    const title = document.getElementById(\'modalTitle\');\n    if (!modal || !title) return;\n    const titles = {\n        \'uid\': \'تعديل الأيدي\',\n        \'password\': \'تعديل كلمة المرور\',\n        \'bot_name\': \'تعديل اسم البوت\',\n        \'display_name\': \'تعديل الاسم المعروض\'\n    };\n    title.innerText = titles[field] || \'تعديل\';\n    modal.style.display = \'flex\';\n    document.getElementById(\'editValue\').value = \'\';\n}\nfunction saveEdit() {\n    const value = document.getElementById(\'editValue\')?.value;\n    if (!value) {\n        showNotification(\'الرجاء إدخال القيمة الجديدة\', \'error\');\n        return;\n    }\n    const botId = window.location.pathname.split(\'/\').pop();\n    const data = {};\n    data[currentField] = value;\n    fetch(\'/edit_bot/\' + botId, {\n        method: \'POST\',\n        headers: {\'Content-Type\': \'application/json\'},\n        body: JSON.stringify(data)\n    })\n    .then(response => response.json())\n    .then(data => {\n        if (data.success) {\n            showNotification(\'✅ تم التعديل بنجاح\', \'success\');\n            setTimeout(() => location.reload(), 1000);\n        } else {\n            showNotification(\'❌ \' + (data.error || \'حدث خطأ\'), \'error\');\n        }\n    })\n    .catch(error => {\n        showNotification(\'❌ خطأ في الاتصال\', \'error\');\n        console.error(\'Error:\', error);\n    });\n}\nfunction addPlayer() {\n    const uid = document.getElementById(\'player_uid\')?.value;\n    const duration = document.getElementById(\'duration\')?.value;\n    if (!uid || !duration) {\n        showNotification(\'الرجاء إدخال أيدي اللاعب والمدة\', \'error\');\n        return;\n    }\n    if (!duration.match(/^\\d+[dh]$/)) {\n        showNotification(\'صيغة خاطئة - استخدم مثلاً: 30d أو 24h\', \'error\');\n        return;\n    }\n    const botId = window.location.pathname.split(\'/\').pop();\n    fetch(\'/add_player\', {\n        method: \'POST\',\n        headers: {\'Content-Type\': \'application/json\'},\n        body: JSON.stringify({\n            bot_id: parseInt(botId),\n            player_uid: uid,\n            duration: duration\n        })\n    })\n    .then(response => response.json())\n    .then(data => {\n        if (data.success) {\n            showNotification(\'✅ تم إضافة اللاعب بنجاح\', \'success\');\n            setTimeout(() => location.reload(), 1000);\n        } else {\n            showNotification(\'❌ \' + (data.error || \'حدث خطأ\'), \'error\');\n        }\n    })\n    .catch(error => {\n        showNotification(\'❌ خطأ في الاتصال\', \'error\');\n        console.error(\'Error:\', error);\n    });\n}\nfunction removePlayer(id) {\n    if (!id) return;\n    if (confirm(\'هل أنت متأكد من حذف هذا اللاعب؟\')) {\n        fetch(\'/remove_player\', {\n            method: \'POST\',\n            headers: {\'Content-Type\': \'application/json\'},\n            body: JSON.stringify({player_id: id})\n        })\n        .then(response => response.json())\n        .then(data => {\n            if (data.success) {\n                showNotification(\'✅ تم حذف اللاعب بنجاح\', \'success\');\n                setTimeout(() => location.reload(), 1000);\n            } else {\n                showNotification(\'❌ \' + (data.error || \'حدث خطأ\'), \'error\');\n            }\n        })\n        .catch(error => {\n            showNotification(\'❌ خطأ في الاتصال\', \'error\');\n            console.error(\'Error:\', error);\n        });\n    }\n}\nfunction logout() {\n    if (confirm(\'تسجيل الخروج؟\')) {\n        window.location.href = \'/logout\';\n    }\n}\nfunction initializeTooltips() {\n    const tooltips = document.querySelectorAll(\'[title]\');\n    tooltips.forEach(el => {\n        el.addEventListener(\'mouseenter\', showTooltip);\n        el.addEventListener(\'mouseleave\', hideTooltip);\n    });\n}\nfunction showTooltip(e) {\n    const tooltip = document.createElement(\'div\');\n    tooltip.className = \'custom-tooltip\';\n    tooltip.textContent = e.target.title;\n    document.body.appendChild(tooltip);\n    const rect = e.target.getBoundingClientRect();\n    tooltip.style.top = rect.top - tooltip.offsetHeight - 10 + \'px\';\n    tooltip.style.left = rect.left + (rect.width - tooltip.offsetWidth) / 2 + \'px\';\n    e.target._tooltip = tooltip;\n}\nfunction hideTooltip(e) {\n    if (e.target._tooltip) {\n        e.target._tooltip.remove();\n        e.target._tooltip = null;\n    }\n}\nfunction updateTimers() {\n    const timers = document.querySelectorAll(\'.player-time\');\n    timers.forEach(timer => {\n        const expiry = timer.dataset.expiry;\n        if (expiry) {\n            updateTimer(timer, expiry);\n        }\n    });\n}\nfunction updateTimer(element, expiryDate) {\n    const expiry = new Date(expiryDate).getTime();\n    const now = new Date().getTime();\n    const distance = expiry - now;\n    if (distance < 0) {\n        element.innerHTML = \'<span style="color: var(--danger);">انتهت المدة</span>\';\n        return;\n    }\n    const days = Math.floor(distance / (1000 * 60 * 60 * 24));\n    const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));\n    const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));\n    const timeSpan = element.querySelector(\'span\');\n    if (timeSpan) {\n        timeSpan.textContent = `${days}d ${hours}h ${minutes}m`;\n    }\n}\nfunction initializeAnimations() {\n    const observer = new IntersectionObserver((entries) => {\n        entries.forEach(entry => {\n            if (entry.isIntersecting) {\n                entry.target.style.animation = \'slideIn 0.5s ease\';\n                observer.unobserve(entry.target);\n            }\n        });\n    }, { threshold: 0.1 });\n    document.querySelectorAll(\'.bot-card, .stat-card, .link-card\').forEach(el => {\n        observer.observe(el);\n    });\n}\nfunction initializeForms() {\n    const createBotForm = document.getElementById(\'createBotForm\');\n    if (createBotForm) {\n        createBotForm.addEventListener(\'submit\', handleCreateBot);\n    }\n}\nfunction handleCreateBot(e) {\n    e.preventDefault();\n    const btn = document.getElementById(\'submitBtn\');\n    const msg = document.getElementById(\'message\');\n    if (!btn || !msg) return;\n    btn.disabled = true;\n    btn.innerHTML = \'<i class="fas fa-spinner fa-spin"></i> جاري الإنشاء...\';\n    fetch(\'/create_bot\', {\n        method: \'POST\',\n        headers: {\'Content-Type\': \'application/json\'},\n        body: JSON.stringify({\n            uid: document.getElementById(\'uid\').value,\n            password: document.getElementById(\'password\').value,\n            bot_name: document.getElementById(\'bot_name\').value,\n            display_name: document.getElementById(\'display_name\').value\n        })\n    })\n    .then(response => response.json())\n    .then(data => {\n        if (data.success) {\n            msg.style.display = \'block\';\n            msg.className = \'success-message\';\n            msg.innerHTML = \'<i class="fas fa-check-circle"></i> تم إنشاء البوت بنجاح!\';\n            showNotification(\'✅ تم إنشاء البوت بنجاح\', \'success\');\n            setTimeout(() => window.location.href = \'/dashboard\', 2000);\n        } else {\n            btn.disabled = false;\n            btn.innerHTML = \'<i class="fas fa-plus"></i> إنشاء البوت\';\n            msg.style.display = \'block\';\n            msg.className = \'error-message\';\n            msg.innerHTML = \'<i class="fas fa-exclamation-circle"></i> \' + (data.error || \'حدث خطأ\');\n            showNotification(\'❌ \' + (data.error || \'حدث خطأ\'), \'error\');\n        }\n    })\n    .catch(error => {\n        btn.disabled = false;\n        btn.innerHTML = \'<i class="fas fa-plus"></i> إنشاء البوت\';\n        msg.style.display = \'block\';\n        msg.className = \'error-message\';\n        msg.innerHTML = \'<i class="fas fa-exclamation-circle"></i> خطأ في الاتصال\';\n        showNotification(\'❌ خطأ في الاتصال\', \'error\');\n        console.error(\'Error:\', error);\n    });\n}\nfunction showNotification(message, type = \'info\') {\n    const notification = document.createElement(\'div\');\n    notification.className = `notification notification-${type}`;\n    notification.innerHTML = `\n        <i class="fas ${type === \'success\' ? \'fa-check-circle\' : type === \'error\' ? \'fa-exclamation-circle\' : \'fa-info-circle\'}"></i>\n        <span>${message}</span>\n    `;\n    document.body.appendChild(notification);\n    setTimeout(() => {\n        notification.style.animation = \'slideOut 0.3s ease\';\n        setTimeout(() => notification.remove(), 300);\n    }, 3000);\n}\nfunction copyToClipboard(text) {\n    navigator.clipboard.writeText(text).then(() => {\n        showNotification(\'تم النسخ!\', \'success\');\n    }).catch(() => {\n        showNotification(\'فشل النسخ\', \'error\');\n    });\n}\nconst style = document.createElement(\'style\');\nstyle.textContent = `\n    @keyframes slideIn {\n        from {\n            opacity: 0;\n            transform: translateY(30px);\n        }\n        to {\n            opacity: 1;\n            transform: translateY(0);\n        }\n    }\n    @keyframes slideOut {\n        from {\n            opacity: 1;\n            transform: translateY(0);\n        }\n        to {\n            opacity: 0;\n            transform: translateY(-30px);\n        }\n    }\n    @keyframes pulse {\n        0%, 100% {\n            opacity: 1;\n        }\n        50% {\n            opacity: 0.5;\n        }\n    }\n    .custom-tooltip {\n        position: fixed;\n        background: var(--card);\n        color: var(--primary);\n        padding: 8px 15px;\n        border-radius: 8px;\n        font-size: 13px;\n        border: 1px solid var(--border);\n        z-index: 9999;\n        pointer-events: none;\n        animation: slideIn 0.2s ease;\n        box-shadow: 0 5px 20px rgba(0,0,0,0.3);\n    }\n    .notification {\n        position: fixed;\n        top: 20px;\n        left: 50%;\n        transform: translateX(-50%);\n        background: var(--card);\n        padding: 15px 30px;\n        border-radius: 50px;\n        border: 1px solid var(--border);\n        box-shadow: 0 10px 30px rgba(0,0,0,0.3);\n        z-index: 9999;\n        display: flex;\n        align-items: center;\n        gap: 10px;\n        animation: slideIn 0.3s ease;\n    }\n    .notification-success {\n        color: var(--success);\n        border-right: 4px solid var(--success);\n    }\n    .notification-error {\n        color: var(--danger);\n        border-right: 4px solid var(--danger);\n    }\n    .notification-info {\n        color: var(--primary);\n        border-right: 4px solid var(--primary);\n    }\n    .notification i {\n        font-size: 20px;\n    }\n    .status.running {\n        animation: pulse 2s infinite;\n    }\n    .fa-spinner {\n        animation: spin 1s linear infinite;\n    }\n    @keyframes spin {\n        from { transform: rotate(0deg); }\n        to { transform: rotate(360deg); }\n    }\n    button:disabled {\n        opacity: 0.6;\n        cursor: not-allowed;\n    }\n    .modal {\n        animation: fadeIn 0.3s ease;\n    }\n    @keyframes fadeIn {\n        from { opacity: 0; }\n        to { opacity: 1; }\n    }\n`;\ndocument.head.appendChild(style);'


TPL_LOGIN           = '<!DOCTYPE html>\n<html lang="ar" dir="rtl">\n<head>\n    <meta charset="UTF-8">\n    <meta name="viewport" content="width=510, initial-scale=1.0">\n    <title>PANELE BOT - تسجيل الدخول</title>\n    <link rel="stylesheet" href="/static/style.css">\n    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">\n</head>\n<body>\n    <div class="container">\n        <div class="login-card">\n            <div class="logo">\n                <i class="fas fa-robot"></i>\n                <h1>9SF TEAM</h1>\n                <p>نظام إدارة البوتات المتقدم</p>\n            </div>\n            \n            {% if error %}\n            <div class="error">\n                <i class="fas fa-exclamation-circle"></i> {{ error }}\n            </div>\n            {% endif %}\n            \n            <form action="/login" method="POST">\n                <div class="input-group">\n                    <label><i class="fas fa-user"></i> اسم المستخدم</label>\n                    <input type="text" name="username" placeholder="أدخل اسم المستخدم" required>\n                </div>\n                \n                <div class="input-group">\n                    <label><i class="fas fa-lock"></i> كلمة المرور</label>\n                    <input type="password" name="password" placeholder="أدخل كلمة المرور" required>\n                </div>\n                \n                <button type="submit" class="btn-login">\n                    <i class="fas fa-sign-in-alt"></i> تسجيل الدخول\n                </button>\n            </form>\n            \n            <div class="footer-text">\n                <i class="fas fa-crown"></i> المطور: @L3abassi1235 @ff_9SF_07\n            </div>\n        </div>\n    </div>\n</body>\n</html>\n'

TPL_DASHBOARD       = '<!DOCTYPE html>\n<html lang="ar" dir="rtl">\n<head>\n    <meta charset="UTF-8">\n    <meta name="viewport" content="width=510, initial-scale=1.0">\n    <title>PANELE BOT - لوحة التحكم</title>\n    <link rel="stylesheet" href="/static/style.css">\n    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">\n</head>\n<body>\n    <div class="sidebar">\n        <a href="/dashboard" class="menu-item active">\n            <i class="fas fa-home"></i>\n            <span>الرئيسية</span>\n        </a>\n        <a href="/create_bot" class="menu-item">\n            <i class="fas fa-plus-circle"></i>\n            <span>إنشاء بوت</span>\n        </a>\n        \n        {% if links %}\n        <div class="divider"></div>\n        <div class="sidebar-title">روابط سريعة</div>\n        {% for link in links %}\n        <a href="{{ link.url }}" target="_blank" class="menu-item quick-link" title="{{ link.name }}">\n            <i class="{{ link.icon }}"></i>\n            <span>{{ link.name }}</span>\n        </a>\n        {% endfor %}\n        {% endif %}\n        \n        <div class="divider"></div>\n        <a href="#" class="menu-item" onclick="logout()">\n            <i class="fas fa-sign-out-alt"></i>\n            <span>تسجيل الخروج</span>\n        </a>\n    </div>\n\n    {% if links %}\n    <div class="quick-links">\n        {% for link in links %}\n        <a href="{{ link.url }}" target="_blank" class="quick-link" title="{{ link.name }}">\n            <i class="{{ link.icon }}"></i>\n        </a>\n        {% endfor %}\n    </div>\n    {% endif %}\n\n    <div class="container">\n        <div class="welcome-section">\n            <h1>مرحباً {{ user.username }}</h1>\n            <div class="user-stats">\n                <span><i class="fas fa-robot"></i> البوتات: {{ bots|length }}/{{ user.max_bots }}</span>\n                <span><i class="fas fa-calendar"></i> تنتهي في: {{ user.expiry_date[:10] }}</span>\n            </div>\n        </div>\n\n        <div class="section-header">\n            <h2><i class="fas fa-robot"></i> البوتات الخاصة بك</h2>\n            <a href="/create_bot" class="btn-create">\n                <i class="fas fa-plus"></i> بوت جديد\n            </a>\n        </div>\n\n        {% if bots %}\n        <div class="bots-grid">\n            {% for bot in bots %}\n            <div class="bot-card" onclick="window.location.href=\'/bot/{{ bot.id }}\'">\n                <div class="status {{ bot.status }}"></div>\n                <div class="bot-icon">\n                    <i class="fas fa-robot"></i>\n                </div>\n                <h3>{{ bot.display_name }}</h3>\n                <div class="bot-id">{{ bot.uid }}</div>\n                <div class="bot-actions" onclick="event.stopPropagation()">\n                    {% if bot.status == \'running\' %}\n                    <button class="btn-stop" onclick="controlBot({{ bot.id }}, \'stop\')">\n                        <i class="fas fa-stop"></i> إيقاف\n                    </button>\n                    {% else %}\n                    <button class="btn-start" onclick="controlBot({{ bot.id }}, \'start\')">\n                        <i class="fas fa-play"></i> تشغيل\n                    </button>\n                    {% endif %}\n                </div>\n            </div>\n            {% endfor %}\n        </div>\n        {% else %}\n        <div class="empty-state">\n            <i class="fas fa-robot"></i>\n            <h3>لا يوجد بوتات</h3>\n            <p>أنشئ أول بوت الآن</p>\n            <a href="/create_bot" class="btn-create">إنشاء بوت</a>\n        </div>\n        {% endif %}\n    </div>\n\n    <script src="/static/scripts.js"></script>\n    <script>\n        function logout() {\n            if(confirm(\'تسجيل الخروج؟\')) {\n                window.location.href = \'/logout\';\n            }\n        }\n        \n        function controlBot(id, action) {\n            const btn = event.target;\n            btn.disabled = true;\n            const originalText = btn.innerHTML;\n            btn.innerHTML = \'<i class="fas fa-spinner fa-spin"></i> جاري...\';\n            \n            fetch(\'/bot_action\', {\n                method: \'POST\',\n                headers: {\'Content-Type\': \'application/json\'},\n                body: JSON.stringify({bot_id: id, action: action})\n            })\n            .then(r => r.json())\n            .then(d => { \n                if(d.success) {\n                    location.reload();\n                } else {\n                    btn.disabled = false;\n                    btn.innerHTML = originalText;\n                    alert(\'خطأ: \' + d.error);\n                }\n            })\n            .catch(() => {\n                btn.disabled = false;\n                btn.innerHTML = originalText;\n                alert(\'حدث خطأ في الاتصال\');\n            });\n        }\n    </script>\n</body>\n</html>\n'

TPL_CREATE_BOT      = '<!DOCTYPE html>\n<html lang="ar" dir="rtl">\n<head>\n    <meta charset="UTF-8">\n    <meta name="viewport" content="width=510, initial-scale=1.0">\n    <title>PANELE BOT - إنشاء بوت جديد</title>\n    <link rel="stylesheet" href="/static/style.css">\n    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">\n</head>\n<body>\n    <div class="sidebar">\n        <a href="/dashboard" class="menu-item">\n            <i class="fas fa-home"></i>\n            <span>الرئيسية</span>\n        </a>\n        <a href="/create_bot" class="menu-item active">\n            <i class="fas fa-plus-circle"></i>\n            <span>إنشاء بوت</span>\n        </a>\n        <div class="divider"></div>\n        <a href="#" class="menu-item" onclick="logout()">\n            <i class="fas fa-sign-out-alt"></i>\n            <span>تسجيل الخروج</span>\n        </a>\n    </div>\n\n    <div class="container">\n        <div class="create-bot-card">\n            <h1><i class="fas fa-plus-circle"></i> إنشاء بوت جديد</h1>\n            \n            <form id="createBotForm">\n                <div class="form-group">\n                    <label><i class="fas fa-id-card"></i> أيدي الحساب (UID)</label>\n                    <input type="text" id="uid" placeholder="مثال: 4408991023" required>\n                </div>\n                \n                <div class="form-group">\n                    <label><i class="fas fa-lock"></i> كلمة المرور</label>\n                    <input type="text" id="password" placeholder="كلمة المرور" required>\n                </div>\n                \n                <div class="form-group">\n                    <label><i class="fas fa-tag"></i> اسم البوت</label>\n                    <input type="text" id="bot_name" placeholder="مثال: SARGO" required>\n                </div>\n                \n                <div class="form-group">\n                    <label><i class="fas fa-font"></i> الاسم المعروض</label>\n                    <input type="text" id="display_name" placeholder="مثال: SARGO" required>\n                </div>\n                \n                <button type="submit" class="btn-submit" id="submitBtn">\n                    <i class="fas fa-plus"></i> إنشاء البوت\n                </button>\n            </form>\n            \n            <div id="message" style="display: none; margin-top: 20px; padding: 15px; border-radius: 10px;"></div>\n        </div>\n    </div>\n\n    <script>\n        function logout() {\n            if(confirm(\'تسجيل الخروج؟\')) window.location.href = \'/logout\';\n        }\n\n        document.getElementById(\'createBotForm\').addEventListener(\'submit\', function(e) {\n            e.preventDefault();\n            \n            const btn = document.getElementById(\'submitBtn\');\n            const msg = document.getElementById(\'message\');\n            const uid = document.getElementById(\'uid\').value;\n            const password = document.getElementById(\'password\').value;\n            \n            btn.disabled = true;\n            btn.innerHTML = \'<i class="fas fa-spinner fa-spin"></i> جاري التحقق من الحساب...\';\n            msg.style.display = \'none\';\n            \n            fetch(\'/verify_account\', {\n                method: \'POST\',\n                headers: {\'Content-Type\': \'application/json\'},\n                body: JSON.stringify({uid: uid, password: password})\n            })\n            .then(r => r.json())\n            .then(verifyData => {\n                if(!verifyData.success) {\n                    btn.disabled = false;\n                    btn.innerHTML = \'<i class="fas fa-plus"></i> إنشاء البوت\';\n                    msg.style.display = \'block\';\n                    msg.className = \'error-message\';\n                    msg.innerHTML = \'<i class="fas fa-exclamation-circle"></i> \' + verifyData.message;\n                    return;\n                }\n                \n                btn.innerHTML = \'<i class="fas fa-spinner fa-spin"></i> جاري إنشاء البوت...\';\n                \n                fetch(\'/create_bot\', {\n                    method: \'POST\',\n                    headers: {\'Content-Type\': \'application/json\'},\n                    body: JSON.stringify({\n                        uid: uid,\n                        password: password,\n                        bot_name: document.getElementById(\'bot_name\').value,\n                        display_name: document.getElementById(\'display_name\').value\n                    })\n                })\n                .then(r => r.json())\n                .then(d => {\n                    if(d.success) {\n                        msg.style.display = \'block\';\n                        msg.className = \'success-message\';\n                        msg.innerHTML = \'<i class="fas fa-check-circle"></i> تم إنشاء البوت بنجاح!\';\n                        setTimeout(() => window.location.href = \'/dashboard\', 2000);\n                    } else {\n                        btn.disabled = false;\n                        btn.innerHTML = \'<i class="fas fa-plus"></i> إنشاء البوت\';\n                        msg.style.display = \'block\';\n                        msg.className = \'error-message\';\n                        msg.innerHTML = \'<i class="fas fa-exclamation-circle"></i> \' + d.error;\n                    }\n                });\n            })\n            .catch(error => {\n                btn.disabled = false;\n                btn.innerHTML = \'<i class="fas fa-plus"></i> إنشاء البوت\';\n                msg.style.display = \'block\';\n                msg.className = \'error-message\';\n                msg.innerHTML = \'<i class="fas fa-exclamation-circle"></i> خطأ في الاتصال\';\n                console.error(\'Error:\', error);\n            });\n        });\n    </script>\n</body>\n</html>\n'

TPL_BOT_DETAILS     = '<!DOCTYPE html>\n<html lang="ar" dir="rtl">\n<head>\n    <meta charset="UTF-8">\n    <meta name="viewport" content="width=510, initial-scale=1.0">\n    <title>PANELE BOT - تفاصيل البوت</title>\n    <link rel="stylesheet" href="/static/style.css">\n    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">\n</head>\n<body>\n    <div class="sidebar">\n        <a href="{% if session.get(\'is_admin\') %}/admin/user/{{ bot.user_id }}{% else %}/dashboard{% endif %}" class="menu-item">\n            <i class="fas fa-arrow-right"></i>\n            <span>العودة</span>\n        </a>\n        <div class="divider"></div>\n        <a href="#" class="menu-item" onclick="logout()">\n            <i class="fas fa-sign-out-alt"></i>\n            <span>تسجيل الخروج</span>\n        </a>\n    </div>\n\n    <div class="container">\n        <a href="{% if session.get(\'is_admin\') %}/admin/user/{{ bot.user_id }}{% else %}/dashboard{% endif %}" class="back-link">\n            <i class="fas fa-arrow-right"></i> العودة\n        </a>\n\n        <div class="bot-details-card">\n            <div class="bot-header">\n                <div class="bot-icon-large">\n                    <i class="fas fa-robot"></i>\n                </div>\n                <div class="bot-info">\n                    <h2>{{ bot.display_name }}</h2>\n                    <p class="bot-status {{ bot.status }}">\n                        <i class="fas fa-circle"></i>\n                        {{ \'يعمل\' if bot.status == \'running\' else \'متوقف\' }}\n                    </p>\n                </div>\n            </div>\n\n            <div class="config-section">\n                <h3><i class="fas fa-cog"></i> الإعدادات</h3>\n                \n                <div class="config-item">\n                    <span class="label">الأيدي (UID):</span>\n                    <span class="value" id="uid_val">{{ bot.uid }}</span>\n                    <button class="btn-edit" onclick="editField(\'uid\')">\n                        <i class="fas fa-edit"></i> تعديل\n                    </button>\n                </div>\n                \n                <div class="config-item">\n                    <span class="label">كلمة المرور:</span>\n                    <span class="value" id="pass_val">••••••••</span>\n                    <button class="btn-edit" onclick="editField(\'password\')">\n                        <i class="fas fa-edit"></i> تعديل\n                    </button>\n                </div>\n                \n                <div class="config-item">\n                    <span class="label">اسم البوت:</span>\n                    <span class="value" id="name_val">{{ bot.name }}</span>\n                    <button class="btn-edit" onclick="editField(\'bot_name\')">\n                        <i class="fas fa-edit"></i> تعديل\n                    </button>\n                </div>\n                \n                <div class="config-item">\n                    <span class="label">الاسم المعروض:</span>\n                    <span class="value" id="display_val">{{ bot.display_name }}</span>\n                    <button class="btn-edit" onclick="editField(\'display_name\')">\n                        <i class="fas fa-edit"></i> تعديل\n                    </button>\n                </div>\n            </div>\n\n            <div class="control-section">\n                {% if bot.status == \'running\' %}\n                <button class="btn-control btn-stop" onclick="controlBot(\'stop\')">\n                    <i class="fas fa-stop"></i> إيقاف\n                </button>\n                <button class="btn-control btn-restart" onclick="controlBot(\'restart\')">\n                    <i class="fas fa-sync-alt"></i> إعادة تشغيل\n                </button>\n                {% else %}\n                <button class="btn-control btn-start" onclick="controlBot(\'start\')">\n                    <i class="fas fa-play"></i> تشغيل\n                </button>\n                {% endif %}\n                <button class="btn-control btn-delete" onclick="deleteBot()">\n                    <i class="fas fa-trash"></i> حذف البوت\n                </button>\n            </div>\n\n            <div class="players-section">\n                <h3><i class="fas fa-users"></i> اللاعبين المضافين</h3>\n                \n                <div class="add-player-form">\n                    <input type="text" id="player_uid" placeholder="أيدي اللاعب">\n                    <input type="text" id="duration" placeholder="المدة (1d أو 24h)">\n                    <button onclick="addPlayer()">\n                        <i class="fas fa-plus"></i> إضافة\n                    </button>\n                </div>\n\n                <div id="players_list">\n                    {% for player in players %}\n                    <div class="player-item" id="player_{{ player.id }}">\n                        <div class="player-info">\n                            <strong>{{ player.name }}</strong>\n                            <span>{{ player.uid }}</span>\n                            <small>المستوى: {{ player.level }} | المنطقة: {{ player.region }}</small>\n                        </div>\n                        <div class="player-time">\n                            <span>{{ player.remaining_days }}d {{ player.remaining_hours }}h</span>\n                            <button onclick="removePlayer({{ player.id }})" title="حذف الصديق">\n                                <i class="fas fa-user-minus"></i>\n                            </button>\n                        </div>\n                    </div>\n                    {% endfor %}\n                </div>\n            </div>\n        </div>\n    </div>\n\n    <div class="modal" id="editModal">\n        <div class="modal-content">\n            <h3 id="modalTitle">تعديل</h3>\n            <input type="text" id="editValue" placeholder="القيمة الجديدة">\n            <div class="modal-buttons">\n                <button onclick="saveEdit()" class="btn-save">حفظ</button>\n                <button onclick="closeModal()" class="btn-cancel">إلغاء</button>\n            </div>\n        </div>\n    </div>\n\n    <script>\n        let currentField = \'\';\n        \n        function logout() {\n            if(confirm(\'تسجيل الخروج؟\')) window.location.href = \'/logout\';\n        }\n\n        function controlBot(action) {\n            const btn = event.target;\n            btn.disabled = true;\n            const originalText = btn.innerHTML;\n            btn.innerHTML = \'<i class="fas fa-spinner fa-spin"></i> جاري...\';\n            \n            fetch(\'/bot_action\', {\n                method: \'POST\',\n                headers: {\'Content-Type\': \'application/json\'},\n                body: JSON.stringify({bot_id: {{ bot.id }}, action: action})\n            })\n            .then(r => r.json())\n            .then(d => { \n                if(d.success) {\n                    location.reload();\n                } else {\n                    btn.disabled = false;\n                    btn.innerHTML = originalText;\n                    alert(\'❌ \' + d.error);\n                }\n            })\n            .catch(() => {\n                btn.disabled = false;\n                btn.innerHTML = originalText;\n                alert(\'❌ حدث خطأ في الاتصال\');\n            });\n        }\n\n        function deleteBot() {\n            if(confirm(\'⚠️ هل أنت متأكد من حذف هذا البوت نهائياً؟\')) {\n                fetch(\'/delete_bot/{{ bot.id }}\', {method: \'POST\'})\n                .then(r => r.json())\n                .then(d => { \n                    if(d.success) {\n                        alert(\'✅ تم حذف البوت بنجاح\');\n                        window.location.href = \'{% if session.get("is_admin") %}/admin/user/{{ bot.user_id }}{% else %}/dashboard{% endif %}\';\n                    } else {\n                        alert(\'❌ \' + d.error);\n                    }\n                });\n            }\n        }\n\n        function editField(field) {\n            currentField = field;\n            const titles = {\n                \'uid\': \'تعديل الأيدي\',\n                \'password\': \'تعديل كلمة المرور\',\n                \'bot_name\': \'تعديل اسم البوت\',\n                \'display_name\': \'تعديل الاسم المعروض\'\n            };\n            document.getElementById(\'modalTitle\').innerText = titles[field] || \'تعديل\';\n            document.getElementById(\'editValue\').value = \'\';\n            document.getElementById(\'editModal\').style.display = \'flex\';\n        }\n\n        function closeModal() {\n            document.getElementById(\'editModal\').style.display = \'none\';\n        }\n\n        function saveEdit() {\n            const value = document.getElementById(\'editValue\').value;\n            if(!value) {\n                alert(\'الرجاء إدخال القيمة\');\n                return;\n            }\n\n            const data = {};\n            data[currentField] = value;\n\n            fetch(\'/edit_bot/{{ bot.id }}\', {\n                method: \'POST\',\n                headers: {\'Content-Type\': \'application/json\'},\n                body: JSON.stringify(data)\n            })\n            .then(r => r.json())\n            .then(d => { \n                if(d.success) {\n                    alert(\'✅ تم التعديل بنجاح\');\n                    location.reload();\n                } else {\n                    alert(\'❌ \' + d.error);\n                }\n            });\n        }\n\n        function addPlayer() {\n            const uid = document.getElementById(\'player_uid\').value;\n            const dur = document.getElementById(\'duration\').value;\n            if(!uid || !dur) {\n                alert(\'الرجاء إدخال أيدي اللاعب والمدة\');\n                return;\n            }\n\n            const btn = event.target;\n            btn.disabled = true;\n            const originalText = btn.innerHTML;\n            btn.innerHTML = \'<i class="fas fa-spinner fa-spin"></i> جاري...\';\n\n            fetch(\'/add_player\', {\n                method: \'POST\',\n                headers: {\'Content-Type\': \'application/json\'},\n                body: JSON.stringify({\n                    bot_id: {{ bot.id }},\n                    player_uid: uid,\n                    duration: dur\n                })\n            })\n            .then(r => r.json())\n            .then(d => {\n                btn.disabled = false;\n                btn.innerHTML = originalText;\n                \n                if(d.success) {\n                    alert(d.message || \'✅ تم إرسال طلب الصداقة بنجاح\');\n                    location.reload();\n                } else {\n                    alert(d.error || \'❌ حدث خطأ ما ولم يتم الإرسال\');\n                }\n            })\n            .catch(() => {\n                btn.disabled = false;\n                btn.innerHTML = originalText;\n                alert(\'❌ حدث خطأ في الاتصال\');\n            });\n        }\n\n        function removePlayer(id) {\n            if(confirm(\'هل أنت متأكد من حذف هذا اللاعب؟\')) {\n                const btn = event.target;\n                btn.disabled = true;\n                const originalText = btn.innerHTML;\n                btn.innerHTML = \'<i class="fas fa-spinner fa-spin"></i>\';\n\n                fetch(\'/remove_player\', {\n                    method: \'POST\',\n                    headers: {\'Content-Type\': \'application/json\'},\n                    body: JSON.stringify({player_id: id})\n                })\n                .then(r => r.json())\n                .then(d => {\n                    btn.disabled = false;\n                    btn.innerHTML = originalText;\n                    \n                    if(d.success) {\n                        alert(d.message || \'✅ تم الحذف بنجاح\');\n                        location.reload();\n                    } else {\n                        alert(d.error || \'❌ حدث خطأ ما ولم يتم الحذف\');\n                    }\n                })\n                .catch(() => {\n                    btn.disabled = false;\n                    btn.innerHTML = originalText;\n                    alert(\'❌ حدث خطأ في الاتصال\');\n                });\n            }\n        }\n    </script>\n</body>\n</html>\n'

TPL_ADMIN_USER_BOTS = '<!DOCTYPE html>\n<html lang="ar" dir="rtl">\n<head>\n    <meta charset="UTF-8">\n    <meta name="viewport" content="width=510, initial-scale=1.0">\n    <title>PANELE BOT - بوتات {{ user.username }}</title>\n    <link rel="stylesheet" href="/static/style.css">\n    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">\n</head>\n<body>\n    <div class="floating-menu">\n        <button onclick="window.location.href=\'/admin\'" title="العودة للوحة الأدمن">\n            <i class="fas fa-arrow-right"></i>\n        </button>\n        <button onclick="logout()" title="تسجيل الخروج">\n            <i class="fas fa-sign-out-alt"></i>\n        </button>\n    </div>\n\n    <div class="container">\n        <a href="/admin" class="back-link">\n            <i class="fas fa-arrow-right"></i> العودة للوحة الأدمن\n        </a>\n\n        <div class="section-header">\n            <h2><i class="fas fa-robot"></i> بوتات المستخدم: {{ user.username }}</h2>\n            <div class="user-info">\n                <span><i class="fas fa-calendar"></i> تنتهي في: {{ user.expiry_date[:10] }}</span>\n                <span><i class="fas fa-chart-line"></i> {{ bots|length }}/{{ user.max_bots }}</span>\n            </div>\n        </div>\n\n        {% if bots %}\n        <div class="bots-grid">\n            {% for bot in bots %}\n            <div class="bot-card" onclick="window.location.href=\'/bot/{{ bot.id }}\'">\n                <div class="status {{ bot.status }}"></div>\n                <div class="bot-icon">\n                    <i class="fas fa-robot"></i>\n                </div>\n                <h3>{{ bot.display_name }}</h3>\n                <div class="bot-id">{{ bot.uid }}</div>\n                <div class="bot-status-text">{{ \'يعمل\' if bot.status == \'running\' else \'متوقف\' }}</div>\n                <div class="bot-actions" onclick="event.stopPropagation()">\n                    {% if bot.status == \'running\' %}\n                    <button class="btn-stop" onclick="controlBot({{ bot.id }}, \'stop\')">\n                        <i class="fas fa-stop"></i> إيقاف\n                    </button>\n                    {% else %}\n                    <button class="btn-start" onclick="controlBot({{ bot.id }}, \'start\')">\n                        <i class="fas fa-play"></i> تشغيل\n                    </button>\n                    {% endif %}\n                    <button class="btn-delete" onclick="deleteBot({{ bot.id }})">\n                        <i class="fas fa-trash"></i>\n                    </button>\n                </div>\n            </div>\n            {% endfor %}\n        </div>\n        {% else %}\n        <div class="empty-state">\n            <i class="fas fa-robot"></i>\n            <h3>لا يوجد بوتات لهذا المستخدم</h3>\n        </div>\n        {% endif %}\n    </div>\n\n    <script>\n        function logout() {\n            if(confirm(\'تسجيل الخروج؟\')) {\n                window.location.href = \'/logout\';\n            }\n        }\n        \n        function controlBot(id, action) {\n            const btn = event.target;\n            btn.disabled = true;\n            const originalText = btn.innerHTML;\n            btn.innerHTML = \'<i class="fas fa-spinner fa-spin"></i> جاري...\';\n            \n            fetch(\'/bot_action\', {\n                method: \'POST\',\n                headers: {\'Content-Type\': \'application/json\'},\n                body: JSON.stringify({bot_id: id, action: action})\n            })\n            .then(r => r.json())\n            .then(d => { \n                if(d.success) {\n                    location.reload();\n                } else {\n                    btn.disabled = false;\n                    btn.innerHTML = originalText;\n                    alert(\'❌ خطأ: \' + d.error);\n                }\n            })\n            .catch(() => {\n                btn.disabled = false;\n                btn.innerHTML = originalText;\n                alert(\'❌ حدث خطأ في الاتصال\');\n            });\n        }\n        \n        function deleteBot(id) {\n            if(confirm(\'⚠️ هل أنت متأكد من حذف هذا البوت نهائياً؟\')) {\n                fetch(\'/delete_bot/\' + id, {method: \'POST\'})\n                .then(r => r.json())\n                .then(d => { \n                    if(d.success) {\n                        alert(\'✅ تم حذف البوت بنجاح\');\n                        location.reload();\n                    } else {\n                        alert(\'❌ خطأ: \' + d.error);\n                    }\n                });\n            }\n        }\n    </script>\n</body>\n</html>\n'

TPL_ADMIN           = '<!DOCTYPE html>\n<html lang="ar" dir="rtl">\n<head>\n    <meta charset="UTF-8">\n    <meta name="viewport" content="width=510, initial-scale=1.0">\n    <title>PANELE BOT - لوحة الأدمن</title>\n    <link rel="stylesheet" href="/static/style.css">\n    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">\n</head>\n<body>\n    <div class="floating-menu">\n        <button onclick="showAddUserModal()" title="إضافة مستخدم">\n            <i class="fas fa-user-plus"></i>\n        </button>\n        <button onclick="showAddLinkModal()" title="إضافة رابط">\n            <i class="fas fa-link"></i>\n        </button>\n        <button onclick="document.getElementById(\'bot-files-section\').scrollIntoView({behavior:\'smooth\'})" title="إدارة ملفات البوت">\n            <i class="fas fa-folder-open"></i>\n        </button>\n        <button onclick="window.location.href=\'/dashboard\'" title="لوحة المستخدم">\n            <i class="fas fa-home"></i>\n        </button>\n        <button onclick="logout()" title="تسجيل الخروج">\n            <i class="fas fa-sign-out-alt"></i>\n        </button>\n    </div>\n\n    <div class="container">\n        <div class="stats-grid">\n            <div class="stat-card">\n                <i class="fas fa-users"></i>\n                <span class="stat-value">{{ users|length }}</span>\n                <span class="stat-label">مستخدم</span>\n            </div>\n            <div class="stat-card">\n                <i class="fas fa-robot"></i>\n                <span class="stat-value">{{ bots|length }}</span>\n                <span class="stat-label">بوت</span>\n            </div>\n            <div class="stat-card">\n                <i class="fas fa-play"></i>\n                <span class="stat-value">{{ bots|selectattr(\'status\', \'equalto\', \'running\')|list|length }}</span>\n                <span class="stat-label">يعمل</span>\n            </div>\n            <div class="stat-card">\n                <i class="fas fa-stop"></i>\n                <span class="stat-value">{{ bots|selectattr(\'status\', \'equalto\', \'stopped\')|list|length }}</span>\n                <span class="stat-label">متوقف</span>\n            </div>\n        </div>\n\n        <div class="section-header">\n            <h2><i class="fas fa-users-cog"></i> المستخدمين</h2>\n            <button class="btn-create" onclick="showAddUserModal()">\n                <i class="fas fa-plus"></i> مستخدم جديد\n            </button>\n        </div>\n\n        <div class="users-table">\n            <table>\n                <thead>\n                    <tr>\n                        <th>المستخدم</th>\n                        <th>التليجرام</th>\n                        <th>البوتات</th>\n                        <th>الحد الأقصى</th>\n                        <th>تاريخ الإنشاء</th>\n                        <th>تنتهي في</th>\n                        <th>التحكم</th>\n                    </tr>\n                </thead>\n                <tbody>\n                    {% for user in users if not user.is_admin %}\n                    <tr>\n                        <td><i class="fas fa-user"></i> {{ user.username }}</td>\n                        <td>{{ user.telegram or \'—\' }}</td>\n                        <td>{{ bots|selectattr(\'user_id\', \'equalto\', user.id)|list|length }}</td>\n                        <td>{{ user.max_bots }}</td>\n                        <td>{{ user.created_at[:10] }}</td>\n                        <td>\n                            <span class="{% if user.expiry_date[:10] < now.strftime(\'%Y-%m-%d\') %}expired{% endif %}">\n                                {{ user.expiry_date[:10] }}\n                            </span>\n                        </td>\n                        <td>\n                            <button class="btn-icon" onclick="viewUserBots({{ user.id }})" title="عرض البوتات">\n                                <i class="fas fa-robot"></i>\n                            </button>\n                            <button class="btn-icon" onclick="editUser({{ user.id }})" title="تعديل">\n                                <i class="fas fa-edit"></i>\n                            </button>\n                            <button class="btn-icon" onclick="deleteUser({{ user.id }})" title="حذف">\n                                <i class="fas fa-trash"></i>\n                            </button>\n                        </td>\n                    </tr>\n                    {% endfor %}\n                </tbody>\n            </table>\n        </div>\n\n\n        <div class="section-header" style="margin-top: 40px;" id="bot-files-section">\n            <h2><i class="fas fa-folder-open"></i> إدارة ملفات بوت الصديق (xL9BI7E)</h2>\n            <div>\n                <button class="btn-create" onclick="document.getElementById(\'upload_single_file\').click()">\n                    <i class="fas fa-file-upload"></i> رفع ملف\n                </button>\n                <button class="btn-create" onclick="document.getElementById(\'upload_zip_file\').click()" style="background:#f59e0b;">\n                    <i class="fas fa-file-archive"></i> رفع ZIP\n                </button>\n                <button class="btn-create" onclick="refreshBotFiles()" style="background:#6b7280;">\n                    <i class="fas fa-sync"></i> تحديث\n                </button>\n            </div>\n        </div>\n\n        <input type="file" id="upload_single_file" style="display:none" onchange="uploadSingleFile(this)">\n        <input type="file" id="upload_zip_file" accept=".zip" style="display:none" onchange="uploadZipFile(this)">\n\n        <div class="modal-note" style="margin-bottom:15px;">\n            <i class="fas fa-info-circle"></i>\n            هذه الملفات هي قالب البوت — يتم نسخها لكل بوت جديد ينشئه المستخدمون.\n            اضغط <b>رفع ZIP</b> لاستبدال كل الملفات دفعةً واحدة (يستخرج محتوى الـ zip)\n            أو <b>رفع ملف</b> لإضافة/استبدال ملف واحد.\n            <br>📁 المسار في الخادم: <code id="xL9BI7E_path"></code>\n        </div>\n\n        <div class="users-table" id="bot_files_table_wrapper">\n            <table>\n                <thead>\n                    <tr>\n                        <th>اسم الملف</th>\n                        <th>الحجم</th>\n                        <th>آخر تعديل</th>\n                        <th>التحكم</th>\n                    </tr>\n                </thead>\n                <tbody id="bot_files_tbody">\n                    <tr><td colspan="4" style="text-align:center;">جاري التحميل...</td></tr>\n                </tbody>\n            </table>\n        </div>\n\n        <div class="modal" id="renameFileModal">\n            <div class="modal-content">\n                <h3><i class="fas fa-edit"></i> إعادة تسمية الملف</h3>\n                <input type="hidden" id="rename_old_name">\n                <input type="text" id="rename_new_name" placeholder="الاسم الجديد">\n                <div class="modal-buttons">\n                    <button onclick="confirmRename()" class="btn-save">\n                        <i class="fas fa-save"></i> حفظ\n                    </button>\n                    <button onclick="closeModal(\'renameFileModal\')" class="btn-cancel">\n                        <i class="fas fa-times"></i> إلغاء\n                    </button>\n                </div>\n            </div>\n        </div>\n\n        <div class="section-header" style="margin-top: 40px;">\n            <h2><i class="fas fa-link"></i> الروابط السريعة</h2>\n        </div>\n\n        <div class="links-grid">\n            {% for link in links %}\n            <div class="link-card">\n                <div class="link-icon">\n                    <i class="{{ link.icon }}"></i>\n                </div>\n                <div class="link-info">\n                    <h4>{{ link.name }}</h4>\n                    <p>{{ link.url[:30] }}...</p>\n                </div>\n                <button class="btn-icon" onclick="deleteLink({{ link.id }})" title="حذف الرابط">\n                    <i class="fas fa-trash"></i>\n                </button>\n            </div>\n            {% endfor %}\n            \n            <div class="link-card add-link" onclick="showAddLinkModal()">\n                <i class="fas fa-plus"></i>\n                <span>إضافة رابط</span>\n            </div>\n        </div>\n    </div>\n\n    <div class="modal" id="addUserModal">\n        <div class="modal-content">\n            <h3><i class="fas fa-user-plus"></i> إضافة مستخدم جديد</h3>\n            <input type="text" id="new_username" placeholder="اسم المستخدم" required>\n            <input type="text" id="new_password" placeholder="كلمة المرور" required>\n            <input type="text" id="new_telegram" placeholder="@username (اختياري)">\n            <div class="form-row">\n                <input type="number" id="new_days" placeholder="عدد الأيام" value="30" min="1">\n                <input type="number" id="new_max_bots" placeholder="عدد البوتات" value="5" min="1">\n            </div>\n            <div class="modal-buttons">\n                <button onclick="createUser()" class="btn-save">\n                    <i class="fas fa-check"></i> إنشاء\n                </button>\n                <button onclick="closeModal(\'addUserModal\')" class="btn-cancel">\n                    <i class="fas fa-times"></i> إلغاء\n                </button>\n            </div>\n        </div>\n    </div>\n\n    <div class="modal" id="editUserModal">\n        <div class="modal-content">\n            <h3><i class="fas fa-edit"></i> تعديل المستخدم</h3>\n            <input type="hidden" id="edit_user_id">\n            <input type="text" id="edit_username" placeholder="اسم المستخدم">\n            <input type="text" id="edit_password" placeholder="كلمة المرور (اترك فارغاً إذا لا تريد التغيير)">\n            <input type="text" id="edit_telegram" placeholder="@username">\n            <div class="form-row">\n                <input type="number" id="edit_days" placeholder="عدد الأيام للإضافة" value="30" min="1">\n                <input type="number" id="edit_max_bots" placeholder="عدد البوتات" min="1">\n            </div>\n            <div class="modal-buttons">\n                <button onclick="saveUserEdit()" class="btn-save">\n                    <i class="fas fa-save"></i> حفظ\n                </button>\n                <button onclick="closeModal(\'editUserModal\')" class="btn-cancel">\n                    <i class="fas fa-times"></i> إلغاء\n                </button>\n            </div>\n        </div>\n    </div>\n\n    <div class="modal" id="addLinkModal">\n        <div class="modal-content">\n            <h3><i class="fas fa-plus-circle"></i> إضافة رابط جديد</h3>\n            <p class="modal-note">هذا الرابط سيظهر في القائمة الجانبية لجميع المستخدمين</p>\n            <input type="text" id="link_name" placeholder="اسم الرابط (مثال: تليجرام المطور)" required>\n            <input type="url" id="link_url" placeholder="الرابط (https://...)" required>\n            <input type="text" id="link_icon" placeholder="الأيقونة (مثال: fab fa-telegram)" value="fas fa-link">\n            <div class="icon-hint">\n                <i class="fas fa-info-circle"></i>\n                أيقونات متاحة: fab fa-telegram, fab fa-youtube, fab fa-discord, fas fa-globe, etc.\n            </div>\n            <div class="modal-buttons">\n                <button onclick="createLink()" class="btn-save">\n                    <i class="fas fa-plus"></i> إضافة\n                </button>\n                <button onclick="closeModal(\'addLinkModal\')" class="btn-cancel">\n                    <i class="fas fa-times"></i> إلغاء\n                </button>\n            </div>\n        </div>\n    </div>\n\n    <script>\n        function logout() {\n            if(confirm(\'تسجيل الخروج؟\')) {\n                window.location.href = \'/logout\';\n            }\n        }\n\n        function showAddUserModal() {\n            document.getElementById(\'addUserModal\').style.display = \'flex\';\n        }\n\n        function showAddLinkModal() {\n            document.getElementById(\'addLinkModal\').style.display = \'flex\';\n        }\n\n        function closeModal(id) {\n            document.getElementById(id).style.display = \'none\';\n        }\n\n        function createUser() {\n            const username = document.getElementById(\'new_username\').value;\n            const password = document.getElementById(\'new_password\').value;\n            const days = document.getElementById(\'new_days\').value;\n            const max_bots = document.getElementById(\'new_max_bots\').value;\n            \n            if(!username || !password) {\n                alert(\'الرجاء إدخال اسم المستخدم وكلمة المرور\');\n                return;\n            }\n            \n            const data = {\n                username: username,\n                password: password,\n                telegram: document.getElementById(\'new_telegram\').value,\n                days: parseInt(days),\n                max_bots: parseInt(max_bots)\n            };\n            \n            fetch(\'/create_user\', {\n                method: \'POST\',\n                headers: {\'Content-Type\': \'application/json\'},\n                body: JSON.stringify(data)\n            })\n            .then(r => r.json())\n            .then(d => { \n                if(d.success) {\n                    alert(\'✅ تم إنشاء المستخدم بنجاح\');\n                    location.reload();\n                } else {\n                    alert(\'❌ خطأ: \' + d.error);\n                }\n            });\n        }\n\n        function createLink() {\n            const name = document.getElementById(\'link_name\').value;\n            const url = document.getElementById(\'link_url\').value;\n            const icon = document.getElementById(\'link_icon\').value;\n            \n            if(!name || !url) {\n                alert(\'الرجاء إدخال اسم الرابط والرابط\');\n                return;\n            }\n            \n            const data = {\n                name: name,\n                url: url,\n                icon: icon || \'fas fa-link\'\n            };\n            \n            fetch(\'/add_link\', {\n                method: \'POST\',\n                headers: {\'Content-Type\': \'application/json\'},\n                body: JSON.stringify(data)\n            })\n            .then(r => r.json())\n            .then(d => { \n                if(d.success) {\n                    alert(\'✅ تم إضافة الرابط بنجاح\');\n                    location.reload();\n                } else {\n                    alert(\'❌ خطأ: \' + d.error);\n                }\n            });\n        }\n\n        function deleteLink(id) {\n            if(confirm(\'هل أنت متأكد من حذف هذا الرابط؟\')) {\n                fetch(\'/delete_link/\' + id, {method: \'POST\'})\n                .then(r => r.json())\n                .then(d => { \n                    if(d.success) {\n                        alert(\'✅ تم حذف الرابط بنجاح\');\n                        location.reload();\n                    } else {\n                        alert(\'❌ خطأ: \' + d.error);\n                    }\n                });\n            }\n        }\n\n        function viewUserBots(id) {\n            window.location.href = \'/admin/user/\' + id;\n        }\n\n        function editUser(id) {\n            fetch(\'/get_user/\' + id)\n            .then(r => r.json())\n            .then(user => {\n                document.getElementById(\'edit_user_id\').value = user.id;\n                document.getElementById(\'edit_username\').value = user.username;\n                document.getElementById(\'edit_telegram\').value = user.telegram || \'\';\n                document.getElementById(\'edit_max_bots\').value = user.max_bots;\n                document.getElementById(\'edit_password\').value = \'\';\n                document.getElementById(\'edit_days\').value = \'30\';\n                document.getElementById(\'editUserModal\').style.display = \'flex\';\n            });\n        }\n\n        function saveUserEdit() {\n            const id = document.getElementById(\'edit_user_id\').value;\n            const data = {};\n            \n            if(document.getElementById(\'edit_username\').value) {\n                data.username = document.getElementById(\'edit_username\').value;\n            }\n            if(document.getElementById(\'edit_password\').value) {\n                data.password = document.getElementById(\'edit_password\').value;\n            }\n            if(document.getElementById(\'edit_telegram\').value) {\n                data.telegram = document.getElementById(\'edit_telegram\').value;\n            }\n            if(document.getElementById(\'edit_max_bots\').value) {\n                data.max_bots = parseInt(document.getElementById(\'edit_max_bots\').value);\n            }\n            if(document.getElementById(\'edit_days\').value) {\n                data.days = parseInt(document.getElementById(\'edit_days\').value);\n            }\n            \n            fetch(\'/edit_user/\' + id, {\n                method: \'POST\',\n                headers: {\'Content-Type\': \'application/json\'},\n                body: JSON.stringify(data)\n            })\n            .then(r => r.json())\n            .then(d => {\n                if(d.success) {\n                    alert(\'✅ تم تعديل المستخدم بنجاح\');\n                    location.reload();\n                } else {\n                    alert(\'❌ خطأ: \' + d.error);\n                }\n            });\n        }\n\n        function deleteUser(id) {\n            if(confirm(\'⚠️ هل أنت متأكد من حذف هذا المستخدم نهائياً؟\\nسيتم حذف جميع بوتاته أيضاً!\')) {\n                fetch(\'/delete_user/\' + id, {method: \'POST\'})\n                .then(r => r.json())\n                .then(d => { \n                    if(d.success) {\n                        alert(\'✅ تم حذف المستخدم بنجاح\');\n                        location.reload();\n                    } else {\n                        alert(\'❌ خطأ: \' + d.error);\n                    }\n                });\n            }\n        }\n    \n\n        // ====== إدارة ملفات بوت الصديق ======\n        async function loadBotFiles() {\n            try {\n                const r = await fetch(\'/admin/bot_files\');\n                const d = await r.json();\n                if (!d.success) {\n                    document.getElementById(\'bot_files_tbody\').innerHTML =\n                        \'<tr><td colspan="4" style="text-align:center;color:#ef4444;">\'+d.error+\'</td></tr>\';\n                    return;\n                }\n                document.getElementById(\'xL9BI7E_path\').textContent = d.path || \'\';\n                const tbody = document.getElementById(\'bot_files_tbody\');\n                if (!d.files || d.files.length === 0) {\n                    tbody.innerHTML = \'<tr><td colspan="4" style="text-align:center;">لا توجد ملفات. ارفع ZIP لاستيراد قالب البوت.</td></tr>\';\n                    return;\n                }\n                tbody.innerHTML = \'\';\n                for (const f of d.files) {\n                    const tr = document.createElement(\'tr\');\n                    tr.innerHTML = `\n                        <td><i class="fas fa-file-code"></i> ${f.name}</td>\n                        <td>${f.size_human}</td>\n                        <td>${f.mtime}</td>\n                        <td>\n                            <button class="btn-icon" title="تنزيل" onclick="downloadBotFile(\'${f.name.replace(/\'/g,"\\\\\'")}\')">\n                                <i class="fas fa-download"></i>\n                            </button>\n                            <button class="btn-icon" title="إعادة تسمية" onclick="renameBotFile(\'${f.name.replace(/\'/g,"\\\\\'")}\')">\n                                <i class="fas fa-edit"></i>\n                            </button>\n                            <button class="btn-icon" title="حذف" onclick="deleteBotFile(\'${f.name.replace(/\'/g,"\\\\\'")}\')">\n                                <i class="fas fa-trash"></i>\n                            </button>\n                        </td>`;\n                    tbody.appendChild(tr);\n                }\n            } catch (e) {\n                document.getElementById(\'bot_files_tbody\').innerHTML =\n                    \'<tr><td colspan="4" style="text-align:center;color:#ef4444;">خطأ في التحميل</td></tr>\';\n            }\n        }\n\n        function refreshBotFiles() { loadBotFiles(); }\n\n        async function uploadSingleFile(input) {\n            if (!input.files || !input.files[0]) return;\n            const file = input.files[0];\n            const fd = new FormData();\n            fd.append(\'file\', file);\n            try {\n                const r = await fetch(\'/admin/bot_files/upload\', { method: \'POST\', body: fd });\n                const d = await r.json();\n                if (d.success) { alert(\'✅ تم رفع الملف: \' + file.name); loadBotFiles(); }\n                else alert(\'❌ \' + d.error);\n            } catch (e) { alert(\'❌ خطأ في الرفع\'); }\n            input.value = \'\';\n        }\n\n        async function uploadZipFile(input) {\n            if (!input.files || !input.files[0]) return;\n            const file = input.files[0];\n            if (!confirm(\'⚠️ سيتم استخراج محتوى الـ ZIP إلى مجلد xL9BI7E.\\nهل تريد حذف الملفات الموجودة أولاً (استبدال كامل)؟\\nاضغط "موافق" للاستبدال الكامل، "إلغاء" لدمج الملفات.\')) {\n                // user chose merge: send replace=false\n                await doZipUpload(file, false);\n            } else {\n                await doZipUpload(file, true);\n            }\n            input.value = \'\';\n        }\n\n        async function doZipUpload(file, replace) {\n            const fd = new FormData();\n            fd.append(\'file\', file);\n            fd.append(\'replace\', replace ? \'1\' : \'0\');\n            try {\n                const r = await fetch(\'/admin/bot_files/upload_zip\', { method: \'POST\', body: fd });\n                const d = await r.json();\n                if (d.success) { alert(\'✅ تم استخراج \'+d.count+\' ملف من ZIP\'); loadBotFiles(); }\n                else alert(\'❌ \' + d.error);\n            } catch (e) { alert(\'❌ خطأ في الرفع\'); }\n        }\n\n        function downloadBotFile(name) {\n            window.location.href = \'/admin/bot_files/download/\' + encodeURIComponent(name);\n        }\n\n        async function deleteBotFile(name) {\n            if (!confirm(\'حذف الملف: \' + name + \' ؟\')) return;\n            const r = await fetch(\'/admin/bot_files/delete/\' + encodeURIComponent(name), { method: \'POST\' });\n            const d = await r.json();\n            if (d.success) { alert(\'✅ تم الحذف\'); loadBotFiles(); }\n            else alert(\'❌ \' + d.error);\n        }\n\n        function renameBotFile(name) {\n            document.getElementById(\'rename_old_name\').value = name;\n            document.getElementById(\'rename_new_name\').value = name;\n            document.getElementById(\'renameFileModal\').style.display = \'flex\';\n        }\n\n        async function confirmRename() {\n            const oldName = document.getElementById(\'rename_old_name\').value;\n            const newName = document.getElementById(\'rename_new_name\').value.trim();\n            if (!newName || newName === oldName) { closeModal(\'renameFileModal\'); return; }\n            const r = await fetch(\'/admin/bot_files/rename\', {\n                method:\'POST\',\n                headers:{\'Content-Type\':\'application/json\'},\n                body: JSON.stringify({old_name: oldName, new_name: newName})\n            });\n            const d = await r.json();\n            if (d.success) { closeModal(\'renameFileModal\'); loadBotFiles(); }\n            else alert(\'❌ \' + d.error);\n        }\n\n        // تحميل الملفات عند فتح الصفحة\n        document.addEventListener(\'DOMContentLoaded\', loadBotFiles);\n</script>\n</body>\n</html>\n'


app = Flask(__name__)
app.secret_key = "L9BI7E_SECRET_KEY_2026"
app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024

                                                  
@app.route('/static/style.css')
def serve_css():
    return Response(STATIC_CSS, mimetype='text/css; charset=utf-8')

@app.route('/static/scripts.js')
def serve_js():
    return Response(STATIC_JS, mimetype='application/javascript; charset=utf-8')


def verify_account(uid, password):
    # محاولة التحقق عبر الـ API الخارجي
    try:
        response = requests.get(f"{VERIFY_API_URL}?uid={uid}&password={password}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success' and 'token' in data:
                return {'success': True, 'message': '✅ الحساب صحيح', 'data': data}
    except:
        pass

    # إذا فشل الـ API الخارجي، سنقوم بالتحقق المباشر من Garena (خاصة لحسابات الضيف)
    try:
        url = "https://100067.connect.garena.com/oauth/guest/token/grant"
        headers = {"Content-Type": "application/x-www-form-urlencoded", "User-Agent": "GarenaMSDK/4.0.19P4"}
        data = {"uid": uid, "password": password, "response_type": "token", "client_type": "2", "client_id": "100067"}
        res = requests.post(url, headers=headers, data=data, verify=False, timeout=10)
        if res.status_code == 200 and "access_token" in res.json():
            return {'success': True, 'message': '✅ تم التحقق من حساب الضيف بنجاح'}
    except:
        pass

    # في حال فشل كل شيء، سنسمح بإنشاء البوت إذا كانت البيانات تبدو منطقية (اختياري حسب رغبة المستخدم)
    # لكن حالياً سنعيد رسالة خطأ واضحة
    return {'success': False, 'message': '❌ بيانات الحساب غير صحيحة أو انتهت صلاحية الجلسة'}

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def _load_json(path, default):
    if not os.path.exists(path): return default
    try:
        with open(path, 'r', encoding='utf-8') as f: return json.load(f)
    except: return default

def _save_json(path, obj):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=4)

def get_users():    return _load_json(USERS_FILE,   [])
def save_users(u):  _save_json(USERS_FILE, u)
def get_bots():     return _load_json(BOTS_FILE,    [])
def save_bots(b):   _save_json(BOTS_FILE, b)
def get_links():    return _load_json(LINKS_FILE,   [])
def save_links(l):  _save_json(LINKS_FILE, l)
def get_players():  return _load_json(PLAYERS_FILE, [])
def save_players(p):_save_json(PLAYERS_FILE, p)

def get_player_info_from_api(uid):
    try:
        name, region, level = fs_get_player_info(uid)
        return {'name': name, 'region': region, 'level': level}
    except Exception as e:
        print(f"⚠️ خطأ في جلب معلومات اللاعب {uid}: {e}")
        return {'name': 'غير معروف', 'region': 'N/A', 'level': 'N/A'}

def send_friend_request_via_api(account_uid, account_password, target_uid):
    try:
        token = fs_fetch_jwt_token_direct(account_uid, account_password)
        if not token:
            return {'status': 'error', 'message': '❌ فشل جلب التوكن. تأكد من صحة بيانات الحساب'}
        success, message = fs_send_friend_request(token, target_uid)
        info = get_player_info_from_api(target_uid)
        if success:
            return {'status': 'success', 'message': '✅ تم إرسال طلب الصداقة بنجاح', 'player_info': info}
        return {'status': 'error', 'message': f'❌ {message}', 'player_info': info}
    except Exception as e:
        return {'status': 'error', 'message': f'❌ حدث خطأ: {str(e)}',
                'player_info': {'name':'غير معروف','region':'N/A','level':'N/A'}}

def remove_friend_via_api(account_uid, account_password, target_uid):
    try:
        token = fs_fetch_jwt_token_direct(account_uid, account_password)
        if not token:
            return {'status': 'error', 'message': '❌ فشل جلب التوكن. تأكد من صحة بيانات الحساب'}
        success, message = fs_remove_friend(token, target_uid)
        info = get_player_info_from_api(target_uid)
        if success:
            return {'status': 'success', 'message': '✅ تم حذف الصديق بنجاح', 'player_info': info}
        return {'status': 'error', 'message': f'❌ {message}', 'player_info': info}
    except Exception as e:
        return {'status': 'error', 'message': f'❌ حدث خطأ: {str(e)}',
                'player_info': {'name':'غير معروف','region':'N/A','level':'N/A'}}

def copy_entire_folder(src, dst):
    try:
        if os.path.exists(dst): shutil.rmtree(dst)
        shutil.copytree(src, dst)
        print(f"✅ تم نسخ المجلد من {src} إلى {dst}"); return True
    except Exception as e:
        print(f"❌ خطأ في نسخ المجلد: {e}"); return False

def update_config_file(bot_path, uid, password, bot_name, display_name):
    config_path = os.path.join(bot_path, 'config.json')
    try:
        config = _load_json(config_path, {})
        config.setdefault('account', {})
        config['account']['uid'] = uid
        config['account']['password'] = password
        config.setdefault('bot', {})
        config['bot']['name'] = bot_name
        config['bot']['display_name'] = display_name
        _save_json(config_path, config)
        print(f"✅ تم تحديث ملف config.json للبوت {uid}"); return True
    except Exception as e:
        print(f"❌ خطأ في تحديث config.json: {e}"); return False

def update_bot_config_file(bot_path, field, value):
    config_path = os.path.join(bot_path, 'config.json')
    try:
        config = _load_json(config_path, {})
        if field == 'uid':
            config.setdefault('account', {})['uid'] = value
        elif field == 'password':
            config.setdefault('account', {})['password'] = value
        elif field == 'bot_name':
            config.setdefault('bot', {})['name'] = value
        elif field == 'display_name':
            config.setdefault('bot', {})['display_name'] = value
        _save_json(config_path, config)
        return True
    except Exception as e:
        print(f"❌ خطأ في تحديث config.json: {e}"); return False


def check_admin_exists():
    users = get_users()
    if not users:
        print("📁 لا يوجد مستخدمين - جاري إنشاء admin...")
        admin = {
            'id': 1, 'username': '@xCTx_AyOuB',
            'password': hash_password('@xCTx_AyOuB'),
            'max_bots': 999999,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'expiry_date': (datetime.now() + timedelta(days=36500)).strftime('%Y-%m-%d %H:%M:%S'),
            'is_admin': True, 'telegram': '@L3abassi1235'
        }
        save_users([admin])
        os.makedirs(os.path.join(USERS_STORAGE, "admin_XL9BI7E"), exist_ok=True)
        if not os.path.exists(BOTS_FILE):    save_bots([])
        if not os.path.exists(LINKS_FILE):   save_links([])
        if not os.path.exists(PLAYERS_FILE): save_players([])
        print("="*50); print("✅ تم إنشاء مستخدم admin بنجاح")
        print("👤 @xCTx_AyOuB / 🔑 @xCTx_AyOuB"); print("="*50)
        return True
    for u in users:
        if u.get('is_admin'):
            print("✅ مستخدم admin موجود بالفعل (9sfwiw / yasser2004@)")
            return True
    new_admin = {
        'id': max([u['id'] for u in users], default=0) + 1,
        'username': '@xCTx_AyOuB',
        'password': hash_password('@xCTx_AyOuB'),
        'max_bots': 999999,
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'expiry_date': (datetime.now() + timedelta(days=36500)).strftime('%Y-%m-%d %H:%M:%S'),
        'is_admin': True, 'telegram': '@L3abassi1235'
    }
    users.append(new_admin); save_users(users)
    os.makedirs(os.path.join(USERS_STORAGE, "admin_XL9BI7E"), exist_ok=True)
    print("✅ تم إضافة admin: 9sfwiw / yasser2004@")
    return True

check_admin_exists()


@app.route('/')
def index():
    if 'user_id' in session:
        return redirect('/admin' if session.get('is_admin') else '/dashboard')
    return render_template_string(TPL_LOGIN)

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username'].strip()
    password = request.form['password'].strip()
    hashed = hash_password(password)
    user = None
    for u in get_users():
        if u['username'] == username and u['password'] == hashed:
            user = u; break
    if user:
        session['user_id']  = user['id']
        session['username'] = user['username']
        session['is_admin'] = user.get('is_admin', False)
        return redirect('/admin' if user.get('is_admin') else '/dashboard')
    return render_template_string(TPL_LOGIN, error='خطأ في اسم المستخدم أو كلمة المرور')

@app.route('/logout')
def logout():
    session.clear(); return redirect('/')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session: return redirect('/')
    if session.get('is_admin'):  return redirect('/admin')
    users = get_users()
    user = next((u for u in users if u['id'] == session['user_id']), None)
    if not user: session.clear(); return redirect('/')
    bots = [b for b in get_bots() if b['user_id'] == user['id']]
    return render_template_string(TPL_DASHBOARD, user=user, bots=bots, links=get_links())

@app.route('/admin')
def admin():
    if 'user_id' not in session or not session.get('is_admin'): return redirect('/')
    return render_template_string(TPL_ADMIN,
        users=get_users(), bots=get_bots(), links=get_links(), now=datetime.now())

@app.route('/admin/user/<int:user_id>')
def admin_user_bots(user_id):
    if 'user_id' not in session or not session.get('is_admin'): return redirect('/')
    user = next((u for u in get_users() if u['id'] == user_id), None)
    if not user: return redirect('/admin')
    bots = [b for b in get_bots() if b['user_id'] == user_id]
    return render_template_string(TPL_ADMIN_USER_BOTS, user=user, bots=bots)


@app.route('/create_user', methods=['POST'])
def create_user():
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'success': False, 'error': 'Unauthorized'})
    data = request.json
    users = get_users()
    for u in users:
        if u['username'] == data['username']:
            return jsonify({'success': False, 'error': 'اسم المستخدم موجود بالفعل'})
    new_id = max([u['id'] for u in users], default=0) + 1
    user = {
        'id': new_id, 'username': data['username'],
        'password': hash_password(data['password']),
        'max_bots': int(data['max_bots']),
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'expiry_date': (datetime.now() + timedelta(days=int(data['days']))).strftime('%Y-%m-%d %H:%M:%S'),
        'is_admin': False, 'telegram': data.get('telegram', '')
    }
    users.append(user); save_users(users)
    user_folder = os.path.join(USERS_STORAGE, f"user_{new_id}_{data['username']}")
    os.makedirs(user_folder, exist_ok=True)
    os.makedirs(os.path.join(user_folder, 'bots'), exist_ok=True)
    return jsonify({'success': True})

@app.route('/edit_user/<int:user_id>', methods=['POST'])
def edit_user(user_id):
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'success': False, 'error': 'Unauthorized'})
    data = request.json
    users = get_users()
    idx = next((i for i,u in enumerate(users) if u['id']==user_id), None)
    if idx is None: return jsonify({'success': False, 'error': 'المستخدم غير موجود'})
    if users[idx].get('is_admin'):
        return jsonify({'success': False, 'error': 'لا يمكن تعديل حساب الأدمن'})
    if 'username' in data and data['username']:
        for u in users:
            if u['id']!=user_id and u['username']==data['username']:
                return jsonify({'success': False, 'error': 'اسم المستخدم موجود بالفعل'})
        users[idx]['username'] = data['username']
    if 'password' in data and data['password']:
        users[idx]['password'] = hash_password(data['password'])
    if 'telegram' in data: users[idx]['telegram'] = data['telegram']
    if 'days' in data and data['days']:
        users[idx]['expiry_date'] = (datetime.now()+timedelta(days=int(data['days']))).strftime('%Y-%m-%d %H:%M:%S')
    if 'max_bots' in data and data['max_bots']:
        users[idx]['max_bots'] = int(data['max_bots'])
    save_users(users)
    return jsonify({'success': True})

@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'success': False, 'error': 'Unauthorized'})
    users = get_users()
    target = next((u for u in users if u['id']==user_id), None)
    if target and target.get('is_admin'):
        return jsonify({'success': False, 'error': 'لا يمكن حذف حساب الأدمن'})
    if target:
        f = os.path.join(USERS_STORAGE, f"user_{user_id}_{target['username']}")
        if os.path.exists(f): shutil.rmtree(f)
    save_bots([b for b in get_bots() if b['user_id'] != user_id])
    save_users([u for u in users if u['id'] != user_id])
    return jsonify({'success': True})

@app.route('/get_user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'success': False, 'error': 'Unauthorized'})
    user = next((u for u in get_users() if u['id']==user_id), None)
    if not user: return jsonify({'success': False, 'error': 'المستخدم غير موجود'})
    return jsonify({'id': user['id'], 'username': user['username'],
                    'max_bots': user['max_bots'], 'expiry_date': user['expiry_date'],
                    'telegram': user.get('telegram',''),
                    'is_admin': user.get('is_admin', False)})


@app.route('/create_bot')
def create_bot_page():
    if 'user_id' not in session or session.get('is_admin'): return redirect('/')
    return render_template_string(TPL_CREATE_BOT)

@app.route('/verify_account', methods=['POST'])
def verify_account_route():
    if 'user_id' not in session: return jsonify({'success': False, 'error': 'Unauthorized'})
    data = request.json
    uid, pw = data.get('uid'), data.get('password')
    if not uid or not pw: return jsonify({'success': False, 'error': 'الرجاء إدخال الأيدي وكلمة المرور'})
    return jsonify(verify_account(uid, pw))

@app.route('/create_bot', methods=['POST'])
def create_bot():
    if 'user_id' not in session: return jsonify({'success': False, 'error': 'Unauthorized'})
    data = request.json
    user_id = session['user_id']
    users = get_users()
    user = next((u for u in users if u['id']==user_id), None)
    if not user: return jsonify({'success': False, 'error': 'User not found'})
    user_bots = len([b for b in get_bots() if b['user_id']==user_id])
    if user_bots >= user['max_bots']:
        return jsonify({'success': False, 'error': '❌ لقد وصلت للحد الأقصى'})
    bot_uid, bot_password = data['uid'], data['password']
    # سنحاول التحقق، لكن إذا فشل سنعطي تحذيراً أو نسمح بالاستمرار إذا كانت البيانات تبدو كحساب ضيف
    vr = verify_account(bot_uid, bot_password)
    # إذا كنت تريد إجبار التحقق، اترك هذا الشرط. إذا كنت تريد السماح بالبيانات "كما هي" فقم بتعطيله.
    # بناءً على طلبك، سأجعله أكثر مرونة.
    if not vr.get('success'):
        # إذا كانت كلمة المرور طويلة جداً (مثل توكن حساب الضيف)، قد نتجاوز التحقق الصارم
        if len(bot_password) < 32: 
            return jsonify({'success': False, 'error': f"❌ فشل التحقق: {vr.get('message')}"})
    user_folder = os.path.join(USERS_STORAGE, f"user_{user_id}_{user['username']}")
    bots_folder = os.path.join(user_folder, 'bots')
    bot_path = os.path.join(bots_folder, bot_uid)
    if os.path.exists(bot_path):
        return jsonify({'success': False, 'error': '❌ هذا الأيدي مستخدم'})
    if not os.path.exists(LONELY_SOURCE) or not os.listdir(LONELY_SOURCE):
        return jsonify({'success': False, 'error': '❌ ملفات قالب البوت (xL9BI7E) غير موجودة. ارفعها من لوحة الأدمن أولاً.'})
    if not copy_entire_folder(LONELY_SOURCE, bot_path):
        return jsonify({'success': False, 'error': '❌ فشل نسخ ملفات البوت'})
    update_config_file(bot_path, data['uid'], data['password'], data['bot_name'], data['display_name'])
    bots = get_bots()
    new_bot = {
        'id': len(bots)+1, 'user_id': user_id,
        'uid': data['uid'], 'password': data['password'],
        'name': data['bot_name'], 'display_name': data['display_name'],
        'status': 'stopped',
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'pid': None
    }
    bots.append(new_bot); save_bots(bots)
    return jsonify({'success': True, 'bot': new_bot})

@app.route('/bot/<int:bot_id>')
def bot_details(bot_id):
    if 'user_id' not in session: return redirect('/')
    bot = next((b for b in get_bots() if b['id']==bot_id), None)
    if not bot or (bot['user_id']!=session['user_id'] and not session.get('is_admin')):
        return redirect('/dashboard')
    players = [p for p in get_players() if p['bot_uid']==bot['uid']]
    for p in players:
        exp = datetime.strptime(p['expiry_date'], '%Y-%m-%d %H:%M:%S')
        rem = exp - datetime.now()
        if rem.total_seconds()>0:
            p['remaining_days']  = rem.days
            p['remaining_hours'] = rem.seconds//3600
        else:
            p['remaining_days']=0; p['remaining_hours']=0
    return render_template_string(TPL_BOT_DETAILS, bot=bot, players=players)

@app.route('/bot_action', methods=['POST'])
def bot_action():
    if 'user_id' not in session: return jsonify({'success': False, 'error': 'Unauthorized'})
    data = request.json; bot_id = data['bot_id']; action = data['action']
    bots = get_bots()
    bot = next((b for b in bots if b['id']==bot_id), None)
    if not bot or (bot['user_id']!=session['user_id'] and not session.get('is_admin')):
        return jsonify({'success': False, 'error': 'Unauthorized'})
    user = next((u for u in get_users() if u['id']==bot['user_id']), None)
    if not user: return jsonify({'success': False, 'error': 'المستخدم غير موجود'})
    bot_path = os.path.join(USERS_STORAGE, f"user_{user['id']}_{user['username']}", 'bots', bot['uid'])
    main_file = os.path.join(bot_path, 'run.py')
    if not os.path.exists(main_file):
        return jsonify({'success': False, 'error': 'ملف run.py غير موجود في مجلد البوت'})
    message = ''
    if action == 'start':
        try:
            p = subprocess.Popen([sys.executable,'run.py'], cwd=bot_path,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
            time.sleep(2)
            if psutil.pid_exists(p.pid):
                bot['status']='running'; bot['pid']=p.pid
                message='✅ تم تشغيل البوت بنجاح'
            else:
                return jsonify({'success': False, 'error': '❌ فشل تشغيل البوت'})
        except Exception as e:
            return jsonify({'success': False, 'error': f'❌ خطأ: {str(e)}'})
    elif action == 'stop':
        if bot['pid']:
            try:
                parent = psutil.Process(bot['pid'])
                for c in parent.children(recursive=True): c.terminate()
                parent.terminate()
                gone, alive = psutil.wait_procs([parent], timeout=3)
                for x in alive: x.kill()
                message='✅ تم إيقاف البوت بنجاح'
            except psutil.NoSuchProcess:
                message='✅ البوت متوقف بالفعل'
            except Exception:
                try: os.kill(bot['pid'], signal.SIGTERM); message='✅ تم إيقاف البوت بنجاح'
                except: message='✅ البوت متوقف بالفعل'
        else:
            message='✅ البوت متوقف بالفعل'
        bot['status']='stopped'; bot['pid']=None
    elif action == 'restart':
        if bot['pid']:
            try:
                parent = psutil.Process(bot['pid'])
                for c in parent.children(recursive=True): c.terminate()
                parent.terminate()
            except:
                try: os.kill(bot['pid'], signal.SIGTERM)
                except: pass
        try:
            p = subprocess.Popen([sys.executable,'run.py'], cwd=bot_path,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
            time.sleep(2)
            if psutil.pid_exists(p.pid):
                bot['status']='running'; bot['pid']=p.pid
                message='✅ تم إعادة تشغيل البوت بنجاح'
            else:
                bot['status']='stopped'; bot['pid']=None
                message='❌ فشل إعادة تشغيل البوت'
        except:
            bot['status']='stopped'; bot['pid']=None
            message='❌ فشل إعادة تشغيل البوت'
    save_bots(bots)
    return jsonify({'success': True, 'status': bot['status'], 'message': message})

@app.route('/edit_bot/<int:bot_id>', methods=['POST'])
def edit_bot(bot_id):
    if 'user_id' not in session: return jsonify({'success': False, 'error': 'Unauthorized'})
    data = request.json
    bots = get_bots()
    bot = next((b for b in bots if b['id']==bot_id), None)
    if not bot or (bot['user_id']!=session['user_id'] and not session.get('is_admin')):
        return jsonify({'success': False, 'error': 'Unauthorized'})
    user = next((u for u in get_users() if u['id']==bot['user_id']), None)
    if not user: return jsonify({'success': False, 'error': 'المستخدم غير موجود'})
    bot_path = os.path.join(USERS_STORAGE, f"user_{user['id']}_{user['username']}", 'bots', bot['uid'])
    for field, value in data.items():
        if field == 'uid':
            if value != bot['uid']:
                new_path = os.path.join(os.path.dirname(bot_path), value)
                if os.path.exists(new_path):
                    return jsonify({'success': False, 'error': 'هذا الأيدي مستخدم لبوت آخر'})
                os.rename(bot_path, new_path); bot_path = new_path; bot['uid']=value
        elif field == 'password':     bot['password']     = value
        elif field == 'bot_name':     bot['name']         = value
        elif field == 'display_name': bot['display_name'] = value
        update_bot_config_file(bot_path, field, value)
    save_bots(bots)
    return jsonify({'success': True})

@app.route('/delete_bot/<int:bot_id>', methods=['POST'])
def delete_bot(bot_id):
    if 'user_id' not in session: return jsonify({'success': False, 'error': 'Unauthorized'})
    bots = get_bots()
    bot = next((b for b in bots if b['id']==bot_id), None)
    if not bot or (bot['user_id']!=session['user_id'] and not session.get('is_admin')):
        return jsonify({'success': False, 'error': 'Unauthorized'})
    if bot['pid']:
        try:
            parent = psutil.Process(bot['pid'])
            for c in parent.children(recursive=True): c.terminate()
            parent.terminate()
        except:
            try: os.kill(bot['pid'], signal.SIGTERM)
            except: pass
    user = next((u for u in get_users() if u['id']==bot['user_id']), None)
    if user:
        bp = os.path.join(USERS_STORAGE, f"user_{user['id']}_{user['username']}", 'bots', bot['uid'])
        if os.path.exists(bp): shutil.rmtree(bp)
    save_players([p for p in get_players() if p['bot_uid']!=bot['uid']])
    save_bots([b for b in bots if b['id']!=bot_id])
    return jsonify({'success': True, 'message': '✅ تم حذف البوت بنجاح'})


@app.route('/add_link', methods=['POST'])
def add_link():
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'success': False, 'error': 'Unauthorized'})
    data = request.json; links = get_links()
    links.append({'id': len(links)+1, 'name': data['name'], 'url': data['url'],
                  'icon': data.get('icon','fas fa-link'),
                  'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
    save_links(links); return jsonify({'success': True})

@app.route('/delete_link/<int:link_id>', methods=['POST'])
def delete_link(link_id):
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'success': False, 'error': 'Unauthorized'})
    save_links([l for l in get_links() if l['id']!=link_id])
    return jsonify({'success': True})

@app.route('/add_player', methods=['POST'])
def add_player():
    if 'user_id' not in session: return jsonify({'success': False, 'error': 'Unauthorized'})
    data = request.json
    bot_id = data['bot_id']; player_uid = data['player_uid']; duration = data['duration']
    bot = next((b for b in get_bots() if b['id']==bot_id), None)
    if not bot or (bot['user_id']!=session['user_id'] and not session.get('is_admin')):
        return jsonify({'success': False, 'error': 'Unauthorized'})
    if duration.endswith('d'):
        expiry = datetime.now() + timedelta(days=int(duration[:-1]))
    elif duration.endswith('h'):
        expiry = datetime.now() + timedelta(hours=int(duration[:-1]))
    else:
        return jsonify({'success': False, 'error': 'صيغة خاطئة استخدم d للأيام أو h للساعات'})
    result = send_friend_request_via_api(bot['uid'], bot['password'], player_uid)
    if result.get('status') == 'success':
        info = result.get('player_info', {})
        players = get_players()
        new_player = {
            'id': len(players)+1, 'bot_uid': bot['uid'], 'bot_id': bot_id,
            'uid': player_uid, 'name': info.get('name','غير معروف'),
            'level': info.get('level','N/A'), 'region': info.get('region','N/A'),
            'added_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'expiry_date': expiry.strftime('%Y-%m-%d %H:%M:%S'),
            'duration': duration, 'status': 'added'
        }
        players.append(new_player); save_players(players)
        return jsonify({'success': True, 'player': new_player,
                        'message': result.get('message','✅ تم إرسال طلب الصداقة'),
                        'api_response': result})
    return jsonify({'success': False, 'error': result.get('message','❌ حدث خطأ'),
                    'player_name': result.get('player_info',{}).get('name', player_uid),
                    'api_response': result})

@app.route('/remove_player', methods=['POST'])
def remove_player():
    if 'user_id' not in session: return jsonify({'success': False, 'error': 'Unauthorized'})
    data = request.json
    player = next((p for p in get_players() if p['id']==data['player_id']), None)
    if not player: return jsonify({'success': False, 'error': 'اللاعب غير موجود'})
    bot = next((b for b in get_bots() if b['uid']==player['bot_uid']), None)
    if not bot or (bot['user_id']!=session['user_id'] and not session.get('is_admin')):
        return jsonify({'success': False, 'error': 'Unauthorized'})
    result = remove_friend_via_api(bot['uid'], bot['password'], player['uid'])
    if result.get('status') == 'success':
        save_players([p for p in get_players() if p['id']!=data['player_id']])
        return jsonify({'success': True, 'message': result.get('message','✅ تم الحذف بنجاح'),
                        'api_response': result})
    msg = result.get('message','')
    if "غير موجود" in msg.lower() or "not found" in msg.lower():
        save_players([p for p in get_players() if p['id']!=data['player_id']])
        return jsonify({'success': True,
                        'message': f"✅ تم حذف {player['name']} (لم يكن في قائمة الأصدقاء)",
                        'api_response': result})
    return jsonify({'success': False, 'error': msg or '❌ خطأ',
                    'player_name': player['name'], 'api_response': result})

@app.route('/check_player_status', methods=['POST'])
def check_player_status():
    if 'user_id' not in session: return jsonify({'success': False, 'error': 'Unauthorized'})
    data = request.json
    bot = next((b for b in get_bots() if b['id']==data['bot_id']), None)
    if not bot or (bot['user_id']!=session['user_id'] and not session.get('is_admin')):
        return jsonify({'success': False, 'error': 'Unauthorized'})
    existing = next((p for p in get_players()
                     if p['bot_uid']==bot['uid'] and p['uid']==data['player_uid']), None)
    return jsonify({'success': True, 'is_added': existing is not None, 'player': existing})

@app.route('/bulk_add', methods=['POST'])
def bulk_add():
    if 'user_id' not in session: return jsonify({'success': False, 'error': 'Unauthorized'})
    data = request.json
    bot = next((b for b in get_bots() if b['id']==data['bot_id']), None)
    if not bot or (bot['user_id']!=session['user_id'] and not session.get('is_admin')):
        return jsonify({'success': False, 'error': 'Unauthorized'})
    duration = data['duration']
    if duration.endswith('d'):   expiry = datetime.now()+timedelta(days=int(duration[:-1]))
    elif duration.endswith('h'): expiry = datetime.now()+timedelta(hours=int(duration[:-1]))
    else: return jsonify({'success': False, 'error': 'صيغة خاطئة'})
    added, failed = [], []
    for player_uid in data['players']:
        try:
            r = send_friend_request_via_api(bot['uid'], bot['password'], player_uid)
            info = r.get('player_info', {})
            name = info.get('name', player_uid)
            if r.get('status')=='success':
                players = get_players()
                np_ = {'id': len(players)+1, 'bot_uid': bot['uid'], 'bot_id': data['bot_id'],
                       'uid': player_uid, 'name': name,
                       'level': info.get('level','N/A'), 'region': info.get('region','N/A'),
                       'added_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                       'expiry_date': expiry.strftime('%Y-%m-%d %H:%M:%S'),
                       'duration': duration, 'status': 'added'}
                players.append(np_); save_players(players)
                added.append({'uid': player_uid, 'name': name, 'message': r.get('message','✅')})
            else:
                failed.append({'uid': player_uid, 'name': name, 'error': r.get('message','❌')})
        except Exception as e:
            failed.append({'uid': player_uid, 'name': 'غير معروف', 'error': f'❌ {e}'})
    return jsonify({'success': True, 'added': added, 'failed': failed,
                    'message': f'✅ تم {len(added)}، فشل {len(failed)}'})

@app.route('/bulk_remove', methods=['POST'])
def bulk_remove():
    if 'user_id' not in session: return jsonify({'success': False, 'error': 'Unauthorized'})
    data = request.json
    bot = next((b for b in get_bots() if b['id']==data['bot_id']), None)
    if not bot or (bot['user_id']!=session['user_id'] and not session.get('is_admin')):
        return jsonify({'success': False, 'error': 'Unauthorized'})
    players = get_players(); removed, failed = [], []
    for pid in data['player_ids']:
        p = next((x for x in players if x['id']==pid), None)
        if not p: continue
        r = remove_friend_via_api(bot['uid'], bot['password'], p['uid'])
        if r.get('status')=='success' or "غير موجود" in r.get('message','').lower():
            players = [x for x in players if x['id']!=pid]; save_players(players)
            removed.append({'uid': p['uid'], 'name': p['name'], 'message': r.get('message','✅')})
        else:
            failed.append({'uid': p['uid'], 'name': p['name'], 'error': r.get('message','❌')})
    return jsonify({'success': True, 'removed': removed, 'failed': failed,
                    'message': f'✅ تم حذف {len(removed)}، فشل {len(failed)}'})


@app.route('/player_info/<player_uid>')
def get_player_info_route(player_uid):
    try:
        name, region, level = fs_get_player_info(player_uid)
        return jsonify({'success': True, 'name': name, 'region': region,
                        'level': level, 'uid': player_uid})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e), 'uid': player_uid})

@app.route('/friend/add')
def friend_add_api():
    aid = request.args.get('uid'); pw = request.args.get('password'); tid = request.args.get('target')
    if not all([aid,pw,tid]): return jsonify({"status":"error","message":"معلمات ناقصة"})
    r = send_friend_request_via_api(aid, pw, tid)
    return jsonify({"status": r.get('status','error'), "message": r.get('message',''),
                    "player_info": r.get('player_info', {})})

@app.route('/friend/remove')
def friend_remove_api():
    aid = request.args.get('uid'); pw = request.args.get('password'); tid = request.args.get('target')
    if not all([aid,pw,tid]): return jsonify({"status":"error","message":"معلمات ناقصة"})
    r = remove_friend_via_api(aid, pw, tid)
    return jsonify({"status": r.get('status','error'), "message": r.get('message',''),
                    "player_info": r.get('player_info', {})})

@app.route('/friend/info')
def friend_info_api():
    tid = request.args.get('target')
    if not tid: return jsonify({"status":"error","message":"معلمات ناقصة"})
    name, region, level = fs_get_player_info(tid)
    return jsonify({"status":"success",
                    "player_info":{"name":name,"id":tid,"level":level,"region":region}})

@app.route('/friend/token')
def friend_token_api():
    aid = request.args.get('uid'); pw = request.args.get('password')
    if not all([aid,pw]): return jsonify({"status":"error","message":"معلمات ناقصة"})
    token = fs_fetch_jwt_token_direct(aid, pw)
    if token: return jsonify({"status":"success","token":token,"message":"✅ تم"})
    return jsonify({"status":"error","message":"❌ فشل جلب التوكن"})

@app.route('/friend/test')
def friend_test_api():
    return jsonify({"status":"success","message":"خدمة الأصدقاء تعمل",
                    "version":"OB52","timestamp": datetime.now().isoformat()})

@app.route('/api/status')
def api_status():
    return jsonify({"status":"success","message":"جميع الخدمات تعمل",
                    "timestamp": datetime.now().isoformat()})


def _human_size(n):
    for unit in ['B','KB','MB','GB']:
        if n < 1024.0: return f"{n:.1f} {unit}"
        n /= 1024.0
    return f"{n:.1f} TB"

def _safe_xL9BI7E_path(filename):
    """منع الخروج من مجلد xL9BI7E (path traversal)."""
    filename = filename.replace('\\', '/').lstrip('/')
    abs_path = os.path.abspath(os.path.join(LONELY_SOURCE, filename))
    if not abs_path.startswith(os.path.abspath(LONELY_SOURCE) + os.sep) \
       and abs_path != os.path.abspath(LONELY_SOURCE):
        return None
    return abs_path

@app.route('/admin/bot_files', methods=['GET'])
def admin_bot_files_list():
    """قائمة جميع الملفات داخل مجلد xL9BI7E (بشكل مسطح: subdir/file)."""
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'success': False, 'error': 'Unauthorized'})
    files = []
    if os.path.isdir(LONELY_SOURCE):
        for root, _, fnames in os.walk(LONELY_SOURCE):
            for name in fnames:
                full = os.path.join(root, name)
                rel  = os.path.relpath(full, LONELY_SOURCE).replace('\\','/')
                try:
                    st = os.stat(full)
                    files.append({
                        'name': rel,
                        'size': st.st_size,
                        'size_human': _human_size(st.st_size),
                        'mtime': datetime.fromtimestamp(st.st_mtime).strftime('%Y-%m-%d %H:%M')
                    })
                except: pass
    files.sort(key=lambda x: x['name'].lower())
    return jsonify({'success': True, 'files': files, 'path': LONELY_SOURCE})

@app.route('/admin/bot_files/upload', methods=['POST'])
def admin_bot_files_upload():
    """رفع ملف منفرد إلى مجلد xL9BI7E (يستبدل إن وجد)."""
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'success': False, 'error': 'Unauthorized'})
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'لا يوجد ملف'})
    f = request.files['file']
    if not f.filename: return jsonify({'success': False, 'error': 'اسم الملف فارغ'})
                                           
    target = _safe_xL9BI7E_path(f.filename)
    if not target: return jsonify({'success': False, 'error': 'مسار غير مسموح'})
    os.makedirs(os.path.dirname(target), exist_ok=True)
    f.save(target)
    return jsonify({'success': True, 'name': f.filename})

@app.route('/admin/bot_files/upload_zip', methods=['POST'])
def admin_bot_files_upload_zip():
    """رفع ZIP وفك ضغطه في مجلد xL9BI7E. replace=1 يحذف المحتوى الموجود أولاً."""
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'success': False, 'error': 'Unauthorized'})
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'لا يوجد ملف'})
    f = request.files['file']
    if not f.filename.lower().endswith('.zip'):
        return jsonify({'success': False, 'error': 'الملف ليس ZIP'})
    replace = request.form.get('replace', '0') == '1'
    try:
        data = f.read()
        zf = zipfile.ZipFile(BytesIO(data))
    except Exception as e:
        return jsonify({'success': False, 'error': f'ZIP غير صالح: {e}'})

    if replace and os.path.isdir(LONELY_SOURCE):
                                  
        for entry in os.listdir(LONELY_SOURCE):
            ep = os.path.join(LONELY_SOURCE, entry)
            try:
                if os.path.isdir(ep): shutil.rmtree(ep)
                else: os.remove(ep)
            except: pass

                                                                            
    names = [n for n in zf.namelist() if not n.endswith('/')]
    if not names:
        return jsonify({'success': False, 'error': 'ZIP فارغ'})
    top_parts = set(n.split('/',1)[0] for n in names if '/' in n)
    only_top = None
    if len(top_parts) == 1 and all(n.startswith(list(top_parts)[0]+'/') for n in names):
        only_top = list(top_parts)[0]

    count = 0
    for info in zf.infolist():
        if info.is_dir(): continue
        rel = info.filename.replace('\\','/')
        if only_top and rel.startswith(only_top+'/'):
            rel = rel[len(only_top)+1:]
        if not rel: continue
        target = _safe_xL9BI7E_path(rel)
        if not target: continue
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with zf.open(info) as src, open(target, 'wb') as dst:
            shutil.copyfileobj(src, dst)
        count += 1
    return jsonify({'success': True, 'count': count})

@app.route('/admin/bot_files/download/<path:filename>')
def admin_bot_files_download(filename):
    if 'user_id' not in session or not session.get('is_admin'):
        return abort(403)
    target = _safe_xL9BI7E_path(filename)
    if not target or not os.path.isfile(target): return abort(404)
    return send_file(target, as_attachment=True,
                     download_name=os.path.basename(target))

@app.route('/admin/bot_files/delete/<path:filename>', methods=['POST'])
def admin_bot_files_delete(filename):
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'success': False, 'error': 'Unauthorized'})
    target = _safe_xL9BI7E_path(filename)
    if not target or not os.path.isfile(target):
        return jsonify({'success': False, 'error': 'الملف غير موجود'})
    try:
        os.remove(target)
                              
        parent = os.path.dirname(target)
        while parent.startswith(os.path.abspath(LONELY_SOURCE)) \
              and parent != os.path.abspath(LONELY_SOURCE) and not os.listdir(parent):
            os.rmdir(parent); parent = os.path.dirname(parent)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/admin/bot_files/rename', methods=['POST'])
def admin_bot_files_rename():
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'success': False, 'error': 'Unauthorized'})
    data = request.json or {}
    old_name = data.get('old_name'); new_name = data.get('new_name')
    if not old_name or not new_name:
        return jsonify({'success': False, 'error': 'بيانات ناقصة'})
    src = _safe_xL9BI7E_path(old_name); dst = _safe_xL9BI7E_path(new_name)
    if not src or not dst: return jsonify({'success': False, 'error': 'مسار غير مسموح'})
    if not os.path.isfile(src): return jsonify({'success': False, 'error': 'الملف غير موجود'})
    if os.path.exists(dst):    return jsonify({'success': False, 'error': 'الاسم الجديد موجود بالفعل'})
    try:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        os.rename(src, dst)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


if __name__ == '__main__':
    print("="*70)
    print("🚀 L9BI7E Bot Manager (Single-File Edition)")
    print("="*70)
    print(f"📁 Base Directory:   {BASE_DIR}")
    print(f"📁 Database:         {DATABASE_DIR}")
    print(f"📁 XL9BI7E Template:  {LONELY_SOURCE}")
    print(f"📁 Bots Storage:     {USERS_STORAGE}")
    print("="*70)
    print("👤 Admin: 9sfwiw / yasser2004@")
    print("="*70)
    if not os.path.exists(LONELY_SOURCE) or not os.listdir(LONELY_SOURCE):
        print("⚠️  مجلد 'xL9BI7E' فارغ. ادخل لوحة الأدمن وارفع ملفات قالب البوت")
        print("    (يفضل رفعها كـ ZIP من قسم 'إدارة ملفات بوت الصديق').")
    else:
        n = sum(len(files) for _,_,files in os.walk(LONELY_SOURCE))
        print(f"✅ مجلد 'xL9BI7E' جاهز ويحتوي على {n} ملف")
    print("="*70)
    try:
        tn, tr, tl = fs_get_player_info("123456789")
        print(f"🧪 friend_service: OK (test: {tn})")
    except Exception as e:
        print(f"⚠️  friend_service warning: {e}")
    print("="*70)
    app.run(host='0.0.0.0', port=7789, debug=False, threaded=True)
