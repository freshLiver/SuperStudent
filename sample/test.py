from sys import path

from botlib import BotConfig
from botlib.api.hanlpapi import HanlpApi
from botlib.semantic_analyzer import SemanticAnalyzer
from botlib.services import match_service



path.append("..")

if __name__ == '__main__' :

    HanlpApi.URL = BotConfig.HANLP_TEST_URL

    # text = "三月七號台南火車站有發放免費便當的活動"
    # text = "六月四號成大資工系館會舉辦專題展"
    text = "三天後會在成功大學有什麼活動"
    analyzer = SemanticAnalyzer(text)
    analyzer.parse_content()
    res = match_service(analyzer)
    print(res)