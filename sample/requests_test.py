import json
from requests import post

# proj libs
from botlib import BotConfig



if __name__ == '__main__' :
    data = { "sentences" : "這是測試句子", "custom_dict" : { } }
    json_data = json.dumps(data)
    res = post(BotConfig.HANLP_URL, json = json_data)

    try :
        result = json.loads(res.text)
    except Exception as e :
        result = res.text

    print(result)