from os import popen, path
from os.path import expanduser
from pathlib import Path

from botlib import BotConfig
from botlib.botlogger import BotLogger



class AudioConvert :
    """
    Convert Audio File From A Specific Format To Another Format
    """


    @staticmethod
    def m4a_to_wav( m4a_file_path: Path ) -> Path :
        """
        convert a mpeg4 audio (.m4a) into wav audio file with postfix .wav
        and the output audio file will be saved at the audio_dir

        :param m4a_file_path: input m4a file path obj
        :return: output file path obj
        """

        # output m4a file will be saved at same dir with .m4a postfix
        input_path = m4a_file_path.__str__()
        output_path = input_path + ".wav"

        # run ffmpeg to convert audio format
        try :
            cmd_output = "----------------------------------------------------------"
            cmd_output += popen(f"ffmpeg -y -i {input_path} {output_path} 2>&1").read()
            cmd_output += "----------------------------------------------------------"

            BotLogger.debug(cmd_output)

        except Exception as e :
            BotLogger.exception(f"{type(e).__name__} = {e}")

        # return full path of output audio file
        return Path(expanduser(output_path))


    @staticmethod
    def wav_to_m4a( wav_file_path: Path ) -> Path :
        """
        convert a wav audio file into mpeg4 audio file (.m4a) with postfix .m4a
        and the output audio file will be saved at the audio_dir

        :param wav_file_path: input wav file path obj
        :return: output file path obj
        """

        # output m4a file will be saved at same dir with .m4a postfix
        input_path = wav_file_path.__str__()
        output_path = input_path + ".m4a"

        try :
            # run ffmpeg to convert audio format
            cmd_output = "----------------------------------------------------------\n"
            cmd_output += popen(f"ffmpeg -y -i {input_path} {output_path} 2>&1").read()
            cmd_output += "----------------------------------------------------------\n"

            BotLogger.debug(cmd_output)

        except Exception as e :
            BotLogger.exception(f"{type(e).__name__} = {e}")

        # return full path of output audio file
        return Path(expanduser(output_path))


if __name__ == '__main__' :

    m4a_input = Path(path.join(BotConfig.get_audio_input_dir(), "test.input"))
    wav_output = AudioConvert.m4a_to_wav(m4a_input)
    m4a_output = AudioConvert.wav_to_m4a(wav_output)