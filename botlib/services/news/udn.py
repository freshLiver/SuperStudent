import requests as rq
from bs4 import BeautifulSoup
import re
import datetime

html_list = []
title_list = []
content_list = []
date_list = []


def parse(keyword: list, ty: (datetime, datetime)):

    url = "https://udn.com/rank/pv/2"
    response = rq.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    sel = soup.select("div.story-list__text h2 a")
    for ele in sel:
        html_list.append(ele["href"])
    for link in html_list:
        url = link
        response = rq.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # get title
        s = soup.find("h1", "article-content__title").text
        title_list.append(s)

        # get date
        s = soup.find("time", "article-content__time").text
        date = datetime.datetime.strptime(s, '%Y-%m-%d %H:%M')
        if ty[0] < date < ty[1]:
            # get content
            text_list = soup.find("section", "article-content__editor").select("p")
            text = "".join(t.text.replace("\r", "").replace("\n", "").replace('</p>', '').replace('<p>', '') for t in text_list)
            text = re.sub('[a-zA-Z]', '', text)
            if match(text,keyword):
                return text

    return "找不到相符結果"


def match(content: str, keyword: list):

    for key in keyword:
        if key not in content:
            return False
    return True

