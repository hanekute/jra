import datetime
import pandas as pd
import shutil
import numpy as np
# グラフを描くための設定
import plotly.graph_objects as go
# グラフ描画（単勝・人気別）
# 横軸は人気，縦軸は的中率および回収率
# 的中率が折れ線，回収率が棒グラフ
def ninkigraph(df, course):
      layout = {
                  "title"  : { "text": course+"：人気別的中率・回収率"},
                  "xaxis" : { "title": "人気", "rangeslider": { "visible": False },  "type" : "category" },
                  "yaxis1" : { "title": "回収率（％）"},
                  "yaxis2" : { "title": "的中率（％）"},
                  "plot_bgcolor":"light blue"
            }

      data =  [
            # 回収率
            go.Bar(yaxis='y1', x=df.index, y=df['単回収'], name='単勝回収率（％）', 
                  marker={'color': 'blue'}),
            # 的中率
            go.Scatter(yaxis='y2', x=df.index, y=df['勝率'], name='的中率（％）', 
                        line={'color': 'red', 'width':2})
            ]

      fig = go.Figure(data = data, layout = go.Layout(layout))
      fig.update_layout(yaxis1=dict(side='right', range=(0,180), dtick=20), yaxis2=dict(side='left', range=(0,45), overlaying = 'y', dtick=5))

      fig.show()

      fig.write_html('analyzed/images/'+course+'.html')
      
def wakugraph(df, course):
      layout = {
                  "title"  : { "text": course+"：枠番別的中率・回収率"},
                  "xaxis" : { "title": "枠番", "rangeslider": { "visible": False },  "type" : "category" },
                  "yaxis1" : { "title": "回収率（％）"},
                  "yaxis2" : { "title": "的中率（％）"},
                  "plot_bgcolor":"light blue"
            }

      data =  [
            # 回収率
            go.Bar(yaxis='y1', x=df.index, y=df['単回収'], name='単勝回収率（％）', 
                  marker={'color': 'blue'}),
            # 的中率
            go.Scatter(yaxis='y2', x=df.index, y=df['勝率'], name='的中率（％）', 
                        line={'color': 'red', 'width':2})
            ]

      fig = go.Figure(data = data, layout = go.Layout(layout))
      fig.update_layout(yaxis1=dict(side='right', range=(0,120), dtick=20), yaxis2=dict(side='left', range=(0,15), overlaying = 'y', dtick=2.5))

      fig.show()

      fig.write_html('analyzed/images/'+course+'.html')