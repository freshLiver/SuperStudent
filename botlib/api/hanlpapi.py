import json
from requests import post
from enum import Enum

# project libs
from botlib import BotConfig
from botlib.botlogger import BotLogger



class NerCatalogs(Enum) :
    @classmethod
    def value_list( cls ) -> list :
        return [cat.value for cat in cls]


    PERSON = "PERSON"
    ORGANIZATION = "ORGANIZATION"
    DATE = "DATE"
    TIME = "TIME"
    LOCATION = "LOCATION"


class HanlpAPI :
    """

    """
    URL = BotConfig.HANLP_URL


    @staticmethod
    def parse_sentences( sentences: list, ws_custom_dict: list or dict or None ) -> dict or None :

        #
        custom_dict = { }

        if type(ws_custom_dict) is None :
            custom_dict = { }
        elif type(ws_custom_dict) is list :
            for word in ws_custom_dict :
                custom_dict[word] = ""

        # 將「句子」、「自訂斷詞字典」打包成單一字典
        data_dict = { "sentences" : sentences, "custom_dict" : custom_dict }

        # 　將上面打包出的單一字典轉換成 json 格式，然後 POST 到 hanlp api
        response = post(HanlpAPI.URL, json = json.dumps(data_dict))

        if response.status_code == 200 :
            try :
                return json.loads(response.text)
            except TypeError :
                BotLogger.exception(f"TypeError, HanlpAPI return non json file : \n {response.text}")
                return None

        else :
            BotLogger.error(f"Request Error, Error Code = {response.status_code}")
            return None


    @staticmethod
    def classify_ner_msra_results( ner_results: list ) -> list :
        """

        :param ner_results: NER/MSRA result of SINGLE SENTENCE str, it should be a 3d list
        :return: a list of dicts that classify NER results into some common catalogs
        """

        # get values of a enum that enumerates common catalogs
        catalog_values = NerCatalogs.value_list()

        # try to classify every ner result of sentences
        classification_results = []
        for ner_result in ner_results :
            result = { cat : [] for cat in catalog_values }

            # classify ner result of this sentence
            for word_ner in ner_result :
                # only extract needed catalogs
                if word_ner[1] in catalog_values :
                    result[word_ner[1]].append(word_ner[0])

            classification_results.append(result)

        # return list of dicts
        return classification_results


    @staticmethod
    def extract_keywords( ws_results: list, pos_results: list ) -> list :
        """

        :param ws_results: ws results of list of sentences
        :param pos_results: pos results of list of sentences
        :return: list of keywords extracted from each sentences
        """

        keywords_list = []

        # check each sentence's pos result
        for iSentence in range(len(ws_results)) :

            # check pos type of each ws tokens in this sentence
            keyword_set = set()
            for iWord in range(len(ws_results[iSentence])) :

                # extract needed pos type
                if pos_results[iSentence][iWord] in ["NN", "NR"] :
                    keyword_set.add(ws_results[iSentence][iWord])

            # convert keyword set to list and append to result list
            keywords_list.append(list(keyword_set))

        return keywords_list


if __name__ == '__main__' :
    HanlpAPI.URL = "https://linebotdemo.loca.lt/HANLP"
    sentences = ["2018年4點10分中", "如果一個網站可以提供比較快速的台積電網路服務", "今天中國時報關於盧文祥的新聞"]

    ws_pos_ner = HanlpAPI.parse_sentences(sentences, [])

    keywords = HanlpAPI.extract_keywords(ws_pos_ner["WS"], ws_pos_ner["POS"])
    print(keywords)
    classify_result = HanlpAPI.classify_ner_msra_results(ws_pos_ner["NER"])
    print(classify_result)