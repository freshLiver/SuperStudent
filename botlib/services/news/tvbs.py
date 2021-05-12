import requests as rq
from bs4 import BeautifulSoup
import re
import datetime


html_list = []
title_list = []
content_list = []
date_list = []


def parse(keyword: list, ty: (datetime, datetime)):
    if_no_url = "NO_URL"
    if_no_context = "找不到相符結果"
    search_string = "https://news.tvbs.com.tw/news/searchresult/"
    if keyword:
        for ele in keyword:
            search_string = search_string + ele
            if ele != keyword[-1]:
                search_string = search_string + "%20"
        search_string = search_string + "/news/"
        response = rq.get(search_string)
        soup = BeautifulSoup(response.text, 'html.parser')
        sel = soup.find("h1", "search_result").text
        sel = sel[sel.find("結果共:")+5:sel.find("筆")-1]

        if int(sel) != 0:
            total_page = int(int(sel)/25) + 1
            if total_page > 5:
                total_page = 5
            for i in range(1, total_page+1):
                if i != 1:
                    url = search_string + str(i)
                    response = rq.get(url)
                    soup = BeautifulSoup(response.text, 'html.parser')
                # get_html
                sel = soup.select("div.search_list_text")
                for ele in sel:
                    w = ele.find("a")
                    html_list.append(w["href"])

                # get_date
                sel = soup.find_all("span", "publish_date display_none")
                for ele in sel:
                    date_list.append(ele.text)

                for j in range(0, len(date_list)):
                    date = datetime.datetime.strptime(str(date_list[j]), '%Y/%m/%d %H:%M')
                    if ty[0] <= date <= ty[1]:
                        response = rq.get(html_list[j])
                        soup = BeautifulSoup(response.text, 'html.parser')
                        text_list = soup.find_all("div", {"class": "article_content"})
                        text = "".join(
                            t.text.replace("\r", "").replace("\n", "").replace('</p>', '').replace('<p>', '') for t in
                            text_list)
                        text = re.sub('[a-zA-Z]', '', text)
                        text = text[0:50]
                        return [html_list[j], text]
                if i == 1:
                    response = rq.get(html_list[0])
                    soup = BeautifulSoup(response.text, 'html.parser')
                    text_list = soup.find_all("div", {"class": "article_content"})
                    text = "".join(
                        t.text.replace("\r", "").replace("\n", "").replace('</p>', '').replace('<p>', '') for t in
                        text_list)
                    text = re.sub('[a-zA-Z]', '', text)
                    text = text[0:50]
                    if_no_url = html_list[0]
                    if_no_context = text
                html_list.clear()
                date_list.clear()
                content_list.clear()
    else:
        html_string = ""
        content_string = ""
        url = "https://news.tvbs.com.tw/hot?from=click_hot"
        response = rq.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        sel = soup.select("div.content_center_contxt_real_news li a", limit=3)
        for ele in sel:
            html_string += "https://news.tvbs.com.tw/" + ele["href"]
            url = "https://news.tvbs.com.tw/" + ele["href"]
            response = rq.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            se = soup.find_all("div", {"class": "article_content"})
            text = "".join(t.text.replace("\r", "").replace("\n", "").replace('</p>', '').replace('<p>', '') for t in se)
            text = text[0:50]
            content_string += text
            if ele != sel[-1]:
                content_string += "\n"
                html_string += "\n"
        content_string = re.sub('[a-zA-Z]', '', content_string)
        return [html_string, content_string]
    return [if_no_url, if_no_context]



