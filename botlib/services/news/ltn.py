import requests as rq
from bs4 import BeautifulSoup
import re
import datetime

html_list = []
title_list = []
content_list = []
date_list = []


def parse(keyword: list, ty: (datetime, datetime)):
    url = "https://news.ltn.com.tw/list/breakingnews/popular"

    response = rq.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    sel = soup.select("a.tit")
    for ele in sel:
        html_list.append(ele["href"])

    for link in html_list:
        url = link
        response = rq.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # get title
        s = soup.find("div", "whitecon").find("h1").text
        title_list.append(s.replace(" ", "").replace("\n", ""))

        # get date
        s = soup.find("span", "time").text
        s = s.replace(" ", "").replace("\n", "")
        date = datetime.datetime.strptime(s, '%Y-%m-%d%H:%M')
        if ty[0] < date < ty[1]:
            # get content
            text_list = soup.find("div", {"class": "text"}).find_all("p", class_="", recursive=False)
            text = "".join(t.text.replace("\r", "").replace("\n", "").replace('</p>', '').replace('<p>', '') for t in text_list)
            text = re.sub('[a-zA-Z]', '', text)
            if match(text, keyword):
                return text

    return "找不到相符結果"


def match(content: str, keyword: list):

    for key in keyword:
        if key not in content:
            return False
    return True

