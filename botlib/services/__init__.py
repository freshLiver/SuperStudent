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
    根據語意辨識的結果選擇對應服務
    
    :param analyzer: Semantic Analyzer instance
    :return: 根據 service 回傳一個 BotResponse, 如果不屬於任何 service 則回傳 None
    """

    BotLogger.info(analyzer.__str__())
    # 根據 analyzer (語意辨識結果) 選擇對應 service
    #
    #
    # 辨識結果為：不知道要做什麼服務
    # * 回傳 INFORM RESPONSE 並附上辨識結果
    #
    if analyzer.service == Services.UNKNOWN :
        error_msg = f"非常抱歉，我聽不懂您的需求 ({analyzer.speech_text})"
        BotLogger.info(f"Unknown Request = {analyzer.parsed_content}")
        return BotResponse.make_inform_response(analyzer.speech_text, error_msg, analyzer.response_language)
    #
    #
    # 辨識結果為：搜尋新聞
    # * 沒找到新聞：回傳 INFORM RESPONSE 並附上辨識結果
    # * 有找到新聞：回傳 NEWS RESPONSE（包含新聞網址以及簡介）
    #
    if analyzer.service == Services.SEARCH_NEWS :

        #  根據「時間範圍」、「關鍵字」搜尋指定的「新聞媒體」
        url_text = news.search_news(analyzer.time_range, analyzer.keywords, analyzer.media)

        if url_text[0] == "NO_URL" :
            not_found_msg = f"找不到相符的新聞 ({analyzer.speech_text})"
            return BotResponse.make_inform_response(analyzer.speech_text, not_found_msg, analyzer.response_language)

        return BotResponse.make_news_response(analyzer.speech_text, url_text, analyzer.response_language)
    #
    #
    # 辨識結果為：搜尋活動
    # * 沒找到活動：回傳 INFORM RESPONSE 並附上辨識結果
    # * 有找到活動：回傳 ACTIVITY RESPONSE (包含位置資訊)
    #
    elif analyzer.service == Services.SEARCH_ACTIVITY :

        # 根據「時間範圍」以及「關鍵字」搜尋資料庫中的活動資料
        result = activity.search_activity(analyzer.time_range, analyzer.keywords)

        if result is None :
            not_found_msg = f"找不到活動 ({analyzer.speech_text})"
            return BotResponse.make_inform_response(analyzer.speech_text, not_found_msg, analyzer.response_language)
        else :
            # 使用 hanlp 從「找到的活動」中找出 main location（longest location）
            location = HanlpApi.extract_location(result)
            return BotResponse.make_activity_response(analyzer.speech_text, result, location, analyzer.response_language)
    #
    #
    # 辨識結果為：新增活動
    # * 地點不明：回傳 INFORM RESPONSE 告知地點不明並附上辨識結果
    # * 地點明確：回傳 INFORM RESPONSE 告知新增活動成功並附上辨識結果
    #
    elif analyzer.service == Services.CREATE_ACTIVITY :

        # 如果地點不明確則無法新增活動
        ambiguous_location = (analyzer.locations == [])

        if ambiguous_location :
            error_msg = f"地點不明，請補上活動舉辦的地點後再說一次 ({analyzer.speech_text})"
            return BotResponse.make_inform_response(analyzer.speech_text, error_msg, analyzer.response_language)
        else :
            result = activity.create_activity(analyzer.parsed_content, analyzer.time_range)
            result += f"({analyzer.speech_text})"
            return BotResponse.make_inform_response(analyzer.speech_text, result, analyzer.response_language)
    #
    #
    # 不屬於任何 Service
    #
    #
    else :
        BotLogger.error("Service Matching Error. Should Never Be Here.")
        return None