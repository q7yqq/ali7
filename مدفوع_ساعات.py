#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
import os
import sys
import time
import re
import json
import secrets
import string
from datetime import datetime
import datetime as dt
from threading import Thread, Lock

# تثبيت المكتبات المطلوبة تلقائياً
try:
    import colorama
    import requests
    from user_agent import generate_user_agent as gg
except ImportError:
    os.system('pip3 install colorama requests user_agent')
    import colorama
    import requests
    from user_agent import generate_user_agent as gg

from colorama import Fore, Style

colorama.init(autoreset=True)

# -------------------- ألوان الواجهة الجديدة --------------------
DARK_GRAY = '\033[90m'     # للحدود (باهت جداً لا يشتت العين)
SOFT_BLUE = '\033[36m'     # أزرق سماوي خافت للعناوين
PURE_WHITE = '\033[97m'    # أبيض ناصع للأرقام فقط لبروزها
RESET_COLOR = '\033[0m'

# -------------------- دالة تقدير السنة من id --------------------
def estimate_year_from_id(user_id):
    """
    تحويل رقم id (pk) إلى سنة تقريبية لإنشاء الحساب.
    النطاقات محدثة حسب الأرقام المعروفة.
    """
    try:
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
            (30577684866, 2020),
            (48009087498, 2021),
            (51994527687, 2022),
            (60000000000, 2023)  # تقديري
        ]
        for upper, year in ranges:
            if user_id <= upper:
                return year
        return 2024  # أحدث من 2023
    except Exception:
        return None

# -------------------- التحقق من انتهاء الصلاحية --------------------
def check_expiry():
    today = dt.date.today()
    if today.month == 12:
        next_month = 1
        next_year = today.year + 1
    else:
        next_month = today.month + 1
        next_year = today.year
    expiry_date = dt.date(next_year, next_month, 2)
    if today >= expiry_date:
        print(Fore.RED + "\nانتهت النسخه المجانيه راسل المطور علي بسام @as_wqt")
        sys.exit(0)

# -------------------- عدادت وإحصائيات --------------------
total_generated = 0
instagram_taken = 0
instagram_not_taken = 0
google_available = 0
google_unavailable = 0
google_errors = 0
counters_lock = Lock()

# -------------------- متغيرات الجلسة --------------------
BOT_TOKEN = ""
CHAT_ID = ""
SELECTED_RANGES = []          # قائمة النطاقات المختارة (كل عنصر عبارة عن (max_id, year))
DOMAIN = "@gmail.com"
THREADS = 20

# -------------------- دالة توليد اسم مستخدم مع id حقيقي --------------------
def generate_username_with_id(max_id):
    """
    محاولة العثور على اسم مستخدم صالح ضمن نطاق معين.
    تعيد (username, real_user_id, estimated_year) أو (None, None, None) عند الفشل.
    """
    attempts = 0
    while attempts < 30:
        try:
            # توليد user_id عشوائي ضمن النطاق (1 إلى max_id)
            random_id = random.randint(1, max_id)
            lsd = ''.join(random.choices(string.ascii_letters + string.digits, k=4))
            variables = json.dumps({"id": str(random_id), "render_surface": "PROFILE"})
            data = {
                "lsd": lsd,
                "variables": variables,
                "doc_id": "25618261841150840"
            }
            response = requests.post(
                "https://www.instagram.com/api/graphql",
                headers={"X-FB-LSD": lsd, "User-Agent": gg()},
                data=data,
                timeout=10
            )
            response.raise_for_status()
            result = response.json()
            if 'data' in result and 'user' in result['data']:
                user_data = result['data']['user']
                username = user_data.get('username')
                real_id = user_data.get('id')
                if username and real_id and '_' not in username:
                    # تقدير السنة من id الحقيقي
                    year = estimate_year_from_id(int(real_id))
                    return username, int(real_id), year
        except Exception:
            pass
        attempts += 1
    return None, None, None

# -------------------- دالة توليد عشوائي من جميع النطاقات --------------------
def generate_random_username():
    """اختيار نطاق عشوائي من القائمة المختارة ومحاولة توليد اسم"""
    if not SELECTED_RANGES:
        return None, None, None
    max_id, _ = random.choice(SELECTED_RANGES)  # نستخدم max_id فقط
    return generate_username_with_id(max_id)

