from __future__ import unicode_literals

import json
import hanlp

# project libs
from botlib import BotConfig
from botlib.api.lineapi import LineApi
from botlib.botlogger import BotLogger
from botlib.botresponse import BotResponse, BotResponseLanguage
from botlib.converter.audio_converter import AudioConvert
from botlib.converter.speech_to_text import SpeechToText
from botlib.services import match_service
from botlib.semantic_analyzer import SemanticAnalyzer

# flask libs
from flask import abort, Flask, jsonify, request, send_from_directory, make_response

# line bot apis
from linebot import LineBotApi, WebhookHandler, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, AudioMessage



# create global app instance
app = Flask(__name__)

line_bot_api = LineBotApi(channel_access_token = BotConfig.LINE_CHANNEL_TOKEN)
handler = WebhookHandler(channel_secret = BotConfig.LINE_CHANNEL_SECRET)
parser = WebhookParser(channel_secret = BotConfig.LINE_CHANNEL_SECRET)

BotLogger.info("Loading HanLP Module ....")
HanLP = hanlp.load(hanlp.pretrained.mtl.CLOSE_TOK_POS_NER_SRL_DEP_SDP_CON_ELECTRA_SMALL_ZH)
BotLogger.info("HanLP Module Loaded !")


# receive line message event
@app.route("/post_message", methods = ['POST'])
def callback() :
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text = True)
    BotLogger.info(f"Get Request Body done, \n=> {body}")

    # parse webhook body
    try :
        events = parser.parse(body, signature)

        # if event is MessageEvent and message is TextMessage
        for event in events :
            # should be message event
            if not isinstance(event, MessageEvent) :
                BotLogger.error("Not A MessageEvent, Ignored.")
                continue

            # check message type
            if isinstance(event.message, AudioMessage) :

                # get userid, reply_token, channel_token
                userid = event.source.user_id
                reply_token = event.reply_token
                channel_token = BotConfig.LINE_CHANNEL_TOKEN

                # save audio message as a file
                m4a_tmp_path = LineApi.save_audio_message_as_m4a(userid, event.message, line_bot_api)

                # convert m4a(raw audio message) to wav for stt
                wav_tmp_path = AudioConvert.m4a_to_wav(m4a_tmp_path)

                # do STT
                speech_text = SpeechToText.chinese_to_cht(wav_tmp_path)

                # stt error, send response audio message
                if speech_text is None :
                    response = BotResponse.make_inform_response("無法辨識內容，請再說一遍", BotResponseLanguage.CHINESE)
                    LineApi.send_response(userid, channel_token, reply_token, response)
                    BotLogger.info("Speech Text Is None.")
                    continue

                # parse user's speech content and get response
                else :
                    analyzer = SemanticAnalyzer(speech_text)
                    analyzer.parse_content()

                    # get response base on analyze result
                    response = match_service(analyzer = analyzer)

                    # send response (None for no response)
                    if response is not None :
                        LineApi.send_response(userid, channel_token, reply_token, response)


    # parse bot event failed
    except InvalidSignatureError as e :
        BotLogger.exception(f"InvalidSignatureError : {e}")
        abort(400)

    return "OK"


@app.route("/audio/<path:filename>")
def audio( filename ) :
    try :
        BotLogger.info(f"Audio Request : audio/{filename}")
        return send_from_directory(BotConfig.AUDIO_OUTPUT_TMP_DIR, filename)

    except Exception as e :
        BotLogger.exception(f"Getting Audio File Error : {type(e).__name__} \n{e}")
        return None


@app.route("/HANLP", methods = ["POST"])
def nlp() :
    # TODO : ADD LOG FOR THIS
    try :
        # get json content from post request
        try :
            post_data = json.loads(request.get_json())
        except TypeError :
            # curl POST will be here
            post_data = request.get_json()

        # try to extract useful data from dict
        sentence_list = post_data["sentences"]
        if type(sentence_list) is not list :
            raise TypeError

        custom_dict = post_data["custom_dict"]
        if type(custom_dict) is not dict :
            raise TypeError

        # set custom dict (low priority, combine tokens after ws)
        HanLP['tok/fine'].dict_combine = custom_dict

        # tokenize sentences base on custom_dict
        ws_result = HanLP(sentence_list)['tok/fine']

        # do pos and ner base on tokens
        pn_result = HanLP(ws_result, tasks = ['pos', 'ner'], skip_tasks = 'tok*')

        # return ws, pos, ner result as json(dict)
        result = {
            "WS" : ws_result,
            "POS" : pn_result['pos/ctb'],
            "NER" : pn_result['ner/msra']
        }

        return jsonify(result)

    except TypeError :
        error_msg = { "Type Error" : "Wrong Value of Key, Value Should Be : \"sentences\":list, \"custom_dict\":dict " }
        return jsonify(error_msg)

    except KeyError :
        error_msg = { "Key Error" : "POST Dict Should Contain 2 Keys : \"sentences\" and \"custom_dict\"" }
        return jsonify(error_msg)


@app.route("/", methods = ["GET"])
def home() :
    res = make_response("Home Route Of My Line Bot.")
    res.mimetype = "text/plain"
    return res


if __name__ == "__main__" :
    app.run(port = BotConfig.PORT, debug = True)