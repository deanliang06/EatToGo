import subprocess
import pyautogui
import base64
from io import BytesIO
from pathlib import Path
import time
from celery.utils.log import get_logger
from dotenv import load_dotenv
from .models import ScrapeResult, Task
import pytesseract

from openai import OpenAI

logger = get_logger(__name__)

load_dotenv()
client = OpenAI()

days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

def removeMinuteSec(current):
    current[4] = 0
    current[5] = 0
    return current


def checkResult(resultList) -> bool:
    #if no same times then we just die I suppose
    resultList = [ScrapeResult.objects.get(id=result_id) for result_id in resultList]
    correct = [
        result for i, result in enumerate(resultList) 
        if i != 0 and result[i].latestTime != result[i-1].latestTime
    ]

    if len(correct) == 0:
        return False, -1, -1

    #If there are at least 2 of the same differences in time (Only strategy for now)
    same = 0
    for el in correct:
        if el.latestTime - el.timeOfAccess == correct[0].latestTime - correct[0].timeOfAccess:
            same+=1
        if same == 2:
            return True, el.timeOfAccess, el.latestTime - el.timeOfAccess 

    return False, -1, -1


def scrapeTime(task, url):
    image_directory = Path(__file__).resolve().parent / "imgToNav"
    test_dir = Path(__file__).resolve().parents[1] / "debug"
    tries = 3
    while tries > 0:
        try:
            return scrapeTimeHelper(task, url, image_directory, test_dir)
        except Exception as e:
            logger.error(f"Error scraping time: {e}")
            tries -= 1
            time.sleep(5)

