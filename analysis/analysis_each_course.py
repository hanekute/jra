# コース別の集計
'''
改善箇所

'''
import pandas as pd
# from graph import ninkigraph, wakugraph

INPUT_CSV = 'scraping/data/jra_chaku_bh.csv'
OUTPUT_CSV = 'analysis/data/course_data/'
# OUTPUT_JPG = 'analyzed/images/'

def payout(row):
    row['単払戻'] = row['単勝'] * (row['着順'] == 1)
    if row['着順'] <= 3:
        row['複払戻'] = row['複勝' + str(row['着順'])[0]]
    else:
        row['複払戻'] = 0
    return row


data = pd.read_csv(INPUT_CSV, encoding='shift-jis')

print('読み込んだ')
data['course_id'] = data['場所'] + data['コース'] + data['距離'].astype(int).astype(str)
print('course_id作った')
data = data.apply(payout, axis=1) 
print('払戻作った')

course_list = sorted(data['course_id'].unique())
columns_list = ['人気', '馬番', '枠', 'コーナー通過順']

for course in course_list:
    course_data = data[data['course_id'] == course]
    print(course)
    for column in columns_list:
        
        grouped = course_data.groupby(column)
        
        chaku1 = course_data[course_data['着順']==1]
        chaku2 = course_data[course_data['着順']==2]
        chaku3 = course_data[course_data['着順']==3]

        new_df = pd.DataFrame(columns=['R数', '1着', '2着', '3着', '勝率', '連対率', '入着率', '単回収', '複回収'])
        new_df['R数'] = grouped.count()['着順']
        new_df['1着'] = chaku1.groupby(column).count()['着順']
        new_df['2着'] = chaku2.groupby(column).count()['着順']
        new_df['3着'] = chaku3.groupby(column).count()['着順']
        new_df['1着':'3着'].fillna(0, inplace=True)
        new_df['勝率']   = round(new_df['1着']*100 / new_df['R数'], 1)
        new_df['連対率'] = round((new_df['1着']+new_df['2着'])*100 / new_df['R数'], 1)
        new_df['入着率'] = round((new_df['1着']+new_df['2着']+new_df['3着'])*100 / new_df['R数'], 1)
        new_df['単回収'] = round(grouped.sum()['単払戻']/new_df['R数'], 1)
        new_df['複回収'] = round(grouped.sum()['複払戻']/new_df['R数'], 1)
        
        # CSV出力
        cap = dict()
        joken = {'コース': course}
        for k,v in joken.items():
            cap[k] = v
        cap['集計'] = column
        cap['レース数'] = len(course_data)
        caption_df = pd.DataFrame([cap])
        caption_df.to_csv(OUTPUT_CSV + course + '.csv', index=False, encoding="shift-jis", mode='a')
        new_df.to_csv(OUTPUT_CSV + course +'.csv', encoding="shift-jis", mode='a')
        
        # JPG出力（勝率を折れ線，単勝回収率を棒グラフ）
        # ninkigraph(new_df, course)
        # wakugraph(new_df, course)