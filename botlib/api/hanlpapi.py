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


class HanlpApi :
    """

    """
    URL = BotConfig.HANLP_URL


    # -----------------------------------------------------------------------------------------
    # Call Server API to do WS, POS, NER
    #
    # default interface : for multiple sentences (list of sentence)
    # alternative interface : for single sentence (string)

    @staticmethod
    def parse_sentences( sentences: list, ws_custom_dict: list or dict or None ) -> dict or None :
        """
        do WS, POS, NER on each sentence(string) in sentences(list) base on custom_dict()
        TODO

        default interface to call Server HanLP API

        :param sentences: list of sentence(string)
        :param ws_custom_dict:
        :return:
        """

        custom_dict = { }

        # make custom dict fit hanlp custom dict format
        if type(ws_custom_dict) is None :
            custom_dict = { }
        elif type(ws_custom_dict) is list :
            for word in ws_custom_dict :
                custom_dict[word] = ""

        # 將「句子」、「自訂斷詞字典」打包成單一字典
        data_dict = { "sentences" : sentences, "custom_dict" : custom_dict }

        # 將上面打包出的單一字典轉換成 json 格式，然後 POST 到 hanlp api
        response = post(HanlpApi.URL, json = json.dumps(data_dict))

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
    def parse_sentence( sentence: str, ws_custom_dict: list or dict or None ) -> dict or None :
        ws_pos_ner = HanlpApi.parse_sentences([sentence], ws_custom_dict)

        sentence_result = {
            "WS" : ws_pos_ner["WS"][0],
            "POS" : ws_pos_ner["POS"][0],
            "NER" : ws_pos_ner["NER"][0]
        }

        return sentence_result


    # -----------------------------------------------------------------------------------------------
    # Other Methods to parse WS, POS, NER results
    #
    # default interfaces :
    #   classify common words: classify words of a sentence into a dict with common catalogs (base on NER result)
    #   extract keywords: extract keywords from a sentence (base on WS and POS result)
    #
    # alternative interfaces:
    #   classify common words of 'list of sentences'
    #   extract keywords of 'list of sentences'

    @staticmethod
    def classify_common_words( ner_result: list ) -> dict or None :
        """

        :param ner_result:
        :return:
        """

        result = None
        try :
            # make a empty dict with common catalogs as KEY (with empty list as VALUE)
            common_cats = NerCatalogs.value_list()
            catalog_dict = { value : [] for value in common_cats }

            # check ner type of every word in list
            for word_ner_result in ner_result :
                if word_ner_result[1] in common_cats :
                    catalog_dict[word_ner_result[1]].append(word_ner_result[0])

            result = catalog_dict

        except IndexError :
            BotLogger.exception(f"Index Error,\n Your NER result List is {ner_result}")

        except Exception as e :
            BotLogger.exception(f"{type(e).__name__} = {e}")

        finally :
            return result


    @staticmethod
    def classify_common_words_of_sentences( ner_results: list ) -> list or None :
        """

        :param ner_results:
        :return:
        """

        result = None
        try :
            # get classification result of each sentence in sentences list
            classifications = []
            for sentence_ner_result in ner_results :
                classifications.append(HanlpApi.classify_common_words(sentence_ner_result))

            result = classifications

        except IndexError :
            BotLogger.exception(f"Index Error,\n Your list of NER result list is {ner_results}")
        except Exception as e :
            BotLogger.exception(f"{type(e).__name__} = {e}")

        finally :
            return result


    @staticmethod
    def extract_keywords( ws_result: list, pos_result: list ) -> list or None :
        """

        :param ws_result:
        :param pos_result:
        :return:
        """

        result = None
        try :

            keywords = []

            # check each tokens in ws_result
            for i, token in enumerate(ws_result) :

                # check pos type of this token
                if pos_result[i] in ["NN", "NR"] :
                    keywords.append(token)

            result = keywords

        except IndexError :
            error_msg = "Index Error,\n"
            error_msg += f"Your WS result list is : {ws_result}\n"
            error_msg += f"Your POS result list is : {pos_result}"
            BotLogger.exception(error_msg)

        except Exception as e :
            BotLogger.exception(f"{type(e).__name__} = {e}")

        finally :
            return result


    @staticmethod
    def extract_keywords_of_sentences( ws_results: list, pos_results: list ) -> list or None :
        """

        :param ws_results:
        :param pos_results:
        :return:
        """

        result = None
        try :

            keywords_list = []

            # get keywords of each sentence base on their ws, ner result
            for i, ws_result in enumerate(ws_results) :
                keywords_list.append(HanlpApi.extract_keywords(ws_result, pos_results[i]))

            result = keywords_list


        except IndexError :
            pass
        except Exception as e :
            BotLogger.exception(f"{type(e).__name__} = {e}")

        finally :
            return result


if __name__ == '__main__' :
    HanlpApi.URL = "https://linebotdemo.loca.lt/HANLP"
    sentences = ["2018年4點10分中", "如果一個網站可以提供比較快速的台積電網路服務", "今天中國時報關於盧文祥的新聞"]

    ws_pos_ner_list = HanlpApi.parse_sentences(sentences, [])
    ws_pos_ner = HanlpApi.parse_sentence(sentences[1], [])

    keywords_list = HanlpApi.extract_keywords_of_sentences(ws_pos_ner_list["WS"], ws_pos_ner_list["POS"])
    keywords = HanlpApi.extract_keywords(ws_pos_ner["WS"], ws_pos_ner["POS"])

    classification_list = HanlpApi.classify_common_words_of_sentences(ws_pos_ner_list["NER"])
    classification = HanlpApi.classify_common_words(ws_pos_ner["NER"])

    print(ws_pos_ner_list)
    print(ws_pos_ner)