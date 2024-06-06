# 取得しているデータを人気順に並び替えて整理するプログラム
import time
import pandas as pd
import numpy as np

F = 18 # Full gate number
COLS = 16
if __name__ == "__main__":
    total_start = time.time()
    try:
        df_before = pd.read_csv('scraping/data/jra_chaku_br.csv', low_memory=False, encoding = "shift-jis")
        df_condition = df_before.loc[:, :'3連単']
        df_result = df_before.loc[:, '着 順1':]
        
        # 人気順の列のnanを9999に置換する
        for i in range(18):
            ninki = str(i + 1)
            df_result['人 気'+ninki].fillna(9999, inplace=True)

        # check
        test_df = df_result.head(2)
        test_df.to_csv('test/test.csv', index=False, encoding = "shift-jis")
        
        col = df_result.columns.to_list()
        result_array = df_result.to_numpy()
        row_number = result_array.shape[0] #行数
        result_array = result_array.reshape([row_number, F, COLS])
        
        
        # 各行（これが2次元）を[9]でソートする
        n = 0
        for race in result_array:
            # for horse in race:
            #     np.nan_to_num(horse, copy=False, nan=9999.0)
            if n < 2:
                print(race[:, 9])
                print(np.argsort(race[:, 9]))
            race = race[np.argsort(race[:, 9])]
            result_array[n] = race
            n += 1
        
        result_array = result_array.reshape([row_number, COLS*F])
        
        result_array[result_array == 9999] = ''
        new_df_result = pd.DataFrame(data=result_array, columns=col)
        
        # check
        test_df2 = new_df_result.head(2)
        test_df2.to_csv('test/test2.csv', index=False, encoding = "shift-jis")
        
        new_df = pd.concat([df_condition, new_df_result], axis=1)
        
        CSV_NAME = "scraping/data/jra_ninki2_br.csv"
        #データの保存        
        new_df.to_csv(CSV_NAME, index=False, encoding = "shift-jis")
        print('ok')
        
    finally:
        # Record time
        total_end = time.time()
        total_t = int(total_end - total_start)
        sec, min = total_t%60, int((total_t/60)%60)
        print('{}m {}s'.format(min, sec))