from __future__ import unicode_literals

# project libs
from botlib import BotConfig
from botlib.botlogger import BotLogger
from botlib.api.lineapi import LineApi
from botlib.converter.audio_converter import AudioConvert
from botlib.converter.speech_to_text import SpeechToText

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
    BotLogger.log_debug(f"Get Request Body done, \n=> {body}")

    # parse webhook body
    try :
        events = parser.parse(body, signature)

        # if event is MessageEvent and message is TextMessage
        for event in events :
            # should be message event
            if not isinstance(event, MessageEvent) :
                BotLogger.log_error("Not A MessageEvent, Ignored.")
                continue

            # check message type
            if isinstance(event.message, AudioMessage) :

                # get userid
                userid = event.source.user_id
                reply_token = event.reply_token

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
                    LineApi.send_audio_by_text(BotConfig.get_channel_token(), reply_token, userid, response_text)
                    continue

                # TODO parse text and get response
                if speech_text is not None :
                    # TEST reply stt content with tts
                    LineApi.send_audio_by_text(BotConfig.get_channel_token(), reply_token, userid, speech_text)

                # do response tts
                # response_wav_path = Path("")

                # convert wav to m4a
                # response_m4a_path = AudioConvert.wav_to_m4a(response_wav_path)

                # send back same audio message
                # LineApi.send_audio(BotConfig.get_channel_token(), event.reply_token, m4a_tmp_path)

    # parse bot event failed
    except InvalidSignatureError as e :
        BotLogger.log_exception(f"InvalidSignatureError : {e}")
        abort(400)

    return "OK"


@app.route("/audio/<path:filename>")
def audio( filename ) :
    try :
        BotLogger.log_info(f"Audio Request : audio/{filename}")
        return send_from_directory(BotConfig.get_audio_output_dir(), filename)

    except Exception as e :
        BotLogger.log_exception(f"Getting Audio File Error : {type(e).__name__} \n{e}")
        return None


if __name__ == "__main__" :
    app.run(port = BotConfig.get_flask_app_port(), debug = True)