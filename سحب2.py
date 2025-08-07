import requests
import random
import time
import uuid
import string
import hashlib
import base64
import json
import ms4
import re
import fake_useragent
import os
from concurrent.futures import ThreadPoolExecutor
import threading
from collections import deque
from colorama import init, Fore, Style

# تهيئة colorama ليعمل على مختلف الأنظمة
init(autoreset=True)

# حقوق المبرمج
print(f"{Fore.MAGENTA}{Style.BRIGHT}" + "#" * 50)
print(f"{Fore.MAGENTA}{Style.BRIGHT}###{Fore.YELLOW}  Coder By Ali BssaM - Telegram : @AliBssaM     {Fore.MAGENTA}###")
print(f"{Fore.MAGENTA}{Style.BRIGHT}" + "#" * 50)

# قائمة ألوان نيون
NEON_COLORS = [Fore.CYAN, Fore.GREEN, Fore.YELLOW, Fore.BLUE, Fore.MAGENTA, Fore.WHITE, Fore.RED]
color_index = 0

def get_next_color():
    global color_index
    color = NEON_COLORS[color_index % len(NEON_COLORS)]
    color_index += 1
    return color

lock = threading.Lock()
user_agent_generator = fake_useragent.FakeUserAgent()
thread_local = threading.local()

# قائمة لتخزين اليوزرات التي تم سحبها وإضافتها لقائمة الانتظار
scraped_usernames_set = set()
scraped_usernames_queue = deque()

def random_num(length=10):
    return ''.join(random.choice(string.digits) for _ in range(length))

def random_hex(length=32):
    return ''.join(random.choice('0123456789abcdef') for _ in range(length))

def random_uuid():
    return str(uuid.uuid4())

def random_user_agent():
    brands = ["Infinix", "Samsung", "Xiaomi", "Huawei", "Realme", "Oppo", "Vivo", "Tecno"]
    models = ["X692", "A52", "M21", "Note9", "Y20", "C25", "F17", "P30"]
    android_versions = ["10", "11", "12", "13"]
    build_versions = ["QP1A.190711.020", "RP1A.200720.011", "TP1A.220905.001", "SP1A.210812.016"]
    brand = random.choice(brands)
    model = random.choice(models)
    android_ver = random.choice(android_versions)
    build_ver = random.choice(build_versions)
    return f"com.zhiliaoapp.musically.go/370402 (Linux; U; Android {android_ver}; ar; {brand} {model}; Build/{build_ver}; tt-ok/3.12.13.27-ul)"

def generate_x_gorgon(ts):
    base = hashlib.md5(str(ts).encode()).hexdigest()
    return "8404" + base[:30]

def generate_x_argus(ts, device_id, iid):
    raw = f"{device_id}:{iid}:{ts}"
    hashed = hashlib.sha256(raw.encode()).digest()
    return base64.b64encode(hashed).decode()

def generate_xtt_params(params_dict):
    encoded = json.dumps(params_dict, separators=(',', ':')).encode()
    return base64.b64encode(encoded).decode()

def get_session():
    if not hasattr(thread_local, "session"):
        thread_local.session = requests.Session()
    return thread_local.session

