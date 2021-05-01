import json
from requests import post

# project libs
from botlib import BotConfig
from botlib.botlogger import BotLogger



class HanlpAPI :
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