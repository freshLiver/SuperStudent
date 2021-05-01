# project libs
import re

from botlib.api.labapi import LabApi
from botlib.botlogger import BotLogger
from botlib.converter.datetime_converter import DatetimeConverter
from botlib.services import Services, news
from botlib.botresponse import BotResponseLanguage



class SemanticAnalyzer :
    """
    Semantic Analyze Input Speech Text
    This Class Try To Find Out These Info With NER:
    1. Target Service
    2. pnList, Events, Datetime Range, Locations
    """


    def __init__( self, speech_text: str ) :

        # should parse and rm language specification part to avoid keywords mismatching
        self.speech_text, self.response_language = self.__change_response_language(speech_text)

        # must pass
        self.parsed_content = DatetimeConverter.standardize_datetime(self.speech_text)
        self.time_range = DatetimeConverter.extract_datetime(self.parsed_content)

        # info dict for target service
        self.obj_list = []
        self.pn_list = []
        self.event_list = []
        self.loc_list = []
        self.keywords = []

        # media extract from speech text
        self.media = news.AvailableMedia.NCKU

        # result types
        self.service = Services.UNKNOWN


    # ------------------------------------------------------------------------------------------------------------
    @staticmethod
    def __change_response_language( speech_text ) -> (str, BotResponseLanguage) :
        """
        extract and rm language specification part from speech text to avoid keywords mismatching

        :return: tuple of  (speech text without language specification parts, BotResponseLanguage obj)
        """

        # extract language specification part from speech text
        chinese_rule = "(以|用)(中文|國語)((告訴|回答|回覆)我?|說)"
        taiwanese_rule = "(以|用)(閩南語|台語|臺語)((告訴|回答|回覆)我?|說)"

        if re.search(chinese_rule, speech_text) is not None :
            speech_text = re.sub(chinese_rule, "", speech_text)
            return speech_text, BotResponseLanguage.CHINESE

        if re.search(taiwanese_rule, speech_text) is not None :
            speech_text = re.sub(taiwanese_rule, "", speech_text)
            return speech_text, BotResponseLanguage.TAIWANESE

        return speech_text, BotResponseLanguage.CHINESE


    def __generate_keywords_list( self ) :

        # use loc, pn, obj as keywords
        self.keywords = self.obj_list + self.pn_list + self.loc_list

        # rm repeat items
        self.keywords = list(set(self.keywords))
        # rm useless keywords
        for kw in self.keywords.copy() :
            # rm single word
            if len(kw) < 2 :
                self.keywords.remove(kw)
            elif kw in ["新聞", "報導", "活動"] :
                self.keywords.remove(kw)
            # rm media keyword
            elif SemanticAnalyzer.__extract_media(kw) is not None :
                self.keywords.remove(kw)


    @staticmethod
    def __extract_media( cht_text: str ) -> news.AvailableMedia or None :
        """
        Find Media From pnList From NER Result

        :param cht_text: pnList from ner info
        :return: news.AvailableMedia, None for no media Found
        """

        # find available media from pn List
        if re.search("自由時報", cht_text) :
            return news.AvailableMedia.LTN
        if re.search("(中國時報|中時(電子報)?)", cht_text) :
            return news.AvailableMedia.CHINATIME
        if re.search("TVBS", cht_text, re.IGNORECASE) :
            return news.AvailableMedia.TVBS
        if re.search("(東森|ETTODAY|新聞雲)", cht_text, re.IGNORECASE) :
            return news.AvailableMedia.ETTODAY
        if re.search("(UDN|聯合報)", cht_text, re.IGNORECASE) :
            return news.AvailableMedia.UDN
        if re.search("(成大|成功大學)", cht_text) :
            return news.AvailableMedia.NCKU

        return None


    # ------------------------------------------------------------------------------------------------------------


    def parse_content( self ) -> None :
        """
        do NER on input speech text vis Lab API
        and determine target Service base on NER result
        
        :return: None
        """

        # parse modified user speech with NER
        ner_dict = LabApi.lab_ner_api(self.parsed_content)
        BotLogger.info(f"{{{self.parsed_content}:{ner_dict}}}")

        # ner get nothing
        if ner_dict is None :
            BotLogger.error("NER Error.")
            return

        # NER result
        self.obj_list = ner_dict['objList']
        self.pn_list += list(ner_dict['pnList'])
        self.event_list += list(ner_dict['fullEventList'])
        self.loc_list += list(ner_dict['locList'])

        # extract media from speech text
        media = SemanticAnalyzer.__extract_media(self.speech_text)
        if media is not None :
            self.media = media

        # generate keywords list from ner result
        self.__generate_keywords_list()

        # determine service type
        if self.is_search_news() :
            self.service = Services.SEARCH_NEWS

        elif self.is_activity() :
            if self.is_search_activity() :
                self.service = Services.SEARCH_ACTIVITY
            elif self.is_create_activity() :
                self.service = Services.CREATE_ACTIVITY
            else :
                self.service = Services.SEARCH_ACTIVITY

        else :
            self.service = Services.UNKNOWN
            BotLogger.info("Unknown Service")

        BotLogger.debug("Parsing Speech Text Done.")


    def is_search_news( self ) -> bool :
        """
        user request a news searching service or not

        :return: is a news searching request
        """
        for kw in ["新聞", "報導"] :
            if kw in self.parsed_content :
                return True
        return False


    def is_activity( self ) -> bool :
        """
        user request a activity searching or creating service or not

        :return: is a activity request
        """
        for kw in ["活動", "考試", "展", "演講"] :
            if kw in self.obj_list :
                return True
        return self.event_list != []


    def is_search_activity( self ) -> bool :
        """
        user request a activity searching service or not

        :return: is a activity searching request
        """
        for keyword in ["查詢", "什麼", "想知道", "哪些"] :
            if keyword in self.parsed_content :
                return True
        return False


    def is_create_activity( self ) -> bool :
        """
        user request a activity creating service or not

        :return: is a activity searching request
        """
        for keyword in ["有", "舉行", "舉辦"] :
            if keyword in self.parsed_content :
                return True
        return False