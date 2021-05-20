import requests as rq
from bs4 import BeautifulSoup
import re
import datetime
from selenium import webdriver
import time
from pathlib import Path

html_list = []
title_list = []
content_list = []
date_list = []


def parse(keyword: list, ty: (datetime, datetime)):
    if_no_url = "NO_URL"
    if_no_context = "找不到相符結果"
    search_string = "https://udn.com/search/word/2/"
    if keyword:
        for ele in keyword :
            search_string = search_string + ele
            if ele != keyword[-1] :
                search_string = search_string + "%20"

        # set selenium web driver
        driver_path = Path.joinpath(Path(__file__).parent, "chromedriver")
        options = webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")
        chrome = webdriver.Chrome(driver_path, options = options)

        # open chrome
        chrome.get(search_string)
        chrome.fullscreen_window()
        for x in range(1, 6) :
            chrome.execute_script("window.scrollTo(0,document.body.scrollHeight)")
            time.sleep(0.5)
        # get soup
        soup = BeautifulSoup(chrome.page_source, 'html.parser')
        # check result
        sel = soup.find("div", "search-total")
        sel = sel.find("span").text

        if sel != "0":
            sel = soup.select("div.story-list__text h2 a")
            for ele in sel:
                html_list.append(ele["href"])
            sel = soup.select("time.story-list__time")
            for ele in sel:
                date = ele.text
                date_list.append(date[:10]+" 00:00")
            sel = soup.select("div.story-list__text p")
            for ele in sel:
                content_list.append(ele.text)
            if_no_url = html_list[0]
            if_no_context = content_list[0]
            for i in range(0, len(html_list)):
                date = datetime.datetime.strptime(str(date_list[i]), '%Y-%m-%d %H:%M')
                if ty[0] <= date <= ty[1]:
                    content_list[i] = re.sub('[a-zA-Z]', '', content_list[i])
                    content_list[i] = content_list[i].replace(u'\u3000', u' ').replace('\n', '')
                    if content_list[i].find("。"):
                        content_list[i] = content_list[i][:content_list[i].find("。")]
                    elif len(content_list[i]) > 50:
                        content_list[i] = content_list[i][:50]
                    return [html_list[i], content_list[i]]
                if i == 0:
                    if_no_url = html_list[0]
                    content_list[0] = re.sub('[a-zA-Z]', '', content_list[0])
                    if_no_context = content_list[0].replace(u'\u3000', u' ').replace('\n', '')
                    if if_no_context.find("。"):
                        if_no_context = if_no_context[:if_no_context.find("。")]
                    elif len(if_no_context) > 50:
                        if_no_context = if_no_context[:50]
        chrome.close()

    else:
        html_string = ""
        content_string = ""
        url = "https://udn.com/rank/pv/2"
        response = rq.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        sel = soup.select("div.story-list__text h2 a", limit=3)
        for ele in sel:
            html_string += ele["href"]
            if ele != sel[-1]:
                html_string += "\n"
        sel = soup.select("div.story-list__text p", limit=3)
        for ele in sel:
            content_string += ele.text.replace(u'\u3000', u' ').replace('\n', '')
            if ele != sel[-1]:
                content_string += "\n"
        content_string = re.sub('[a-zA-Z]', '', content_string)
        return [html_string, content_string]
    return [if_no_url, if_no_context]