def process_user(drk):
    try:
        ms = ms4.InfoTik.TikTok_Info(drk)
        user_id_ = ms["id"]
        url_profile = f'https://www.tiktok.com/@{drk}'
        headers_profile = {'User-Agent': user_agent_generator.random}
        session = get_session()
        rsp = session.get(url_profile, headers=headers_profile).text
        sec_user_ = re.search(r'"secUid":"([^"]+)"', rsp).group(1)

        iid = random_num(19)
        device_id = random_num(19)
        cdid = random_uuid()
        openudid = random_hex(16)
        page_token = ""
        max_time = ""
        total_count = 0
        file_path = "vip2.txt"

        print(f"{get_next_color()}{Style.BRIGHT}بدء سحب المتابعين من @{drk}...")

        while True:
            ts = int(time.time())
            headers = {
                'User-Agent': random_user_agent(),
                'x-tt-token': random_hex(96),
                'x-tt-store-region': "iq",
                'x-khronos': str(ts),
                'x-argus': generate_x_argus(ts, device_id, iid),
                'x-gorgon': generate_x_gorgon(ts),
                'X-Tt-Params': generate_xtt_params({
                    "iid": iid,
                    "device_id": device_id,
                    "cdid": cdid,
                    "ts": ts,
                    "version": "37.4.2",
                    "region": "IQ"
                }),
                'Cookie': f"install_id={iid}; device_id={device_id}; odin_tt={random_hex(64)}; sessionid={random_hex(32)}"
            }

            url = f"https://api16-normal-c-alisg.tiktokv.com/lite/v2/relation/follower/list/?" \
                  f"sss-network-channel={random_num(13)}&user_id={user_id_}&count=200&page_token={page_token}&max_time={max_time}&source_type=4" \
                  f"&request_tag_from=h5&sec_user_id={sec_user_}" \
                  f"&manifest_version_code=370402&_rticket={random_num(13)}&app_language=ar&app_type=normal" \
                  f"&iid={iid}&app_package=com.zhiliaoapp.musically.go&channel=googleplay&device_type=Infinix+X692" \
                  f"&language=ar&host_abi=arm64-v8a&locale=ar&resolution=720*1464&openudid={openudid}&update_version_code=370402" \
                  f"&ac2=wifi&cdid={cdid}&sys_region=EG&os_api=29&timezone_name=Asia%2FBaghdad&dpi=320" \
                  f"&carrier_region=IQ&ac=wifi&device_id={device_id}&os_version=10&timezone_offset=10800&version_code=370402" \
                  f"&app_name=musically_go&ab_version=37.4.2&version_name=37.4.2&device_brand=Infinix&op_region=IQ&ssmix=a" \
                  f"&device_platform=android&build_number=37.4.2&region=EG&aid=1340&ts={ts}"

            try:
                response = session.get(url, headers=headers).json()
                users = [item['unique_id'] for item in response.get('followers', [])]

                with lock:
                    with open(file_path, "a", encoding="utf-8") as f:
                        for u in users:
                            if u not in scraped_usernames_set:
                                scraped_usernames_set.add(u)
                                scraped_usernames_queue.append(u)
                                f.write(u + "\n")
                                total_count += 1
                                print(f"{get_next_color()}{Style.BRIGHT}تم سحب يوزر جديد من @{drk}: @{u}")
                                print(f"{get_next_color()}{Style.DIM}عدد المتابعين المسحوبين حتى الآن من @{drk}: {total_count}")
                            
                if not response.get("has_more"):
                    break

                page_token = response.get("next_page_token", "")
                max_time = response.get("min_time", "")
            except Exception as e:
                print(f"{Fore.RED}{Style.BRIGHT}حدث خطأ أثناء السحب من @{drk}: {e}")
                break
        print(f"{Fore.GREEN}{Style.BRIGHT}✅ تم الانتهاء من سحب المتابعين من @{drk}. إجمالي العدد: {total_count}")
    except Exception as e:
        print(f"{Fore.RED}{Style.BRIGHT}❌ حدث خطأ في معالجة المستخدم @{drk}: {e}")

def main():
    username_input = input(f"{Fore.CYAN}{Style.BRIGHT}أدخل اسم المستخدم (اليوزر) الذي تريد سحب متابعيه: {Fore.WHITE}")
    initial_usernames = [u.strip() for u in username_input.strip().split("\n") if u.strip()]

    if not initial_usernames:
        print(f"{Fore.RED}{Style.BRIGHT}❌ لم يتم إدخال أي أسماء مستخدمين.")
        return

    output_file = "vip2.txt"
    if os.path.exists(output_file):
        os.remove(output_file)
        print(f"{Fore.YELLOW}تم حذف الملف السابق {output_file}.")

    for username in initial_usernames:
        if username not in scraped_usernames_set:
            scraped_usernames_set.add(username)
            scraped_usernames_queue.append(username)
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        while True:
            if scraped_usernames_queue:
                username_to_scrape = scraped_usernames_queue.popleft()
                print(f"{get_next_color()}{Style.BRIGHT}سيتم سحب المتابعين من اليوزر الجديد: @{username_to_scrape}")
                executor.submit(process_user, username_to_scrape)
                time.sleep(5)
            else:
                print(f"{Fore.YELLOW}{Style.BRIGHT}قائمة الانتظار فارغة. جاري البحث عن يوزرات جديدة من الملف...")
                try:
                    with lock:
                        with open(output_file, "r", encoding="utf-8") as f:
                            all_scraped = f.read().splitlines()
                            new_usernames = [u for u in all_scraped if u not in scraped_usernames_set]
                            if new_usernames:
                                random_new_user = random.choice(new_usernames)
                                scraped_usernames_set.add(random_new_user)
                                scraped_usernames_queue.append(random_new_user)
                                print(f"{Fore.GREEN}تمت إضافة يوزر عشوائي من الملف: @{random_new_user}")
                            else:
                                print(f"{Fore.YELLOW}لا يوجد يوزرات جديدة في الملف. سيتم إعادة فحص القائمة بعد قليل.")
                                time.sleep(30)
                except FileNotFoundError:
                    print(f"{Fore.RED}الملف vip2.txt غير موجود. سيتم التوقف.")
                    break

if __name__ == "__main__":
    main()