# -------------------- جلب إحصائيات إنستغرام (متابعين) من صفحة الويب --------------------
def get_instagram_stats(username):
    url = f"https://www.instagram.com/{username}/"
    headers = {'User-Agent': gg()}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code != 200:
            return None, None
        pattern = r'<meta\s+property="og:description"\s+content="([^"]+)"'
        match = re.search(pattern, resp.text)
        if match:
            desc = match.group(1)
            parts = desc.split(',')
            followers_str = parts[0].strip() if len(parts) > 0 else ''
            following_str = parts[1].strip() if len(parts) > 1 else ''
            followers_num = re.search(r'([\d.,]+k?)\s*Followers', followers_str, re.IGNORECASE)
            following_num = re.search(r'([\d.,]+k?)\s*Following', following_str, re.IGNORECASE)
            followers = followers_num.group(1) if followers_num else 'N/A'
            following = following_num.group(1) if following_num else 'N/A'
            return followers, following
        else:
            return None, None
    except Exception:
        return None, None

# -------------------- إرسال إلى تليجرام بالتنسيق المطلوب --------------------
def send_to_telegram(email, username, followers, following, year, user_id):
    profile_url = f"https://www.instagram.com/{username}/"
    # تاريخ الإنشاء (نفترض أول يوم في السنة)
    creation_date = f"{year}-01-01" if year else "Unknown"
    message = f"""
📋 ACCOUNT INFO
━━━━━━━━━━━━━━
🆔 User: {username}
📧 MAIL: {email}
🍺 Url: {profile_url}
🗓 DATE: {creation_date}
📊 FOLLOWERS: {followers}

━━━━━━━━━━━━━━
✅ Ali BssaM @as_wqt
"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    try:
        requests.post(url, data=payload, timeout=5)
    except Exception as e:
        print(Fore.RED + f"[-] Telegram send error: {e}")

# -------------------- فحص إنستغرام (هل البريد مسجل) --------------------
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

# -------------------- الحصول على توكن جوجل --------------------
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
    except Exception as e:
        return None, None

# -------------------- فحص جوجل (هل اسم المستخدم متاح) --------------------
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

# -------------------- شاشة العرض الحية (الواجهة الجديدة الهادئة) --------------------
def print_minimal_dashboard():
    # نأخذ القيم من المتغيرات العامة
    with counters_lock:
        created = total_generated
        total_ops = instagram_taken + instagram_not_taken
        ig_pass = instagram_taken
        ig_fail = instagram_not_taken
        g_valid = google_available
        g_locked = google_unavailable
        err = google_errors

    head = f"{DARK_GRAY}──────────────────────────────────────────────────────────"
    
    dashboard = f"""
{head}
{DARK_GRAY}  User: {SOFT_BLUE}Ali Bssam {DARK_GRAY}│ Status: {SOFT_BLUE}Active{DARK_GRAY} │ Target: {SOFT_BLUE}IG + Gmail
{head}

{DARK_GRAY}  [ SESSION ]
{DARK_GRAY}  Created Usernames  : {PURE_WHITE}{created:<6}
{DARK_GRAY}  Total Operations   : {PURE_WHITE}{total_ops:<6}

{DARK_GRAY}  [ RESULTS ]
{DARK_GRAY}  Instagram  {DARK_GRAY}»  {SOFT_BLUE}Success: {PURE_WHITE}{ig_pass:<5} {DARK_GRAY}│ {SOFT_BLUE}Failed: {PURE_WHITE}{ig_fail:<5}
{DARK_GRAY}  Gmail      {DARK_GRAY}»  {SOFT_BLUE}Valid:   {PURE_WHITE}{g_valid:<5} {DARK_GRAY}│ {SOFT_BLUE}Locked: {PURE_WHITE}{g_locked:<5}
{DARK_GRAY}  Errors     {DARK_GRAY}»  {PURE_WHITE}{err:<5}

