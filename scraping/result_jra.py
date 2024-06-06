import re
import time
import warnings
from datetime import datetime, date

import numpy as np
import pandas as pd
import swifter

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome import service as fs
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from send_gmail import send_gmail

warnings.simplefilter('ignore', pd.errors.SettingWithCopyWarning)

driver = webdriver.Chrome()
wait = WebDriverWait(driver=driver, timeout=10)

swift = swifter.progress_bar(False)

SAIKAI = 1
SLEEP_TIME = 10

INPUT_CSV = 'data/kaisai.csv'

OUTPUT_BY_HORSE = 'data/jra_result_by_horse.csv'
OUTPUT_BY_RACE = 'data/jra_result_by_race.csv'

def get_condition(driver, year):
    col = [
        '日付', '場所', '開催', '日目', 'レース', '名前', '年齢', 'クラス',
        '斤量条件', 'コース', '距離', '天候', '馬場状態', '頭数'
        ]
    condition = pd.DataFrame(columns=col, index=[0])
    
    monthdays = driver.find_elements(By.CLASS_NAME, 'Active')[1].text
    dates = re.findall(r'\d+', monthdays)
    ymd_str = year + dates[0].zfill(2) + dates[1].zfill(2)
    datetime_ = datetime.strptime(ymd_str, '%Y%m%d')
    condition['日付'] = date(datetime_.year, datetime_.month, datetime_.day)
    racedata2 = driver.find_elements(By.XPATH, '//*[@class="RaceData02"]/span')
    condition['場所'] = racedata2[1].text
    condition['開催'] = racedata2[0].text[:-1]
    condition['日目'] = racedata2[2].text[:-2]
    condition['レース'] = driver.find_element(By.CLASS_NAME, 'RaceNum').text[:-1]
    condition['名前'] = driver.find_element(By.CLASS_NAME, 'RaceName').text
    course_length = driver.find_element(By.XPATH, '//*[@class="RaceData01"]/span[1]').text
    condition['コース'] = course_length[0]
    condition['距離'] = course_length[1:-1]
    weather = driver.find_element(By.XPATH, '//*[@class="RaceData01"]').text
    condition['天候'] = weather[weather.find('天候:')+3:weather.find('天候:')+4]
    ground03 = driver.find_elements(By.CLASS_NAME, 'Item03')
    if ground03:
        ground = ground03[0]
    else:
        ground = driver.find_elements(By.CLASS_NAME, 'Item04')[0]
    condition['馬場状態'] = ground.text[-1]
    condition['年齢'] = racedata2[3].text[3:] 
    condition['クラス'] = racedata2[4].text
    condition['斤量条件'] = racedata2[6].text
    condition['頭数']  = racedata2[7].text[:-1]
    return condition


def get_result_by_horse(df):
    # 1~3着に同着があれば終了
    first_to_fourth = df.iloc[1:5].to_numpy()
    if np.any(first_to_fourth == '同着'):
        return pd.DataFrame()
    # 除外・取消→削除
    df = df[(df['着 順'] != '除外')&(df['着 順'] != '取消')]
    # 失格・中止→下の着順を挿入
    df['No'] = range(1, len(df.index) + 1)
    df.loc[(df['着 順'] == '中止')|(df['着 順'] == '失格'), '着 順'] = df['No']
    
    df['性'] = df['性齢'].swift.apply(lambda x: x[0])
    df['齢'] = df['性齢'].swift.apply(lambda x: x[1:])
    df['コーナー 通過順'].fillna('0', inplace=True)
    df['コーナー 通過順'] = df['コーナー 通過順'].swift.apply(lambda x: re.findall(r'\d+', str(x))[-1])
    
    batai = df['馬体重 (増減)']
    df['馬体重'] = batai.swift.apply(lambda x: x[0:3] if x != '' else None)
    df['増減'] = batai.swift.apply(lambda x: x[4:-1] if x != '' else None)
    
    col = [
        '着 順', '枠', '馬 番', '馬名', '性', '齢', '斤量', '騎手', 'タイム', '人 気', 
        '単勝 オッズ', '後3F', 'コーナー 通過順', '厩舎', '馬体重', '増減'
        ]
    new_df = df.reindex(columns=col)
    new_df.columns = [c.replace(' ', '') for c in new_df.columns.tolist()]
    
    return new_df


def get_result_by_race(df):
    col = df.columns.to_list()
    a = df.to_numpy().reshape([1, len(col)*len(df)])
    new_col = list()
    for i in range(len(df)):
        new_col += [c+str(i+1) for c in col]
    new_df = pd.DataFrame(data=a, columns=new_col)
    if len(df) < 18:
        extra_col = list()
        for i in range(len(df), 18):
            extra_col += [c+str(i+1) for c in col]
        extra_df = pd.DataFrame(columns=extra_col)
        new_df = pd.concat([new_df, extra_df], axis=1)
    return new_df


