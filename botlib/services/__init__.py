# @formatter:off, this is for avoiding circular type import
from typing import TYPE_CHECKING
if TYPE_CHECKING :
    from botlib.semantic_analyzer import SemanticAnalyzer
# @formatter:on

from enum import Enum

# project libs
from botlib.api.hanlpapi import HanlpApi
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
    Choose Service By Using Semantic Analyzed Result
    
    :param analyzer: Semantic Analyzer
    :return: request response, return None if Service Matching Error Happened
    """

    # choose target service with analyzer.target_service
    if analyzer.service == Services.UNKNOWN :
        msg = f"非常抱歉，我聽不懂您的需求 ({analyzer.speech_text})"
        BotLogger.info(f"Unknown Request = {analyzer.parsed_content}")
        return BotResponse.make_inform_response(msg, analyzer.response_language)

    if analyzer.service == Services.SEARCH_NEWS :
        BotLogger.info(analyzer.__str__())

        url_text = news.search_news(analyzer.time_range, analyzer.keywords, analyzer.media)

        if url_text[0] == "NO_URL" :
            return BotResponse.make_inform_response("找不到相符的新聞", language = analyzer.response_language)

        return BotResponse.make_news_response(url_text = url_text, language = analyzer.response_language)

    elif analyzer.service == Services.SEARCH_ACTIVITY :
        BotLogger.info(analyzer.__str__())

        result = activity.search_activity(analyzer.keywords, analyzer.time_range)


        if result is None :
            return BotResponse.make_inform_response("找不到活動", analyzer.response_language)
        else :
            # get main location from result text using hanlp api
            location = HanlpApi.extract_location(result)
            return BotResponse.make_activity_response(result, location, analyzer.response_language)

    elif analyzer.service == Services.CREATE_ACTIVITY :
        BotLogger.info(analyzer.__str__())

        # TODO : reject ambiguous content
        ambiguous_loc = (analyzer.locations == [])

        if ambiguous_loc :
            return BotResponse.make_inform_response("地點不明，請補上活動舉辦的地點後再說一次", analyzer.response_language)
        else :
            result = activity.create_activity(analyzer.parsed_content, analyzer.time_range)
            return BotResponse.make_inform_response(result, analyzer.response_language)

    else :
        BotLogger.critical("Service Matching Error. Should Never Be Here.")
        return None