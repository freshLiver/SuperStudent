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
    def ffmpeg_convert( in_file_path: Path, out_file_path: Path, volume: int ) -> None :
        # run ffmpeg to convert audio format
        try :
            ffmpeg_log = "----------------------------------------------------------\n"
            ffmpeg_log += popen(f"ffmpeg -y -i {in_file_path} -filter:a \"volume={volume}\" {out_file_path} 2>&1").read()
            ffmpeg_log += "----------------------------------------------------------\n"

            BotLogger.debug(ffmpeg_log)

        except Exception as e :
            BotLogger.exception(f"{type(e).__name__} = {e}")


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
        output_path = Path(input_path + ".wav")

        # convert wav to m4a with ffmpeg
        AudioConvert.ffmpeg_convert(m4a_file_path, output_path, 1)

        # return full path of output audio file
        return Path(expanduser(output_path))


    @staticmethod
    def wav_to_m4a( wav_file_path: Path, volume = 1 ) -> Path :
        """
        convert a wav audio file into mpeg4 audio file (.m4a) with postfix .m4a
        and the output audio file will be saved at the audio_dir

        :param wav_file_path: input wav file path obj
        :param volume: FFmpeg's volume audio filter
        :return: output file path obj
        """

        # output m4a file will be saved at same dir with .m4a postfix
        input_path = wav_file_path.__str__()
        output_path = Path(input_path + ".m4a")

        # convert wav to m4a with ffmpeg
        AudioConvert.ffmpeg_convert(wav_file_path, output_path, volume)

        # return full path of output audio file
        return Path(expanduser(output_path))


if __name__ == '__main__' :

    m4a_input = Path(path.join(BotConfig.AUDIO_INPUT_TMP_DIR, "test.input"))
    wav_output = AudioConvert.m4a_to_wav(m4a_input)
    m4a_output = AudioConvert.wav_to_m4a(wav_output)