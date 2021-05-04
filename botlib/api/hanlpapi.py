import json
from requests import post, HTTPError
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
    def parse_sentences( sentences: list, ws_custom_dict = None ) -> dict or None :
        """
        負責呼叫 HanLP API 進行 WS, POS, NER 處理
        會先對「由數個句子組成的 list」進行 WS，可使用 ws_custom_dict 進行自訂字典處理
        並用 WS 的結果進行 POS, NER 最後回傳一個 dict（包含 "WS", "POS", "NER" 三個 KEY）

        Exceptions:
            - TypeError : Wrong Param Type or HanLP API return non-json data
            - HTTPError : Request Error, status_code not 200
            - Other Errors : See Log

        :param sentences: 由數個要進行 WS, POS, NER 處理的句子（string）組成的 list
        :param ws_custom_dict: 自定義的斷詞 dict, default None 則為空的字典檔
        :return: 由 WS, POS, NER 組成的 dict，發生錯誤時則回傳 None
        """

        result = None
        try :

            # check sentences type
            if type(sentences) is not list :
                raise TypeError("Sentences Should Be A List.")

            # check custom dict type
            custom_dict: dict
            if ws_custom_dict is None :
                custom_dict = { }
            elif type(ws_custom_dict) is dict :
                custom_dict = ws_custom_dict
            else :
                raise TypeError("Custom Dict Should Be A Dict.")

            # 將「句子」、「自訂斷詞字典」打包成單一字典
            data_dict = {
                "sentences" : sentences,
                "custom_dict" : custom_dict
            }

            # 將上面打包出的單一字典轉換成 json 格式，然後 POST 到 hanlp api 的 address
            response = post(HanlpApi.URL, json = json.dumps(data_dict))

            # 檢查 post 結果是否為 200
            if response.status_code == 200 :
                try :
                    result = json.loads(response.text)
                except TypeError :
                    raise TypeError(f"TypeError, HanlpAPI return non json file : \n {response.text}")

            else :
                raise HTTPError(f"Status is not 200 ({response.status_code})")

        except (TypeError, HTTPError) as e :
            BotLogger.exception(e.__str__())

        except Exception as e :
            BotLogger.exception(f"{type(e).__name__} = {e}")

        finally :
            return result


    @staticmethod
    def parse_sentence( sentence: str, ws_custom_dict = None ) -> dict or None :
        """
        利用 HanLP API 對「某個」句子進行 WS, POS, NER
        會將 sentence 包成 list 然後經由 parse_sentences 進行處理
        並抽出 WS, POS, NER 結果的第一個 result（傳入 [sentence]）
        然後回傳由 WS, POS, NER 結果構成的 dict

        :param sentence: 要進行 WS, POS, NER 處理的句子（string）
        :param ws_custom_dict: 以 "WS", "POS", "NER" 為 KEY, token results 為 VALUE 的 dict
        :return: 由 WS, POS, NER 結果構成的 dict
        """

        ws_pos_ner = HanlpApi.parse_sentences([sentence], ws_custom_dict)

        if ws_pos_ner is None :
            return None
        else :
            return {
                "WS" : ws_pos_ner["WS"][0],
                "POS" : ws_pos_ner["POS"][0],
                "NER" : ws_pos_ner["NER"][0]
            }


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
        根據某「一」個句子的 NER 結果（list）檢查各個 token
        並抓出幾個常見的類別（例如：時間、地點）並建立 dict 儲存（catalog: list of tokens）

        Exceptions :
            - TypeError : Wrong Param Type, NER result should be a 2d array
            - IndexError : ner_result Should Be A 2D List
            - Other Errors : See Log

        :param ner_result: 某「一」句子的 NER 結果，應為 list of list
        :return: 常見類別的 dict，以常見的類別名稱為 KEY, token 組成的 list 則為 VALUE，發生錯誤時則會回傳 None
        """

        result = None
        try :
            # check ner_result type
            if type(ner_result) is not list :
                raise TypeError("NER Result Should Be A 2D List.")

            # make a empty dict with common catalogs as KEY (with empty list as VALUE)
            common_cats = NerCatalogs.value_list()
            catalog_dict = { value : [] for value in common_cats }

            # check ner type of every word in list
            for word_ner_result in ner_result :
                if word_ner_result[1] in common_cats :
                    catalog_dict[word_ner_result[1]].append(word_ner_result[0])

            result = catalog_dict
            BotLogger.debug(f"Catalogs Dict is : \n{result}")

        except TypeError as e :
            BotLogger.exception(e.__str__())

        except IndexError as e :
            BotLogger.exception(f"{e}\nMaybe Your ner_result is not A 2D array")

        except Exception as e :
            BotLogger.exception(f"{type(e).__name__} = {e}")

        finally :
            return result


    @staticmethod
    def classify_common_words_of_sentences( ner_results: list ) -> list or None :
        """
        與 classify_common_words 相似，但是用來處理「多個句子的 NER 結果」
        以「各個句子的 NER 結果組成的 list」作為 argument
        依據呼叫 classify_common_words 進行處理
        並回傳「各個句子的結果組成的 list」

        Exceptions（ return None ）:
            - TypeError : Wrong Param Type, ner results should be 3d list
            - Other Errors : See Log

        :param ner_results: 「各個句子的 NER 結果」組成的 list
        :return: 各個句子的結果組成的 list，發生錯誤時則回傳 None
        """

        result = None
        try :

            # check input arg type
            if type(ner_results) is not list :
                raise TypeError("NER Result Should Be A 2D List.")

            # get classification result of each sentence in sentences list
            classifications = []
            for sentence_ner_result in ner_results :
                classifications.append(HanlpApi.classify_common_words(sentence_ner_result))

            result = classifications

        except TypeError as e :
            BotLogger.exception(e.__str__())

        except Exception as e :
            BotLogger.exception(f"{type(e).__name__} : {e}")

        finally :
            return result


    @staticmethod
    def extract_keywords( ws_result: list, pos_result: list ) -> list or None :
        """
        檢查某「一」個句子的 WS 結果（tokens）
        並依據對應 token 的 POS 結果找出該句中的「關鍵詞」

        Exceptions :
            - TypeError : Wrong Param Type
            - Index Error : ws_results, pos_results Should Be Both 2D List And Have Same Size
            - Other Errors : See Log

        :param ws_result: 「某一」句子的 WS 結果（tokens）
        :param pos_result: 「某一」句子的 POS 結果（pos type of tokens）
        :return: 各個句子的結果組成的 list，發生錯誤時則回傳 None
        """

        result = None
        try :
            # check input arg type
            if not (type(ws_result) == type(pos_result) == list) :
                raise TypeError("ws_result, pos_result Should Be Both 2D List.")

            # check each tokens in ws_result
            keywords = []
            for i, token in enumerate(ws_result) :
                # check pos type of this token
                if pos_result[i] in ["NN", "NR"] :
                    keywords.append(token)

            result = keywords
            BotLogger.debug(f"Extract Keywords : {result}")

        except TypeError as e :
            BotLogger.exception(e.__str__())

        except IndexError as e :
            BotLogger.exception(f"{e}\nMaybe Your ws_results and pos_results Not Both 2D List Or Have Diff Size.")

        except Exception as e :
            BotLogger.exception(f"{type(e).__name__} = {e}")

        finally :
            return result


    @staticmethod
    def extract_keywords_of_sentences( ws_results: list, pos_results: list ) -> list or None :
        """
        與 extract_keywords 相似
        但是用來處理「數個句子構成的 list」
        會依序使用 ws_results[i] 以及 pos_result[i] 呼叫 extract_keywords
        並將「各句的結果（關鍵字 list）組合成 list」進行回傳

        Exceptions :
            - TypeError : Wrong Param Type, ws_results, pos_results Should Be Both 3D List
            - IndexError : ws_results, pos_results Should Have Same Size
            - Other Errors : See Log

        :param ws_results:「各個」句子的 POS 結果（pos type of tokens）
        :param pos_results: 「各個」句子的 POS 結果（pos type of tokens）
        :return: 由各句的「關鍵詞 list 組成的 list」，錯誤時則會回傳 None
        """

        result = None
        try :
            # check para, type
            if not (type(ws_results) == type(pos_results) == list) :
                raise TypeError("ws_results, pos_results Should Be Both 3D List.")

            # get keywords of each sentence base on their ws, ner result
            keywords_list = []
            for i, ws_result in enumerate(ws_results) :
                keywords_list.append(HanlpApi.extract_keywords(ws_result, pos_results[i]))

            result = keywords_list


        except TypeError as e :
            BotLogger.exception(e.__str__())

        except IndexError as e :
            BotLogger.exception(f"{e}\nMaybe Your ws_results And pos_results Have Diff Size.")

        except Exception as e :
            BotLogger.exception(f"{type(e).__name__} = {e}")

        finally :
            return result


if __name__ == '__main__' :
    HanlpApi.URL = BotConfig.HANLP_TEST_URL
    sentences = ["2018年4點10分中", "如果一個網站可以提供比較快速的台積電網路服務", "今天中國時報關於盧文祥的新聞"]

    ws_pos_ner_list = HanlpApi.parse_sentences(sentences, { })
    ws_pos_ner = HanlpApi.parse_sentence(sentences[1], { })

    keywords_list = HanlpApi.extract_keywords_of_sentences(ws_pos_ner_list["WS"], ws_pos_ner_list["POS"])
    keywords = HanlpApi.extract_keywords(ws_pos_ner["WS"], ws_pos_ner["POS"])

    classification_list = HanlpApi.classify_common_words_of_sentences(ws_pos_ner_list["NER"])
    classification = HanlpApi.classify_common_words(ws_pos_ner["NER"])

    print(ws_pos_ner_list)
    print(ws_pos_ner)