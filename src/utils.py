import time
import datetime

from colorama import init, Fore, Style

import requests
import sys
import json
import asyncio

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options as ChromeOptions

from bs4 import BeautifulSoup



init(convert=True)  # colorama init

NOW_TIME = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

loop = asyncio.get_event_loop()
flag = False


def log(log_message, time_limit=False):
    if time_limit:
        time.sleep(0.1)
    now_time = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print(f"[Log: {now_time}] {log_message}")

    '''with open("LOG_"+str(NOW_TIME)+".txt", "a", encoding="utf-8") as log_file:
        log_file.write(f"[Log: {now_time}] {log_message}\n")
        '''

    return


def crawling_PHPSESSID(ID, PASSWORD):
    log("open the webdriver")
    log("setting options (NTHU_OAuth_Decaptcha.crx)")
    chrome_options = ChromeOptions()
    # chrome_options.add_argument('--headless')
    # chrome_options.add_argument('--disable-gpu')
    chrome_options.add_extension("NTHU_OAuth_Decaptcha.crx")
    nthualb = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    log("set implicitly waitting time as 10 secs")
    nthualb.implicitly_wait(10)
    log("enter the website to login")
    nthualb.get("https://oauth.ccxp.nthu.edu.tw/v1.1/authorize.php?client_id=nthualb&response_type=code")

    log("waiting for website done")
    WebDriverWait(nthualb, 10).until(EC.presence_of_element_located((By.ID, "id")))
    log("waiting for the extension work (5 secs)")
    time.sleep(5)
    log("get account_blank")
    # account_blank = nthualb.find_element_by_id("id")
    account_blank = nthualb.find_element(By.ID, "id")
    log("send account_blank")
    account_blank.send_keys(ID + PASSWORD)

    log("get login_button")
    # login_button = nthualb.find_element_by_class_name("btn-login")
    login_button = nthualb.find_element(By.CLASS_NAME, "btn-login")
    log("click login_button")
    login_button.click()
    
    log("enter the website to last day")
    WebDriverWait(nthualb, 10).until(EC.presence_of_element_located((By.ID, "reservation")))
    nthualb.get("https://nthualb.url.tw/reservation/reservation?d=4")
    time.sleep(1)
    if str(nthualb.page_source).find("預約") == -1:
        log(f"{Fore.RED+Style.BRIGHT}登入失敗，請檢查登入資料是否正確。{Fore.RESET+Style.RESET_ALL}")
        exit()
    else:
        log(f"{Fore.GREEN+Style.BRIGHT}登入成功。{Fore.RESET+Style.RESET_ALL}")

    PHPSESSID = nthualb.get_cookie("PHPSESSID")

    log(f"get PHPSESSION = {PHPSESSID['value']}")
    log("close driver")
    nthualb.close()

    return PHPSESSID["value"]

async def post_reservation(url, headers, json):
    # response = await requests.post(url=url, headers=headers, json=json)
    time.sleep(1)
    response = await loop.run_in_executor(None, lambda: requests.post(url=url, headers=headers, json=json))

    html_data = BeautifulSoup(response.text, "html.parser")
    if response.status_code == 200 and str(html_data) == "ok":
        log(f"reserved {json} {Fore.GREEN+Style.BRIGHT}successfully{Fore.RESET+Style.RESET_ALL},"
            f"see more detail in nthualb website.")
        global flag
        flag = True
    elif str(html_data) is None:
        log(f"reserved {json} {Fore.RED+Style.BRIGHT}FAIL{Fore.RESET+Style.RESET_ALL}."
            f"Because {Fore.RED+Style.BRIGHT}the session isn't work "
            f"(i.e. you didn't login successfully){Fore.RESET+Style.RESET_ALL}.")
    else:
        log(f"reserved {json} {Fore.RED+Style.BRIGHT}FAIL{Fore.RESET+Style.RESET_ALL}."
            f"Because {Fore.RED+Style.BRIGHT}{html_data}{Fore.RESET+Style.RESET_ALL}.")


def reserve_badminton_court(FIELD1, TIME1, FIELD2, TIME2, TOKEN):  
    DEBUG = True

    init(convert=True)  # colorama init

    TODAY = (
        int(datetime.datetime.now().strftime("%Y")),
        int(datetime.datetime.now().strftime("%m")),
        int(datetime.datetime.now().strftime("%d")))

    RESERVE_TIME = datetime.datetime(year=TODAY[0], month=TODAY[1], day=TODAY[2]) \
        + datetime.timedelta(days=4 if not DEBUG else 4)

    RESERVE_TIME = str(int(RESERVE_TIME.timestamp()))

    URL = "https://nthualb.url.tw/reservation/api/reserve_field"

    try:
        with open("headers.json") as headers_file:
            raw_header = json.load(headers_file)
            post_header = raw_header["post_header"]
    except FileNotFoundError:
        sys.stderr.write(
            "\"header.json\" not found, please add it and try again.\n")
    except Exception as err:
        sys.stderr.write(f"Unexpected Error. \nErr: {err}\n")

    try:
        with open("cookie.json") as cookie_file:
            cookie = json.load(cookie_file)
            post_header["cookie"] = "PHPSESSID=" + cookie["PHPSESSID"]

    except FileNotFoundError:
        sys.stderr.write(
            "\"cookie.json\" not found, please add it and try again.\n")
    except Exception as err:
        sys.stderr.write(f"Unexpected Error. \nErr: {err}\n")

    

    tasks = []
    for info in [(TIME1, FIELD1), (TIME2, FIELD2)]:
        post_header["content-length"] = f"{42+len(str(info[0]))+len(str(info[1]))}"

        data = {
            "time": str(info[0]),
            "field": str(info[1]),
            "date": RESERVE_TIME
        }

        log(f"start reserving {data}")
        log("sending POST request")
        # raw_data = requests.post(url=URL, headers=post_header, json=data)
        for _ in range(5):
            tasks.append(loop.create_task(
                post_reservation(URL, post_header, data)))
    
    loop.run_until_complete(asyncio.wait(tasks))

    log(f"{Style.BRIGHT}FIN{Style.RESET_ALL}")
    
    if flag:
        notify(TOKEN, "Successfully!!\nLink: https://nthualb.url.tw/reservation/reservation?d=4")
    else:
        notify(TOKEN, "Fail!!\nLink: https://nthualb.url.tw/reservation/reservation?d=4")


def get_server_time(URL, get_header):
    get_respond = requests.get(url=URL, headers=get_header)
    raw_server_date = str(get_respond.headers["date"])
    SERVER_TIME = datetime.datetime.strptime(raw_server_date, "%a, %d %b %Y %H:%M:%S %Z") \
        + datetime.timedelta(hours=8)

    return SERVER_TIME


def notify(token, msg):
    url = 'https://notify-api.line.me/api/notify'
    headers = {
        'Authorization': 'Bearer ' + token 
    }
    data = {
        'message':msg
    }
    data = requests.post(url, headers=headers, data=data)