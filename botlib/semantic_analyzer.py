# project libs
import re

from botlib.api.labapi import LabApi
from botlib.botlogger import BotLogger
from botlib.converter.datetime_converter import DatetimeConverter
from botlib.services import Services, news



class SemanticAnalyzer :
    """
    Semantic Analyze Input Speech Text
    This Class Try To Find Out These Info With NER:
    1. Target Service
    2. pnList, Events, Datetime Range, Locations
    """


    # ------------------------------------------------------------------------------------------------------------

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
            elif kw in ["新聞", "報導"] :
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

        # TODO find available media from pn List
        if re.search("自由時報", cht_text) :
            return news.AvailableMedia.LTN
        if re.search("(中國時報|中時(電子報)?)", cht_text) :
            return news.AvailableMedia.CHINATIME
        if re.search("TVBS", cht_text) :
            return news.AvailableMedia.TVBS
        if re.search("(東森|ETTODAY|新聞雲)", cht_text) :
            return news.AvailableMedia.ETTODAY
        if re.search("(UDN|聯合報)", cht_text) :
            return news.AvailableMedia.UDN
        if re.search("(成大|成功大學)", cht_text) :
            return news.AvailableMedia.NCKU

        return None


    # ------------------------------------------------------------------------------------------------------------


    def __init__( self, speech_text: str ) :
        # text will be parsed
        self.speech_text = speech_text
        self.parsed_content = DatetimeConverter.standardize_datetime(speech_text)
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

        # determine service
        if self.is_search_news() :
            self.service = Services.SEARCH_NEWS

        elif self.event_list != [] or "活動" in self.obj_list :
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