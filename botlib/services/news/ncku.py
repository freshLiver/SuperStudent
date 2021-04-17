import requests as rq
from bs4 import BeautifulSoup
import re
import datetime

html_list = []
title_list = []
content_list = []
date_list = []


def parse(keyword: list, ty: (datetime, datetime)):
    url = "https://web.ncku.edu.tw/p/403-1000-3094-1.php?Lang=zh-tw"
    response = rq.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    sel = soup.select("div.mtitle a")
    for ele in sel:
        html_list.append(ele["href"])

    for link in html_list:
        url = link
        response = rq.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # get title
        s = soup.find("h2", "hdline").text

        # get title
        s = soup.find_all("span", "mattr-val")
        date_text = s[1].text + " 00:01"
        date = datetime.datetime.strptime(date_text, '%Y-%m-%d %H:%M')
        if ty[0] < date < ty[1]:
            # get context
            s = soup.find_all('span', attrs={'style': 'font-size:1.125em;'})
            text = ""
            for ele in s:
                text += ele.text.replace("\n", "")
            text = re.sub('[a-zA-Z]', '', text)
            if match(text, keyword):
                return [link, text[:30]]
    return ["NO_URL", "找不到相符結果"]


def match(content: str, keyword: list):

    for key in keyword:
        if key not in content:
            return False
    return True
