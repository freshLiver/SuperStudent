import requests as rq
from bs4 import BeautifulSoup
import re
import datetime

html_list = []
title_list = []
content_list = []
date_list = []


def parse(keyword: list, ty: (datetime, datetime)):
    url = "https://www.ettoday.net/news/hot-news.htm"
    response = rq.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    sel = soup.find("div", {"class": "part_pictxt_3"}).select("div.piece h3 a")
    for ele in sel:
        html_list.append("https://www.ettoday.net" + ele["href"])

    for link in html_list:
        url = link
        response = rq.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # get title
        s = soup.find("h1", itemprop="headline").text
        title_list.append(s)

        # get date
        s = soup.find("time", itemprop="datePublished").text
        date_list.append(s.replace(" ", "").replace("\n", ""))
        s = s.replace(" ", "").replace("\n", "")
        try:
            date = datetime.datetime.strptime(s, '%Y年%m月%d日%H:%M')
        except:
            date = -1
        if date != -1:
            if ty[0] < date < ty[1]:
                # get content
                text = ""
                text_list = soup.find("div", itemprop="articleBody").find_all("p", recursive=False)
                for t in text_list:
                    if not t.find("strong"):
                        text += t.text.replace("\r", "").replace("\n", "").replace('</p>', '').replace('<p>', '')
                text = re.sub('[a-zA-Z]', '', text)
                if match(text, keyword):
                    return [link, text[:30]]
    return ["NO_URL", "找不到相符結果"]


def match(content: str, keyword: list):

    for key in keyword:
        if key not in content:
            return False
    return True
