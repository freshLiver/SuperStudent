import requests as rq
from bs4 import BeautifulSoup
import re
import datetime


html_list = []
title_list = []
content_list = []
date_list = []


def parse(keyword: list, ty: (datetime, datetime)):
    url = "https://news.tvbs.com.tw/hot?from=click_hot"

    response = rq.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    sel = soup.select("div.content_center_contxt_real_news li a")

    for s in sel:
        html_list.append("https://news.tvbs.com.tw" + s["href"])

    for link in html_list:
        url = link
        response = rq.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # get title
        s = soup.find("div", "title_box").find("h1").text
        title_list.append(s)

        # get date
        s = soup.find("div", "author").text
        s = s.replace("	", "").replace("\n", "")
        if "最後更新時間：" in s:
            s = s[s.index("最後更新時間：") + 7:]
        else:
            s = s[s.index("發佈時間：") + 5:]
        try:
            date = datetime.datetime.strptime(s, '%Y/%m/%d %H:%M')
        except:
            date = -1
        if date != -1:
            if ty[0] < date < ty[1]:
                # get content
                text_list = soup.find_all("div", {"class": "article_content"})
                text = "".join(
                    t.text.replace("\r", "").replace("\n", "").replace('</p>', '').replace('<p>', '') for t in
                    text_list)
                text = re.sub('[a-zA-Z]', '', text)
                text = text.replace("～開啟小鈴鐺　 頻道新聞搶先看　快點我按讚訂閱～最話題在這！想跟上時事，快點我加入新聞好友！", "")
                if match(text, keyword):
                    return [link, text[:30]]
    return ["NO_URL", "找不到相符結果"]


def match(content: str, keyword: list):

    for key in keyword:
        if key not in content:
            return False
    return True



