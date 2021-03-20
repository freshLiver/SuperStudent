from __future__ import unicode_literals

# project libs
from botlib import BotConfig
from botlib.api.lineapi import LineApi
from botlib.botlogger import BotLogger
from botlib.converter.audio_converter import AudioConvert
from botlib.converter.speech_to_text import SpeechToText
from botlib.services import service_matching
from botlib.semantic_analyzer import SemanticAnalyzer

# flask libs
from flask import abort, Flask, request, send_from_directory

# line bot apis
from linebot import LineBotApi, WebhookHandler, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, AudioMessage



# create global app instance
app = Flask(__name__)

line_bot_api = LineBotApi(channel_access_token = BotConfig.get_channel_token())
handler = WebhookHandler(channel_secret = BotConfig.get_channel_secret())
parser = WebhookParser(channel_secret = BotConfig.get_channel_secret())


# receive line message event
@app.route("/post_message", methods = ['POST'])
def callback() :
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text = True)
    BotLogger.debug(f"Get Request Body done, \n=> {body}")

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
                channel_token = BotConfig.get_channel_token()

                # save audio message as a file
                m4a_tmp_path = LineApi.save_audio_message_as_m4a(userid, event.message, line_bot_api)

                # convert tmp m4a to wav for stt
                wav_tmp_path = AudioConvert.m4a_to_wav(m4a_tmp_path)

                # do STT
                speech_text = SpeechToText.chinese_to_cht(wav_tmp_path)

                # default error response
                response_text = "無法辨識內容，請再說一遍"

                # stt error, send response audio message
                if speech_text is None :
                    LineApi.make_audio_message_and_send(channel_token, reply_token, userid, response_text)
                    BotLogger.info("Speech Text Is None.")
                    continue

                # parse user's speech content and get response
                else :
                    analyzer = SemanticAnalyzer(speech_text)
                    analyzer.parse_content()

                    # get response base on analyze result
                    response_text = service_matching(analyzer = analyzer)

                # send response (None for no response)
                if response_text is not None :
                    LineApi.make_audio_message_and_send(channel_token, reply_token, userid, response_text)

    # parse bot event failed
    except InvalidSignatureError as e :
        BotLogger.exception(f"InvalidSignatureError : {e}")
        abort(400)

    return "OK"


@app.route("/audio/<path:filename>")
def audio( filename ) :
    try :
        BotLogger.info(f"Audio Request : audio/{filename}")
        return send_from_directory(BotConfig.get_audio_output_dir(), filename)

    except Exception as e :
        BotLogger.exception(f"Getting Audio File Error : {type(e).__name__} \n{e}")
        return None


if __name__ == "__main__" :
    app.run(port = BotConfig.get_flask_app_port(), debug = True)