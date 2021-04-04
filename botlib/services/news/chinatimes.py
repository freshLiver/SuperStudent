import requests as rq
from bs4 import BeautifulSoup
import re
import datetime

html_list = []
title_list = []
content_list = []
date_list = []


def parse(keyword: list, ty: (datetime, datetime)):

    url = "https://www.chinatimes.com/realtimenews?chdtv"

    response = rq.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    sel = soup.select("h4.title a")
    for ele in sel:
        html_list.append(ele["href"])

    for link in html_list:
        url = link
        response = rq.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # get title
        s = soup.find("h1", "article-title").text
        title_list.append(s)
        print(s)
        # get date
        s = soup.find("span", "date").text
        hour = soup.find("span", "hour").text
        s += " "+hour
        print(s)
        date = datetime.datetime.strptime(s, '%Y/%m/%d %H:%M')
        if ty[0] < date < ty[1]:
            # get content
            text_list = soup.find("div", "article-body").select("p")
            text = ""
            for ele in text_list:
                ele = str(ele).replace("<p>", "").replace("</p>", "")
                text += ele
            text = re.sub('[a-zA-Z]', '', text)
            if match(text, keyword):
                return text
    return "找不到相符結果"


def match(content: str, keyword: list):

    for key in keyword:
        if key not in content:
            return False
    return True




