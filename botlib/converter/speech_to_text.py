import speech_recognition as recognizer
from botlib.botlogger import BotLogger



class SpeechToText :
    """
    Parse Audio File With 'wav' Format And Get Text Content
    """



    @staticmethod
    def chinese_to_cht( wav_audio_path: str ) -> str or None :
        """
        Convert Chinese Speech Audio With Wav Format To CHT Text

        :param wav_audio_path: Chinese Speech Audio
        :return: Result Text, None if LookupError
        """

        try :
            # extract audio data from the file
            with recognizer.WavFile(wav_audio_path) as file :
                audio = recognizer.Recognizer().record(file)

            # try to recognize speech using Google Speech Recognition
            text = recognizer.Recognizer().recognize_google(audio, language = 'zh-tw')
            BotLogger.log_info(f"Chinese Wav {wav_audio_path} To CHT Done.")

            # return speech audio content text
            return text

        # input file not found
        except FileNotFoundError :
            BotLogger.log_exception(f"STT Error, This File Not Found : {wav_audio_path}")
            return None

        # speech is unintelligible
        except LookupError :
            BotLogger.log_exception(f"STT LookupError, Unintelligible Wav File : {wav_audio_path}.")
            return None


if __name__ == '__main__' :
    from botlib import BotConfig



    wav_path = BotConfig.file_path_from(BotConfig.get_audio_input_dir(), "test.input1", postfix = ".wav")
    res = SpeechToText.chinese_to_cht(wav_path)

    if res is not None :
        print(res)
    else :
        print("ERROR")