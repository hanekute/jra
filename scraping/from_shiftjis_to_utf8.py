import pandas as pd
data = pd.read_csv('scraping/data/jra_chaku_br.csv', low_memory=False, encoding = "shift-jis")
data.to_csv('scraping/data/jra_chaku_br_utf8.csv', index=False)

data = pd.read_csv('scraping/data/jra_ninki_br.csv', low_memory=False, encoding = "shift-jis")
data.to_csv('scraping/data/jra_ninki_br_utf8.csv', index=False)
