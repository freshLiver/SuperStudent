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


def __extract_media( cht_text: str ) -> news.AvailableMedia :
    """
    Find Media From pnList From NER Result
    
    :param cht_text: pnList from ner info
    :return: news.AvailableMedia (default media is news.AvailableMedia.NCKU)
    """

    # TODO find available media from pn List
    if re.search("(中國時報|中時(電子報)?)", cht_text) :
        return news.AvailableMedia.CHINATIME

    # default news media is NCKU news
    return news.AvailableMedia.NCKU


def service_matching( analyzer: 'SemanticAnalyzer' ) -> str :
    """
    Choose Service Via Semantic Analyzed Result Info
    
    :param analyzer: Semantic Analyzer
    :return: request response
    """

    # choose target service with analyzer.target_service
    if analyzer.target_service == Services.UNKNOWN :
        BotLogger.info("Unknown Request")
        return "非常抱歉，我聽不懂您的需求"


    elif analyzer.target_service == Services.SEARCH_NEWS :
        # convert raw ner info into news service param format
        time_range = analyzer.time_range
        keywords = analyzer.obj_list
        available_media = __extract_media(analyzer.parsed_content)

        BotLogger.info("News Request")
        return news.find_news(time_range, keywords, available_media)


    elif analyzer.target_service is Services.SEARCH_ACTIVITY or Services.CREATE_ACTIVITY :
        # convert raw ner info into activity param format
        people = analyzer.pn_list
        events = analyzer.events
        time_range = analyzer.time_range
        location = analyzer.locations

        # TODO : search or create activity
        BotLogger.info("Activity Request")
        if analyzer.target_service == Services.SEARCH_ACTIVITY :
            return activity.find_activity(people, events, time_range, location)
        return activity.create_activity(people, events, time_range, location)


    else :
        BotLogger.critical("Service Matching Error. Should Not Be Here.")