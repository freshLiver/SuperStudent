# @formatter:off, this is for avoiding circular type import
from typing import TYPE_CHECKING
if TYPE_CHECKING :
    from botlib.semantic_analyzer import SemanticAnalyzer
# @formatter:on

from enum import Enum

# project libs
from botlib.botlogger import BotLogger
from botlib.services import news, activity



class Services(Enum) :
    UNKNOWN = "無法辨識服務"
    SEARCH_NEWS = "查詢新聞"
    CREATE_ACTIVITY = "新增活動"
    SEARCH_ACTIVITY = "查詢活動"


# ------------------------------------------------------------------------------------------------------------


def match_service( analyzer: 'SemanticAnalyzer' ) -> str :
    """
    Choose Service Via Semantic Analyzed Result Info
    
    :param analyzer: Semantic Analyzer
    :return: request response
    """

    # choose target service with analyzer.target_service
    if analyzer.service == Services.UNKNOWN :
        BotLogger.info(f"Unknown Request : {analyzer.parsed_content}")
        return "非常抱歉，我聽不懂您的需求"

    if analyzer.service == Services.SEARCH_NEWS :
        BotLogger.info(f"Search News Request {analyzer.parsed_content}")
        return news.search_news(analyzer.time_range, analyzer.keywords, analyzer.media)

    elif analyzer.service == Services.SEARCH_ACTIVITY :
        BotLogger.info(f"Search Activity Request {analyzer.parsed_content}")
        return activity.search_activity(analyzer.keywords, analyzer.time_range)

    elif analyzer.service == Services.CREATE_ACTIVITY :
        BotLogger.info(f"Create Activity Request {analyzer.parsed_content}")
        return activity.create_activity(analyzer.parsed_content, analyzer.time_range)

    else :
        BotLogger.critical("Service Matching Error. Should Never Be Here.")