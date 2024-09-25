import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as dates
from pyweb import pydom
from pyodide.http import open_url
from pyscript import display
from js import console, fetch
from pathlib import Path
import asyncio, os, sys, io, zipfile
import nltk

response = await fetch('https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/packages/sentiment/vader_lexicon.zip')
js_buffer = await response.arrayBuffer()
py_buffer = js_buffer.to_py()  # this is a memoryview
stream = py_buffer.tobytes()  # now we have a bytes object

d = Path("/nltk/vader")
d.mkdir(parents=True, exist_ok=True)

Path('/nltk/vader/master.zip').write_bytes(stream)

zipfile.ZipFile('/nltk/vader/master.zip').extractall(
    path='/nltk/vader/'
)

# nltk.downloader.download("all")
from nltk.sentiment import SentimentIntensityAnalyzer

title = "Pandas (and basic DOM manipulation)"
page_message = f"This example loads a remote CSV file into a Pandas dataframe  {np.random.randint(10)}, and displays it."
url = "Ukraine"

url1 = "https://raw.githubusercontent.com/scarcellidom/congressional_hearings/refs/heads/main/assets/house_transcripts_1.csv"
url2 = "https://raw.githubusercontent.com/scarcellidom/congressional_hearings/refs/heads/main/assets/house_transcripts_2.csv"
url3 = "https://raw.githubusercontent.com/scarcellidom/congressional_hearings/refs/heads/main/assets/house_transcripts_3.csv"
url4 = "https://raw.githubusercontent.com/scarcellidom/congressional_hearings/refs/heads/main/assets/house_transcripts_4.csv"


pydom["title#header-title"].html = title
pydom["a#page-title"].html = title
pydom["div#page-message"].html = page_message
pydom["input#txt-url"][0].value = url

def log(message):
    # log to pandas dev console
    print(message)
    # log to JS console
    console.log(message)

def loadFromURL(event):
    pydom["div#pandas-output-inner"].html = ""
    url = pydom["input#txt-url"][0].value

    log(f"Analyzing sentiment for {url}")
    df1 = pd.read_csv(open_url(url1))
    df2 = pd.read_csv(open_url(url2))
    df3 = pd.read_csv(open_url(url3))
    df4 = pd.read_csv(open_url(url4))
    
    df = pd.concat([df1,df2,df3,df4])
    df['date'] = pd.to_datetime(df['date'])
    
    term = url
    start_date = datetime.datetime(2012, 1, 1)
    end_date = datetime.datetime(2023, 12, 31)
    subcommittee = "."
    
    df = df.loc[(df['yt_tscpt'].astype(str).str.contains(term, regex=True, case=False)) &
                (df['yt_tscpt'].astype(str).str.contains(subcommittee, regex=True, case=False)) &
                (df['date']>start_date) & (df['date']<end_date)]
    log(f"length of dataset is {len(df)}")
    
    s_score = []
    wc_words = []
    try:
        sia = SentimentIntensityAnalyzer()
    except Exception as e:
        log(e)

    try:
        for hearing in df['yt_tscpt']:
            score = {}
            for i in range(len(hearing.split(term))):
                if i==0:
                    continue
                else:
                    text = hearing.split(term)[i-1][-50:] + hearing.split(term)[i][:50]
                    score[text] = sia.polarity_scores(text)['compound']
            if len(score)>0:
                s_score.append(sum(score.values())/len(score.values()))
                words = list(set(" ".join(list(score.keys())).split()))
                bad_words = {}
        
                for word in words:
                    s = sia.polarity_scores(word)['compound']
                    if s != 0:
                        bad_words[word] = abs(s)
                wc_words.append(bad_words)
            else:
                s_score.append(0)
                wc_words.append({})
    except Exception as e:
        log(i)
        
    df['s_score'] = s_score
    df['wc_words'] = wc_words
    
    df.dropna(inplace=True)
    df = df[df['s_score']!=0]
    avg = df.copy()
    avg['year'] = avg['date'].apply(lambda dt: dt.replace(day=6, month=6))
    avg = avg.groupby('year', as_index=False)['s_score'].mean()
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    ax.scatter(dates.date2num(df['date']),df['s_score'])
    ax.plot(dates.date2num(avg['year']),avg['s_score'], c='r')
    
    ax.xaxis.set_major_formatter(dates.DateFormatter('%Y'))
    
    display(fig, target="pandas-output-inner")

