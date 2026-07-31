import subprocess
import pyautogui
import time

class Result():
    def __init__(self, time, result):
        self.latestTime = time
        self.timeOfAccess = result


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
            return False, -1

        #If there are at least 2 of the same differences in time (Only strategy for now)
        same = 0
        for el in correct:
            if el.latestTime - el.timeOfAccess == correct[0].latestTime - correct[0].timeOfAccess:
                same+=1
            if same == 2:
                return True, el.timeOfAccess

        return False, -1

    
class RestaurantResults():
    resultsConfig = ResultsConfig()
    def __init__(self, url):
        self.url = url

    def scraping(self):
        chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        subprocess.Popen([
            chrome_path,
        ])
        pyautogui.moveTo(300, 100, duration=1)
        pyautogui.typewrite(self.url, interval=0.05)
        pyautogui.keyDown("enter")
        pyautogui.keyUp("enter")
        pyautogui.moveTo(2300, 1700, duration=1)
        time.sleep(3)
        pyautogui.leftClick()
        time.sleep(3)
        
        # for i in range(12):
        #     pyautogui.moveTo(1900, 850, duration=1)
        #     time.sleep(1)

        # X_end = 1960
        # X_start = 1540
        # Y_start = 940
        # Y_end = 1300

        X_end = 1960
        X_start = 1540
        Y_start = 935
        Y_end = 1330

        x_dif = (X_end-X_start)/7
        y_dif = (Y_end-Y_start)/6
        x = X_start
        y = Y_start

        for i in range(6):
            x = X_start
            for j in range(7):
                pyautogui.moveTo(x, y, duration=0.5)
                pyautogui.leftClick()
                time.sleep(1)
                x+=x_dif
            y+=y_dif
