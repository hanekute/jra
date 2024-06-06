import pandas as pd
import numpy as np
import math


before = pd.read_csv('scraping/data/jra_chaku_br.csv', low_memory=False, encoding = "shift-jis")

# 最初にafterの列を用意
after_columns = list(before.columns.values[:26]) + [s[:-1] for s in before.columns.values[26:42]]
# 1を弾く
# 条件＋払戻と馬の情報に分ける
joken = before.loc[:, :'3連単']
uma   = before.loc[:, '着順1':]
# 馬の方の中身を成形（numpyで）
# 条件の方を増殖
joken_array = joken.to_numpy()
uma_array   = uma.to_numpy()

after_array = np.empty((0, 42))

def count_non_missing(arr):
    # 欠損値が含まれているかどうかを判定するマスクを作成
    mask = np.isnan(arr) if np.issubdtype(arr.dtype, np.floating) else arr == arr
    # 欠損値でない要素の数を数える
    return np.count_nonzero(mask)

print(joken_array.shape[0])

for i in range(joken_array.shape[0]):
    if i % 1000 == 0:
        print(i)
    joken_row = joken_array[i]
    uma_row   = uma_array[i]
    horse_num = math.ceil(count_non_missing(uma_row) / 16)
    uma_row = uma_row[:16 * horse_num].reshape([horse_num, 16])
    # uma_rowの各行の左にjoken_rowを結合する
    new_row = np.column_stack((np.tile(joken_row, (uma_row.shape[0], 1)), uma_row))
    after_array = np.vstack((after_array, new_row))

after = pd.DataFrame(data=after_array, columns=after_columns)
after.to_csv('scraping/data/jra_chaku_bh.csv', index=False, encoding = "shift-jis")


# numpyリストのままcsvに出力してしまおう