import speech_recognition as recognizer
from pathlib import Path

# project lib
from botlib.botlogger import BotLogger
from botlib.api.labapi import LabApi
from botlib.api.hanlpapi import HanlpApi



class SpeechToText :
    """
    Parse Audio File With 'wav' Format And Get Text Content
    """


    @staticmethod
    def duo_lang_to_cht( wav_audio_path: Path ) -> str or None :

        c2c_result = SpeechToText.chinese_to_cht(wav_audio_path)
        t2c_result = SpeechToText.taiwanese_to_cht(wav_audio_path)

        # compare 2 result
        c2c_ws_pos_ner = HanlpApi.parse_sentence(c2c_result)
        t2c_ws_pos_ner = HanlpApi.parse_sentence(t2c_result)

        if len(c2c_ws_pos_ner["WS"]) <= len(t2c_ws_pos_ner["WS"]) :
            BotLogger.info("DuoLangResult : C2C")
            return c2c_result
        else :
            BotLogger.info("DuoLangResult : T2C")
            return t2c_result


    @staticmethod
    def chinese_to_cht( wav_audio_path: Path ) -> str or None :
        """
        Convert Chinese Speech Audio With Wav Format To CHT Text

        :param wav_audio_path: Chinese Speech Audio File Path Obj
        :return: Result Text, None if LookupError
        """

        try :
            # extract audio data from the file
            with recognizer.WavFile(wav_audio_path.__str__()) as file :
                audio = recognizer.Recognizer().record(file)

            # try to recognize speech using Google Speech Recognition
            text = recognizer.Recognizer().recognize_google(audio, language = 'zh-tw')

            # return speech audio content text
            BotLogger.debug(f"Chinese Wav {wav_audio_path.__str__()} To CHT Done.")
            return text

        # input file not found
        except FileNotFoundError :
            BotLogger.exception(f"STT Error, This File Not Found : {wav_audio_path.__str__()}")
            return None

        # speech is unintelligible
        except LookupError :
            BotLogger.exception(f"STT LookupError, Unintelligible Wav File : {wav_audio_path}.")
            return None


    @staticmethod
    def taiwanese_to_cht( wav_16khz_audio_path: Path ) -> str or None :

        tai_text = LabApi.lab_tstt_api(wav_16khz_audio_path)
        cht_text = LabApi.lab_t2c_api(tai_text)

        return cht_text


if __name__ == '__main__' :
    from botlib import BotConfig



    wav_path = BotConfig.file_path_from(BotConfig.AUDIO_INPUT_TMP_DIR, "test.input", postfix = ".wav")
    res = SpeechToText.chinese_to_cht(wav_path)

    if res is not None :
        print(res)
    else :
        print("ERROR")