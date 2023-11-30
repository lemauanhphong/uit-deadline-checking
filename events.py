import html
import time
import apprise
from datetime import datetime, timedelta
import pytz
import requests
import re
from config import *
from traceback import print_exc

URL = "https://courses.uit.edu.vn"
SESSKEY = ""

apobj = apprise.Apprise()
apobj.add("windows://")

def login():
    global session, USERNAME, PASSWORD, SESSKEY

    resp = session.get(f"{URL}/login/index.php")

    token = re.search(
        '<input type="hidden" name="logintoken" value="(\w{32})', resp.text
    ).group(1)

    data = {
        "username": USERNAME,
        "password": PASSWORD,
        "logintoken": token,
        "anchor": "",
    }
    resp = session.post(f"{URL}/login/index.php", data)

    SESSKEY = re.search('"sesskey":"([^"]+)"', resp.text).group(1)


def get_calendar():
    global session

    date = datetime.now(pytz.timezone("Asia/Ho_Chi_Minh"))
    for i in range(7):
        day = int(date.strftime("%d"))
        month = int(date.strftime("%m"))
        year = int(date.strftime("%Y"))
        params = {"sesskey": SESSKEY}
        json = [
            {
                "methodname": "core_calendar_get_calendar_day_view",
                "args": {"year": year, "month": month, "day": day},
            }
        ]
        resp = session.post(f"{URL}/lib/ajax/service.php", params=params, json=json)
        # print(i, day, month, year,resp.json()[0])
        events = resp.json()[0]["data"]["events"]

        for event in events:
            noti = f"TODAY{'' if i == 0 else f' + {i}'}: "
            noti += f" {event['name']} - {datetime.fromtimestamp(event['timestart'])}"
            noti = html.unescape(noti)
            title = html.unescape(f"UIT - Deadline: {event['course']['fullname']}")
            apobj.notify(body=noti, title=title)
        date += timedelta(days=1)

def logout():
    global session, SESSKEY

    params = {"sesskey": SESSKEY}
    session.get(f"{URL}/login/logout.php", params=params)

if __name__ == '__main__':
    while True:
        try:
            session = requests.Session()
            login()
            get_calendar()
            logout()
            time.sleep(60 * 60)
        except:
            time.sleep(2 * 60)
