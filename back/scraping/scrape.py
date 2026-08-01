import subprocess
import pyautogui
import base64
from io import BytesIO
import time
from celery import Celery

from dotenv import load_dotenv

from openai import OpenAI

load_dotenv("../.env")
client = OpenAI()

class Result():
    def __init__(self, latestOpening, now):
        self.latestTime = latestOpening
        self.timeOfAccess = now


class InjectedResult(Result):
    def __init__(self, latestOpening, now, history):
        super().__init__(latestOpening, now)
        self._history = history

    def __getitem__(self, index):
        return self._history[index]


class ResultsConfig():
    resultList = []
    def __init__(self):
        pass

    def addResult(self, result):
        self.resultList.append(result)

    def checkResult(self) -> bool:
        #if no same times then we just die I suppose
        correct = [
            result for i, result in enumerate(self.resultList) 
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

    
class RestaurantResults():
    def __init__(self, url):
        self.resultsConfig = ResultsConfig()
        self.url = url
    def scraping(self):
        chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        subprocess.Popen([
            chrome_path,
        ])
        time.sleep(1.5)
        pyautogui.moveTo(300, 100, duration=1)
        pyautogui.typewrite(self.url, interval=0.05)
        pyautogui.keyDown("enter")
        pyautogui.keyUp("enter")
        time.sleep(3)
        #move to availaility
        availCenter = pyautogui.center(pyautogui.locateOnScreen("./imgToNav/AvailabilityButton.png", minSearchTime=3, confidence=0.8))
        pyautogui.moveTo(availCenter[0], availCenter[1], duration=1)
        pyautogui.leftClick()
        time.sleep(3)

        nextMonthCenter = pyautogui.center(pyautogui.locateOnScreen("./imgToNav/NextMonthButton.png", minSearchTime=3, confidence=0.8))
        pyautogui.moveTo(nextMonthCenter[0], nextMonthCenter[1], duration=1)
        for i in range(12):
            pyautogui.leftClick()
            time.sleep(1)

        screen_x, screen_y = pyautogui.size()
        img = pyautogui.screenshot(region=(int(screen_x/4), int(screen_y/4), int(screen_x/2), int(screen_y/2)))
        buffer = BytesIO()
        img.save(buffer, format="png")
        img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')

        
        response = client.responses.create(
            model="gpt-5",
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

        self.resultsConfig.addResult(Result(latestDate, now))
        done, timeOfAccess, dif = self.resultsConfig.checkResult()
        if not done:
            return {}

        return {"hour": time.localtime(timeOfAccess)[3], "dayDif": (dif / (3600 * 24))}


def removeMinuteSec(current):
    current[4] = 0
    current[5] = 0
    return current




        