{head}
{DARK_GRAY}  Logs saved to: {PURE_WHITE}valid_accounts.txt {DARK_GRAY}| Press Ctrl+C to stop
{RESET_COLOR}"""
    # مسح الشاشة قبل الطباعة (اختياري للحصول على تحديث نظيف)
    os.system('cls' if os.name == 'nt' else 'clear')
    print(dashboard)

def status_display():
    while True:
        print_minimal_dashboard()
        time.sleep(1)

# -------------------- دالة العامل (Worker) --------------------
def worker():
    global total_generated, instagram_taken, instagram_not_taken
    global google_available, google_unavailable, google_errors

    while True:
        if not SELECTED_RANGES:
            time.sleep(1)
            continue

        # توليد اسم مستخدم مع id حقيقي وسنة تقديرية
        username, real_id, year = generate_random_username()
        if not username:
            continue

        with counters_lock:
            total_generated += 1

        # تخطي الأسماء التي تحتوي على '_' (اختياري)
        if '_' in username:
            continue

        email = username + DOMAIN

        # فحص إنستغرام
        ig_registered = insta_check(email)
        if ig_registered:
            with counters_lock:
                instagram_taken += 1

            google_status = google_check(username)
            if google_status is True:
                followers, following = get_instagram_stats(username)
                if followers is None:
                    followers = "غير معروف"
                    following = "غير معروف"

                with counters_lock:
                    google_available += 1

                # إرسال إلى تليجرام وحفظ
                send_to_telegram(email, username, followers, following, year, real_id)
                with open("valid_accounts.txt", "a", encoding='utf-8') as f:
                    f.write(f"{email} | Year: {year} | Followers: {followers} | ID: {real_id}\n")
                # يمكن إضافة طباعة سريعة للحالة (اختياري) لكن شاشة العرض كافية
            elif google_status is False:
                with counters_lock:
                    google_unavailable += 1
            else:
                with counters_lock:
                    google_errors += 1
        else:
            with counters_lock:
                instagram_not_taken += 1

# -------------------- الواجهة الرئيسية --------------------
def main():
    global BOT_TOKEN, CHAT_ID, SELECTED_RANGES

    check_expiry()

    # عرض اللوجو (يمكن الاحتفاظ به أو استبداله بلوحة ترحيب بسيطة)
    print(DARK_GRAY + "──────────────────────────────────────────────────────────")
    print(SOFT_BLUE + "  Ali BssaM Instagram + Gmail Validator")
    print(DARK_GRAY + "──────────────────────────────────────────────────────────" + RESET_COLOR)

    # إدخال التوكن والايدي
    BOT_TOKEN = input(SOFT_BLUE + "Enter your Telegram Bot Token: " + RESET_COLOR).strip()
    CHAT_ID = input(SOFT_BLUE + "Enter your Telegram Chat ID: " + RESET_COLOR).strip()

    # عرض خيارات السنوات (نطاقات ID القصوى)
    print(DARK_GRAY + "\nاختر نطاق الصيد (أدخل رقم):" + RESET_COLOR)
    print(" 1. 2010  (ID <= 1,279,000)")
    print(" 2. 2011  (ID <= 17,750,000)")
    print(" 3. 2012  (ID <= 279,760,000)")
    print(" 4. 2013  (ID <= 900,990,000)")
    print(" 5. 2014  (ID <= 1,629,010,000)")
    print(" 6. 2015  (ID <= 2,500,000,000)")
    print(" 7. 2016  (ID <= 3,713,668,786)")
    print(" 8. 2017  (ID <= 5,699,785,217)")
    print(" 9. 2018  (ID <= 8,597,939,245)")
    print("10. 2019  (ID <= 21,254,029,834)")
    print("11. 2020  (ID <= 30,577,684,866)")
    print("12. 2021  (ID <= 48,009,087,498)")
    print("13. 2022  (ID <= 51,994,527,687)")
    print("14. فحص عشوائي (جميع السنوات)")
    choice = input(SOFT_BLUE + "اختيارك: " + RESET_COLOR).strip()

    # تجهيز SELECTED_RANGES بناءً على الاختيار (نستخدم max_id فقط)
    RANGES_LIST = [
        1279000,
        17750000,
        279760000,
        900990000,
        1629010000,
        2500000000,
        3713668786,
        5699785217,
        8597939245,
        21254029834,
        30577684866,
        48009087498,
        51994527687,
    ]

    if choice == '14':
        SELECTED_RANGES = [(max_id, None) for max_id in RANGES_LIST]  # السنة غير مستخدمة هنا
    else:
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(RANGES_LIST):
                SELECTED_RANGES = [(RANGES_LIST[idx], None)]
            else:
                print(DARK_GRAY + "اختيار غير صحيح، سيتم استخدام العشوائي." + RESET_COLOR)
                SELECTED_RANGES = [(max_id, None) for max_id in RANGES_LIST]
        except ValueError:
            print(DARK_GRAY + "إدخال غير صحيح، سيتم استخدام العشوائي." + RESET_COLOR)
            SELECTED_RANGES = [(max_id, None) for max_id in RANGES_LIST]

    # تأكيد الاختيار
    if choice == '14':
        print(SOFT_BLUE + "تم تحديد الفحص العشوائي (جميع السنوات)." + RESET_COLOR)
    else:
        year_text = ["2010","2011","2012","2013","2014","2015","2016","2017","2018","2019","2020","2021","2022"][idx]
        print(SOFT_BLUE + f"تم تحديد سنة {year_text}." + RESET_COLOR)

    # بدء شاشة العرض
    status_thread = Thread(target=status_display, daemon=True)
    status_thread.start()

    # بدء العمال
    workers = []
    for _ in range(THREADS):
        t = Thread(target=worker, daemon=True)
        t.start()
        workers.append(t)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(DARK_GRAY + "\n──────────────────────────────────────────────────────────")
        print(SOFT_BLUE + "  Stopped by user. Final stats saved to valid_accounts.txt")
        print(DARK_GRAY + "──────────────────────────────────────────────────────────" + RESET_COLOR)
        sys.exit(0)

if __name__ == "__main__":
    main()
