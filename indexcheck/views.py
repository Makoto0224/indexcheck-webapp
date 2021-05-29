from django.shortcuts import render, get_object_or_404, redirect
from .models import Indexcheck
from .forms import IndexCreateForm

import pandas as pd
import pandas_datareader.data as web
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from datetime import date
from datetime import timedelta
from urllib.request import urlopen
from bs4 import BeautifulSoup
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

import requests
import json
import matplotlib
matplotlib.use('Agg')

import io
from django.http import HttpResponse

from .forms import SignUpForm



def index_list(request):
    context = {
        'index_list':Indexcheck.objects.all().order_by('created_at'),
    }
    return render(request, 'indexcheck/index_list.html', context)

def index_detail(request, pk):
    context = {
        'index': get_object_or_404(Indexcheck, pk=pk)
    }
    return render(request, 'indexcheck/index_detail.html', context)

def index_create(request):
    form = IndexCreateForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('indexcheck:index_list')

    context = {
        'form': form
    }
    return render(request, 'indexcheck/index_form.html', context)

def index_update(request, pk):
    index = get_object_or_404(Indexcheck, pk=pk)
    form = IndexCreateForm(request.POST or None, instance=index)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('indexcheck:index_list')

    context = {
        'form':form
    }
    return render(request, 'indexcheck/index_form.html', context)

def index_delete(request, pk):
    index = get_object_or_404(Indexcheck, pk=pk)
    if request.method =='POST':
        index.delete()
        return redirect('indexcheck:index_list')

    context = {
        'index': index
    }
    return render(request, 'indexcheck/index_confirm_delete.html', context)

def setPlt(request, pk):
    #theme = Indexcheck.objects.values_list('theme_name').get(pk=pk)
    l = Indexcheck.objects.values_list('code', flat=True).get(pk=pk)
    l = list(l)

    td = date.today()
    md = timedelta(weeks=18)
    st_dt = td - md #@param {type:'date'}
        

    data = web.DataReader([str(c) + '.JP' for c in l], 'stooq')

    dt0 = pd.DataFrame(data.index)

    def cook(code):
        try:
            tgt = 'https://kabutan.jp/stock/kabuka?code=' + str(code)
            html = urlopen(tgt)
            bsObj = BeautifulSoup(html, 'html.parser')
            table = bsObj.findAll('table', {'class':'stock_kabuka0'})[0]
            rows = table.findAll('tr')
            for row in rows:
                rec = []
                for cell in row.findAll(['td', 'th']):
                    rec.append(cell.get_text())
                del rec[5:7]
                rec.insert(0, str(code) + '.JP')
            dish.append(rec)
            return 'Success'
        except Exception as e:
            return str(code) + ': ' + str(e)
        
    dish = []
    [cook(i) for i in l]

    df10 = pd.DataFrame(dish).rename(columns={0: 'code', 1: 'Date', 2:'Open', 3: 'High', 4: 'Low', 5:'Close', 6: 'Volume'})
        
    dt_fmt = lambda dt_str: datetime.strptime(dt_str, '%y/%m/%d')

    df10['Date'] = df10['Date'].map(dt_fmt)

    def conv(dfn, col, typ):
        try:
            dfn[col] = dfn[col].astype(typ)
        except:
            dfn[col] = dfn[col].str.replace(',', '').astype(typ)
        finally:
            return 'Success'
        
    cols = ['code', 'Date', 'Open', 'High', 'Low', 'Close', 'Volume'] 

    [conv(df10, j, float) for j in cols[2:]]

    output = pd.DataFrame(index=[], columns=cols)

    for c in l:
        try:
            vec = []
            ex_values = lambda x: vec.append(data[x, str(c) + '.JP'].values.tolist())
            [ex_values(x) for x in cols[2:]] 

            df0 = pd.DataFrame(vec).T.rename(columns={0:'Open', 1:'High', 2:'Low', 3:'Close', 4:'Volume'})
            df1 = pd.merge(dt0, df0, left_index=True, right_index=True).query('Date >= @st_dt').dropna().reset_index().drop(columns='index')

            df11 = df10[df10['code'] == str(c) + '.JP'].drop(columns='code')

            df = df1.append(df11, ignore_index=True, sort=False)
            df['code'] = c

            output = output.append(df[cols])
        except Exception as e:
            print(str(c) + ': ' + e)
            
    output2 = output.drop(['Open','High','Low','Volume'], axis = 1)

    cols = []
    for i in range(0,len(l)):
        qs = 'code == @l[{0}]'.format(i)
        col = output2.query(qs).drop(columns='code').rename(columns={'Close':l[i]})
        col.set_index('Date', inplace=True)
        cols.append(col)

    output = pd.concat(cols, axis=1)  
    output = output.sort_index()
    
    output3 = np.log(output)
    output4 = output3.diff().fillna(0) + 1
    output5 = output4.cumprod()
    output6 = output5.drop(columns = l[0])
    topix = pd.DataFrame(output5[l[0]])
    output6["theme_avg"] = output6.mean(axis=1)
    theme_avg = pd.DataFrame(output6["theme_avg"])
    output7 = pd.concat([topix, theme_avg], axis=1)
    output7['Index'] = output7['theme_avg']/output7[l[0]]
    output8 = output7.drop(columns = ['theme_avg', l[0]])

    fig,ax = plt.subplots()
    ax.plot(output8.index, output8)
    ax.grid(True)
    #ax.set_title(theme, fontname="MS Gothic")
    plt.setp(ax.get_xticklabels(), rotation=60, ha="right")

def plt_svg():
    buf = io.BytesIO()
    plt.savefig(buf, format='svg', bbox_inches='tight')
    s = buf.getvalue()
    buf.close()
    return s

def get_svg(request, pk):
    setPlt(request, pk)  
    svg = plt_svg()  #SVG化
    plt.cla()  # グラフをリセット
    response = HttpResponse(svg, content_type='image/svg+xml')
    return response

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(to='indexcheck/index_list.html')
    else:
        form = SignUpForm()
    return render(request, 'indexcheck/signup.html', {'form': form})

def hello(request):
    name = request.user
    print(name)
    return render(request, 'indexcheck/hello.html', {'name': name})
