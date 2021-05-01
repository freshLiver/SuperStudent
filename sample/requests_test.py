import json
from sys import path
from requests import post



path.append("..")

# proj libs
from botlib.api.hanlpapi import HanlpAPI



if __name__ == '__main__' :

    sentences = ["這是第一句測試句", "所以這就是第二句"]
    custom_dict = ["測試句"]

    result = HanlpAPI.parse_sentences(sentences, custom_dict)

    print(result)