def scrapeTimeHelper(task, url, image_directory, test_dir):
    chrome = subprocess.Popen([
        "google-chrome",
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--no-first-run",
        "--no-default-browser-check",
        "--window-size=3840,2160",
        "--force-device-scale-factor=1",
        "--user-data-dir=/tmp/eattogo-chrome-profile",
        url,
    ])

    try:
        time.sleep(5)

        screen_x, screen_y = pyautogui.size()
        #Something is wrong with
        availCenter = pyautogui.center(pyautogui.locateOnScreen(str(image_directory / "AvailabilityButton.png"), 55, region=(int(screen_x/3), int(screen_y/3), int(screen_x/3), int(screen_y/3)), confidence=0.7))
        pyautogui.moveTo(availCenter[0], availCenter[1], duration=1)
        pyautogui.leftClick()
        time.sleep(3)

        img = pyautogui.screenshot(region=(int(screen_x/3), int(2*screen_y/5), int(screen_x/3), int(screen_y/5)))
        img.save(test_dir / f"screenshot{time.time()}.png")
        nextMonthCenter = pyautogui.center(pyautogui.locateOnScreen(str(image_directory / "NextMonthButton.png"), 60, region=(int(screen_x/3), int(2*screen_y/5), int(screen_x/3), int(screen_y/5)), confidence=0.3))
        pyautogui.moveTo(nextMonthCenter[0], nextMonthCenter[1], duration=1)
        
        for i in range(12):
            pyautogui.leftClick()
            time.sleep(1)
        
        img = pyautogui.screenshot(region=(int(screen_x/3), int(2*screen_y/5), int(screen_x/3), int(screen_y/5)))
        img.save(test_dir / f"screenshot{time.time()}.png")

        buffer = BytesIO()
        img.save(buffer, format="png")
        img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')

        
        response = client.responses.create(
            model="gpt-5.5",
            input=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": """
        Analyze this reservation calendar.

        A date is unavailable if it is visually disabled, crossed out,
        greyed out, or blocked. Write the date of the last available reservation in MM-DD-YYYY format 
        with MM indicating where the numeric represnetation for the month would go, 
        DD for the numeric representation for the day,
        and YYYY for the year
        """,
                        },
                        {
                            "type": "input_image",
                            "image_url": f"data:image/png;base64,{img_str}",
                            "detail": "high",
                        },
                    ],
                }
            ],
        )
        latestDate = time.mktime(time.strptime(response.output_text, "%m-%d-%Y"))

        now = time.mktime(tuple(removeMinuteSec(list(time.localtime(time.time())))))

        scrapeResult = ScrapeResult.objects.create(task=task, timeOfAccess=int(now), latestTime=int(latestDate))
        task.addResult(scrapeResult.id)


        done, timeOfAccess, dif = checkResult(task.results)
        if not done:
            return {"dayDif": int((latestDate - time.time()) / (3600 * 24)), "done": False}

        return {"hour": time.localtime(timeOfAccess)[3], "dayDif": (dif / (3600 * 24)), "done": True}
    finally:
        chrome.terminate()
        chrome.wait()




def findNumberDown(tupleTime):
    weeksAfterFirst = (tupleTime[2] - time.localtime(time.time())[2])/7
    offset = 1 if time.localtime(time.time())[6] < tupleTime[6] else 0
    return weeksAfterFirst + offset
        
def selectTime(task, url, reservationFor):
    image_directory = Path(__file__).resolve().parent / "imgToNav"
    test_dir = Path(__file__).resolve().parents[1] / "debug"

    tupleTime = time.strptime(reservationFor, "%H:%M:%S %m/%d/%Y")

    chrome = subprocess.Popen([
        "google-chrome",
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--no-first-run",
        "--no-default-browser-check",
        "--window-size=3840,2160",
        "--force-device-scale-factor=1",
        "--user-data-dir=/tmp/eattogo-chrome-profile",
        url,
    ])
    try:
        time.sleep(5)

        screen_x, screen_y = pyautogui.size()
        availCenter = pyautogui.center(pyautogui.locateOnScreen(str(image_directory / "AvailabilityButton.png"), 55, region=(int(screen_x/3), int(2*screen_y/5), int(screen_x/3), int(screen_y/5)), confidence=0.70))
        pyautogui.moveTo(availCenter[0], availCenter[1], duration=1)
        pyautogui.leftClick()
        time.sleep(3)

        nextMonthCenter = pyautogui.center(pyautogui.locateOnScreen(str(image_directory / "NextMonthButton.png"), 60, region=(int(screen_x/3), int(2*screen_y/5), int(screen_x/3), int(screen_y/5)), confidence=0.3))
        pyautogui.moveTo(nextMonthCenter[0], nextMonthCenter[1], duration=1)

        currentMonth = time.localtime(time.time())[1]
        needMonth = tupleTime[1]
        separationMonths = needMonth - currentMonth if needMonth >= currentMonth else 12 - currentMonth + needMonth

        for i in range(separationMonths):
            pyautogui.leftClick()
            time.sleep(1)
        
        img = pyautogui.screenshot(region=(int(screen_x/3), int(2*screen_y/5), int(screen_x/3), int(screen_y/5)))
        img.save(test_dir / f"screenshot{time.time()}.png")
        

        # TODO: NEED TO FIND CORRECT TIME
        img = pyautogui.screenshot(region=(int(2*screen_x/5), int(2*screen_y/5), int(screen_x/5), int(screen_y/5)))
        img.save(test_dir / f"screenshot{time.time()}.png")
        config = "--oem 3 --psm 6"
        page = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT, config=config)
        print(page['text'])
        for i, text in enumerate(page['text']):
            if text.strip() == days[tupleTime[6]]:
                x = page['left'][i]
                y = page['top'][i]
                width = page['width'][i]
                height = page['height'][i]
                center = pyautogui.center((x, y, width, height))

                numberDown = findNumberDown(tupleTime)
                pyautogui.moveTo(center[0], center[1] + numberDown * 36, duration=1)
                pyautogui.leftClick()
                time.sleep(1)
                print("found, ")
                img = pyautogui.screenshot(region=(center[0], center[1] + numberDown * 36, 40, 40))
                img.save(test_dir / f"screenshot{time.time()}.png")
                break

        img = pyautogui.screenshot(region=(int(2*screen_x/5), int(2*screen_y/5), int(screen_x/5), int(screen_y/5)))
        img.save(test_dir / f"screenshot{time.time()}.png")

        pyautogui.scroll(-1000)

        return {"done": False}
    finally:
        chrome.terminate()

        chrome.wait()

    #Click the box
    #Then use the pytesseract and openai to match preferences and such and if it requires a credit card abort and return error





        