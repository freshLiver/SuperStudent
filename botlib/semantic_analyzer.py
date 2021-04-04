# project libs
import datetime

from botlib.api.labapi import LabApi
from botlib.botlogger import BotLogger
from botlib.converter.datetime_converter import DatetimeConverter
from botlib.services import Services



class SemanticAnalyzer :
    """
    Semantic Analyze Input Speech Text
    This Class Try To Find Out These Info With NER:
    1. Target Service
    2. pnList, Events, Datetime Range, Locations
    """


    # ------------------------------------------------------------------------------------------------------------


    # ------------------------------------------------------------------------------------------------------------


    def __init__( self, speech_text: str ) :
        # text will be parsed
        self.speech_text = speech_text
        self.parsed_content = DatetimeConverter.standardize_datetime(speech_text)

        # info dict for target service
        self.obj_list = []
        self.pn_list = []
        self.event_list = []
        self.time = DatetimeConverter.extract_datetime(self.parsed_content)
        self.loc_list = []

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
            BotLogger.info("NER Error.")
            return

        # TODO (MUST IMPROVE THIS) : extract info from ner result (if result not None)
        self.obj_list = ner_dict['objList']
        self.pn_list += list(ner_dict['pnList'])
        self.event_list += list(ner_dict['fullEventList'])
        self.loc_list += list(ner_dict['locList'])

        # determine service
        if self.is_search_news() :
            self.service = Services.SEARCH_NEWS

        elif self.event_list != [] or "活動" in self.obj_list :
            if self.is_search_activity() :
                self.service = Services.SEARCH_ACTIVITY
            elif self.is_create_activity() :
                self.service = Services.CREATE_ACTIVITY
            else :
                self.service = Services.SEARCH_NEWS

        else :
            self.service = Services.UNKNOWN
            BotLogger.info("Unknown Service")

        BotLogger.info("Parsing Speech Text Done.")


    def is_search_news( self ) -> bool :
        """
        user request a news searching service or not

        :return: is a news searching request
        """
        if "新聞" in self.parsed_content :
            BotLogger.info("Is Search News")
            return True
        return False


    def is_search_activity( self ) -> bool :
        """
        user request a activity searching service or not

        :return: is a activity searching request
        """
        for keyword in ["查詢", "什麼", "想知道", "哪些"] :
            if keyword in self.parsed_content :
                BotLogger.info("Is Search Activity")
                return True
        return False


    def is_create_activity( self ) -> bool :
        """
        user request a activity creating service or not

        :return: is a activity searching request
        """
        for keyword in ["有", "舉行", "舉辦"] :
            if keyword in self.parsed_content :
                BotLogger.info("Is Create Activity")
                return True
        return False