def get_payout(df1, df2):
    col = [
        '単勝', '複勝1', '複勝2', '複勝3', '枠連', '馬連',
        'ワイド12', 'ワイド13', 'ワイド23', '枠単', '馬単', '3連複', '3連単'
        ]
    new_df = df1.join(df2)
    new_df.index = ['a']
    try:
        fukusho = new_df.at['a', '複勝'][:-1].split('円')
        for i in range(len(fukusho)):
            new_df['複勝'+str(i+1)] = fukusho[i]
    except: pass
    try:
        wide = new_df.at['a', 'ワイド'][:-1].split('円')
        w = ['12', '13', '23']
        for i in range(len(wide)):
            new_df['ワイド'+w[i]] = wide[i]
    except: pass
    new_df = new_df.replace('(.*),(.*)', r'\1\2', regex=True)
    new_df = new_df.replace('(.*)円(.*)', r'\1\2', regex=True)
    new_df = new_df.reindex(columns=col).reset_index(drop=True)
    return new_df


if __name__ == '__main__':
    try:
        count = 1
        
        total_start = time.time()
        k_2D = np.loadtxt(INPUT_CSV, dtype='unicode')
        ALL_RACE_URL = k_2D.reshape(-1)
        
        for race_url in ALL_RACE_URL:
            if count < SAIKAI:
                count += 1
                continue
            race_start = time.time()
            print(count, end=': ')
            year = race_url[51:55]
            
            # 謎のTimeout対策
            flag = True
            while flag:
                try:
                    driver.get(race_url)
                    flag = False
                except:
                    print('Retry')
                    driver.quit()
                    time.sleep(SLEEP_TIME)
                    driver = webdriver.Chrome()
            
            condition_by_race = get_condition(driver, year)
            # Race result
            result_html = driver.find_element(By.ID, 'All_Result_Table')
            result_df = pd.read_html(result_html.get_attribute('outerHTML'))[0]            
            result_by_horse = get_result_by_horse(result_df)
            if result_by_horse.empty:
                count += 1
                continue
            result_by_race = get_result_by_race(result_by_horse)
            tag = driver.find_elements(By.CLASS_NAME, 'Payout_Detail_Table')
            payout_df1 = pd.read_html(tag[0].get_attribute('outerHTML'), index_col=0)[0].T[1:2]
            payout_df2 = pd.read_html(tag[1].get_attribute('outerHTML'), index_col=0)[0].T[1:2]
            payout = get_payout(payout_df1, payout_df2)
            
            info_by_race = pd.concat([condition_by_race, payout], axis=1)
            info_col = info_by_race.columns.to_list()
            info_by_horse_a = info_by_race.to_numpy()
            info_by_horse_a = np.tile(info_by_horse_a,(len(result_by_horse),1))
            info_by_horse = pd.DataFrame(data=info_by_horse_a, columns=info_col)
            df_by_horse = pd.concat([info_by_horse, result_by_horse], axis=1)
            df_by_race = pd.concat([info_by_race, result_by_race], axis=1)
            
            
            if count==1:
                df_by_horse.to_csv(OUTPUT_BY_HORSE, index=False, encoding='shift-jis', mode='a')
                df_by_race.to_csv(OUTPUT_BY_RACE, index=False, encoding='shift-jis', mode='a')
            else:
                df_by_horse.to_csv(OUTPUT_BY_HORSE, index=False, header=False, encoding='shift-jis', mode='a', errors='ignore')
                df_by_race.to_csv(OUTPUT_BY_RACE, index=False, header=False, encoding='shift-jis', mode='a', errors='ignore')
            
            race_end = time.time()
            race_t = int(race_end - race_start)
            sec, min, hou = race_t%60, (race_t//60)//60, race_t//3600
            print(f'{hou}h {min}m {sec}s')
            
            count += 1
    
    finally:
        print(count)
        
        total_end = time.time()
        total_t = int(total_end - total_start)
        sec, min, hou = race_t%60, (race_t//60)//60, race_t//3600
        print(f'{hou}h {min}m {sec}s')
        
        driver.quit()
        
        path = 'codes/'
        json_file = 'credentials.json'
        message_text = f'{hou}h {min}m{sec}s.'
        send_gmail(path, json_file, message_text)

'''
タイム差は後日or別プログラムでやろう
df['前との差'] = df['タイム'].diff().fillna(0)
df['タイム差'] = df['前との差'].cumsum()
df.loc[df['タイム差'] < 0, 'タイム差'] = float('nan')
'''