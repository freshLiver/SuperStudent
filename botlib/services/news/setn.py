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
    search_string = "https://www.setn.com/search.aspx?q="
    if keyword:
        last_page = False
        for ele in keyword:
            search_string = search_string + ele
            if ele != keyword[-1]:
                search_string = search_string + "%20"
        for i in range(1, 6):
            url = search_string + "&p=" + str(i)
            response = rq.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            sel = soup.select("div.newsimg-area-info a")

            # get_html
            for ele in sel:
                html_list.append("https://www.setn.com/" + ele["href"])
            if len(html_list) < 36:
                last_page = True

            # get_date
            for ele in soup.select("div.newsimg-date"):
                date_list.append(ele.text)

            # get_context
            for ele in soup.select("div.newsimg-area-info a"):
                content_list.append(ele.text)

            for j in range(0, len(html_list)):
                date = datetime.datetime.strptime(str(date_list[j]), '%Y/%m/%d %H:%M')
                if ty[0] <= date <= ty[1]:
                    content_list[j] = re.sub('[a-zA-Z]', '', content_list[j])
                    content_list[j] = content_list[j].replace(u'\u3000', u' ').replace('\n', '')
                    return [html_list[j], content_list[j]]
            if last_page:
                break
            if i == 1:
                if_no_url = html_list[0]
                content_list[0] = re.sub('[a-zA-Z]', '', content_list[0])
                if_no_context = content_list[0].replace(u'\u3000', u' ').replace('\n', '')
            html_list.clear()
            date_list.clear()
            content_list.clear()

    else:
        html_string = ""
        content_string = ""
        url = "https://www.setn.com/ViewAll.aspx?PageGroupID=0"
        response = rq.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        sel = soup.select("h3.view-li-title a", limit=3)
        for ele in sel:
            html = ele["href"]
            if html.find("http"):
                html = "https://www.setn.com/" + html
            html_string += html
            response = rq.get(html)
            soup = BeautifulSoup(response.text, 'html.parser')
            text = soup.find("div", id="ckuse").text
            text = text.replace("\r", "").replace("\n", "")
            text = text[text.find("報導")+2:text.find("報導")+52]
            content_string += text
            if ele != sel[-1]:
                content_string += "\n"
                html_string += "\n"
        content_string = re.sub('[a-zA-Z]', '', content_string)
        return [html_string, content_string]
    return [if_no_url, if_no_context]