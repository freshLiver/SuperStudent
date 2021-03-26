import gtts
from pathlib import Path

# project libs
from botlib import BotConfig



class TextToSpeech :
    """
    Convert Text of Specific Lang to Speech of Specific Lang and Save in '.wav' Format
    """



    @staticmethod
    def cht_to_taiwanese( chinese_text: str ) -> Path :
        #
        pass



    @staticmethod
    def cht_to_chinese( userid: str, cht_text: str ) -> Path :
        try :
            # Determine output audio path
            output_path = BotConfig.file_path_from(BotConfig.get_audio_output_dir(), userid, ".wav")

            # Convert Cht Text to Chinese Speech
            gtts.gTTS(cht_text, lang = 'zh').save(output_path.__str__())

            # return output file path
            return output_path

        except Exception as e :
            print(type(e).__name__, e)


if __name__ == '__main__' :
    res = TextToSpeech.cht_to_chinese("tts", "123456")
    print(res)