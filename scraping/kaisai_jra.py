# Program to collect racing calendars.
# 2013_Jan~2022_Dec
'''
Problems:
    2 urls are connected sometimes -> add (+'\n') to str_
        last and first url of the month are connected
    Blank rows (gradually increase) -> Partial text in (find_elements)
        Double blank in the classname causes this?
    Movie AD makes scraping slow.
'''
import time
import pandas as pd
import numpy as np
from selenium import webdriver
# from seleniumwire import webdriver
from selenium.webdriver.common.by import By
import csv
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from send_gmail import send_gmail


driver = webdriver.Chrome()
wait = WebDriverWait(driver=driver, timeout=5)

# def interceptor(request):
#     if request.path.endswith(('.png', '.jpg', '.gif')):
#         request.abort()


def get_daily_url(driver):
    calendar = driver.find_element(By.CLASS_NAME, 'Calendar_Table')
    day_list = calendar.find_elements(By.TAG_NAME, 'a')
    day_urls = [i.get_attribute('href') for i in day_list]
    day_array = np.array(day_urls)
    return day_array
    
def get_race_url(url): # return list
    driver.get(url)
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'RaceList_DataItem')))
    race_list = driver.find_elements(By.CLASS_NAME, 'RaceList_DataItem')
    race_urls_list = [l.find_element(By.TAG_NAME, 'a').get_attribute('href') for l in race_list]
    return race_urls_list
    
if __name__ == "__main__":
    try:
        total_start = time.time()
        # urls: ndarray for calendar URL 
        YEARS = np.arange(2013, 2023).astype(str)
        mlist = list(range(1,13))
        mlist = [str(i).zfill(2) for i in mlist]
        MONTHS = np.array(mlist)
        urls = np.full(12*YEARS.size, 'year=0000&month=00')
        for i in range(YEARS.size):
            for j in range(12):
                urls[12*i+j] = 'year='+YEARS[i]+'&month='+MONTHS[j]
        
        for i in range(urls.size):
            start = time.time()
            print(urls[i])
            url = 'https://race.netkeiba.com/top/calendar.html?' + urls[i]
            driver.get(url)
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'Calendar_Table')))
            # ndarray of daily url
            day_array = get_daily_url(driver)
            # ndarray of race url
            race_list = [get_race_url(row) for row in day_array]
            # List size (not empty only)
            print('開催数=', end='')
            print(sum(len(v) for v in race_list)/12) 
            str_list = ['\n'.join(l) for l in race_list]
            str_ = '\n'.join(str_list)+'\n'
            # Output file
            CSV_NAME = "data/kaisai.csv"
            # Save file
            with open(CSV_NAME, 'a', newline='') as file:
                file.write(str_)
            
            end = time.time()
            t = int(end - start)
            sec, min, hou = t%60, int((t/60)%60), int(t/3600)
            print('{}h {}m {}s'.format(hou, min, sec))
    finally:
        total_end = time.time()
        t = int(total_end - total_start)
        sec, min, hou = t%60, int((t/60)%60), int(t/3600)
        print('{}h {}m {}s'.format(hou, min, sec))
        driver.quit()
        
        # Send an email
        path = "codes/"
        json_file = "credentials.json"
        message_text = f'Total: {hou}時間{min}分{sec}秒．'
        send_gmail(path, json_file, message_text)
