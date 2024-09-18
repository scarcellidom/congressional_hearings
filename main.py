import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pyweb import pydom
from pyodide.http import open_url
from pyscript import display
from js import console

title = "Pandas (and basic DOM manipulation)"
page_message = f"This example loads a remote CSV file into a Pandas dataframe  {np.random.randint(10)}, and displays it."
url = "https://raw.githubusercontent.com/scarcellidom/congressional_hearings/refs/heads/main/assets/house_transcripts_3.csv"

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

    log(f"Trying to fetch CSV from {url}")
    # df = pd.read_csv(open_url(url), usecols=['title'])
    df1 = pd.read_csv(open_url(url1), usecols=['date'])
    df2 = pd.read_csv(open_url(url2), usecols=['date'])
    df3 = pd.read_csv(open_url(url3), usecols=['date'])
    df4 = pd.read_csv(open_url(url4), usecols=['date'])

    df = pd.concat([df1,df2,df3,df4])

    plt.hist(df['date'])

    pydom["div#pandas-output"].style["display"] = "block"
    pydom["div#pandas-dev-console"].style["display"] = "block"

    display(plt, target="pandas-output-inner", append="False")
