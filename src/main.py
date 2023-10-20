from utils import crawling_PHPSESSID, reserve_badminton_court
import sys
import json
import argparse
from apscheduler.schedulers.blocking import BlockingScheduler

parser = argparse.ArgumentParser(description='manual to this script')

parser.add_argument("--id", type=str)
parser.add_argument("--password", type=str)
parser.add_argument("--field1", type=int)
parser.add_argument("--time1", type=int)
parser.add_argument("--field2", type=int)
parser.add_argument("--time2", type=int)
parser.add_argument("--linetoken", type=str)
args = parser.parse_args()

def reserve():
    reserve_badminton_court(args.field1-1, args.time1-1, args.field2-1, args.time2-1, args.linetoken)

def preprocess():
    try:
        ID = args.id + '\t'
        PASSWORD = args.password

        PHPSESSID = crawling_PHPSESSID(ID, PASSWORD)

        with open("cookie.json", "w") as cookie_file:
            json_object = json.dumps({"PHPSESSID":PHPSESSID}, indent=1)
            cookie_file.write(json_object)
        
    except ValueError as err:
        sys.stderr.write(
            f"setting format is wrong, please check and try again.\nError: {err}\n")
    except Exception as err:
        sys.stderr.write(f"Unexpected Error. \nErr: {err}\n")


if __name__ == "__main__":
    print("Waiting for scheduling...")
    scheduler = BlockingScheduler(timezone="Asia/Shanghai")

    scheduler.add_job(preprocess, 'cron', day_of_week='mon,thu,fri,sat,sun', hour=23, minute=59)
    scheduler.add_job(reserve, 'cron', day_of_week='mon,thu,fri,sat,sun', hour=23, minute=59, second=59)

    scheduler.start()