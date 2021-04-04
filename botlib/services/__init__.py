# @formatter:off, this is for avoiding circular type import
from typing import TYPE_CHECKING
if TYPE_CHECKING :
    from botlib.semantic_analyzer import SemanticAnalyzer
# @formatter:on

import re
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


def extract_media( cht_text: str ) -> news.AvailableMedia :
    """
    Find Media From pnList From NER Result
    
    :param cht_text: pnList from ner info
    :return: news.AvailableMedia (default media is news.AvailableMedia.NCKU)
    """

    # TODO find available media from pn List
    if re.search("自由時報", cht_text) :
        return news.AvailableMedia.LTN
    if re.search("(中國時報|中時(電子報)?)", cht_text) :
        return news.AvailableMedia.CHINATIME
    if re.search("TVBS", cht_text) :
        return news.AvailableMedia.TVBS
    if re.search("ETTODAY(新聞雲)?", cht_text) :
        return news.AvailableMedia.ETTODAY
    if re.search("(UDN|聯合報)", cht_text) :
        return news.AvailableMedia.UDN

    # default news media is NCKU news
    return news.AvailableMedia.NCKU


# ------------------------------------------------------------------------------------------------------------


def match_service( analyzer: 'SemanticAnalyzer' ) -> str :
    """
    Choose Service Via Semantic Analyzed Result Info
    
    :param analyzer: Semantic Analyzer
    :return: request response
    """

    # choose target service with analyzer.target_service
    if analyzer.service == Services.UNKNOWN :
        BotLogger.info("Unknown Request")
        return "非常抱歉，我聽不懂您的需求"

    keywords = analyzer.obj_list + analyzer.pn_list + analyzer.loc_list
    events = analyzer.event_list

    if analyzer.service == Services.SEARCH_NEWS :
        BotLogger.info("Search News Request")
        media = extract_media(analyzer.parsed_content)
        return news.search_news(analyzer.time, keywords, media)

    elif analyzer.service == Services.SEARCH_ACTIVITY :
        BotLogger.info("Search Activity Request")
        return activity.search_activity(analyzer.pn_list, events, analyzer.time, analyzer.loc_list)

    elif analyzer.service == Services.CREATE_ACTIVITY :
        BotLogger.info("Create Activity Request")
        return activity.create_activity(analyzer.parsed_content)

    else :
        BotLogger.critical("Service Matching Error. Should Never Be Here.")