import gtts
from pathlib import Path

# project libs
from botlib import BotConfig
from botlib.api.labapi import LabApi



class TextToSpeech :
    """
    Convert Text of Specific Lang to Speech of Specific Lang and Save in '.wav' Format
    """


    @staticmethod
    def cht_to_taiwanese( audio_name: str, cht_text: str ) -> Path :
        """

        :param audio_name:
        :param cht_text:
        :return:
        """

        return LabApi.lab_c2t_api(audio_name, cht_text)


    @staticmethod
    def cht_to_chinese( audio_name: str, cht_text: str ) -> Path :
        try :
            # Determine output audio path
            output_path = BotConfig.file_path_from(BotConfig.AUDIO_OUTPUT_TMP_DIR, audio_name, ".wav")

            # Convert Cht Text to Chinese Speech
            gtts.gTTS(cht_text, lang = 'zh').save(output_path.__str__())

            # return output file path
            return output_path

        except Exception as e :
            print(type(e).__name__, e)


if __name__ == '__main__' :
    res = TextToSpeech.cht_to_chinese("tts", "123456")
    print(res)