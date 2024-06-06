#2013~2021のデータと2022のデータを合体させる
import pandas as pd

bh_new = pd.read_csv('data/2022/jra_result_bh_2022.csv', encoding='shift-jis')
bh_old = pd.read_csv('data/jra_result_bh_2021.csv', encoding='shift-jis')
bh = pd.concat([bh_new, bh_old])
bh.to_csv('data/jra_result_bh.csv', index=False, encoding='shift-jis')
bh_new = 0
bh_old = 0
br_new = pd.read_csv('data/2022/jra_result_br_2022.csv', encoding='shift-jis')
br_old = pd.read_csv('data/jra_result_br_2021.csv', encoding='shift-jis')
br = pd.concat([br_new, br_old])
br.to_csv('data/jra_result_br.csv', index=False, encoding='shift-jis')