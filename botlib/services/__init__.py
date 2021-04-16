# @formatter:off, this is for avoiding circular type import
from typing import TYPE_CHECKING
if TYPE_CHECKING :
    from botlib.semantic_analyzer import SemanticAnalyzer
# @formatter:on

from enum import Enum

# project libs
from botlib.botlogger import BotLogger
from botlib.services import news, activity
from botlib.botresponse import BotResponse



class Services(Enum) :
    UNKNOWN = "無法辨識服務"
    SEARCH_NEWS = "查詢新聞"
    CREATE_ACTIVITY = "新增活動"
    SEARCH_ACTIVITY = "查詢活動"


# ------------------------------------------------------------------------------------------------------------


def match_service( analyzer: 'SemanticAnalyzer' ) -> BotResponse or None :
    """
    Choose Service Via Semantic Analyzed Result Info
    
    :param analyzer: Semantic Analyzer
    :return: request response, return None if Service Matching Error Happened
    """

    # choose target service with analyzer.target_service
    if analyzer.service == Services.UNKNOWN :
        BotLogger.info(f"Unknown Request = {analyzer.parsed_content}")
        return BotResponse.make_inform_response("非常抱歉，我聽不懂您的需求")

    if analyzer.service == Services.SEARCH_NEWS :
        BotLogger.info(f"Search News Request ({analyzer.media}) : \n"
                       f"Parse Content  = {analyzer.parsed_content} \n"
                       f"Time Range     = {analyzer.time_range}) \n"
                       f"Keywords       = {analyzer.keywords}")

        url_text = news.search_news(analyzer.time_range, analyzer.keywords, analyzer.media)
        return BotResponse.make_news_response(news_url = url_text[0], news_content = url_text[1])

    elif analyzer.service == Services.SEARCH_ACTIVITY :
        BotLogger.info(f"Search Activity Request : \n"
                       f"Parse Content  = {analyzer.parsed_content} \n"
                       f"Time Range     = {analyzer.time_range}) \n"
                       f"Keywords       = {analyzer.keywords}")

        result = activity.search_activity(analyzer.keywords, analyzer.time_range)
        if result is None :
            return BotResponse.make_inform_response("找不到活動")
        else :
            return BotResponse.make_activity_response(result)

    elif analyzer.service == Services.CREATE_ACTIVITY :
        BotLogger.info(f"Create Activity Request : \n"
                       f"Parse Content  = {analyzer.parsed_content} \n"
                       f"Time Range     = {analyzer.time_range}) \n"
                       f"Keywords       = {analyzer.keywords}")

        result = activity.create_activity(analyzer.parsed_content, analyzer.time_range)
        return BotResponse.make_inform_response(result)

    else :
        BotLogger.critical("Service Matching Error. Should Never Be Here.")
        return None