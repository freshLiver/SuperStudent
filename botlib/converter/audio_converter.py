from os import path, popen

from botlib import BotConfig
from botlib.botlogger import BotLogger



class AudioConvert :
    """
    Convert Audio File From A Specific Format To Another Format
    """



    @staticmethod
    def m4a_to_wav( audio_dir: str, m4a_file: str ) -> str :
        """
        convert a mpeg4 audio (.m4a) into wav audio file with postfix .wav
        and the output audio file will be saved at the audio_dir

        :param audio_dir: input m4a file dir path
        :param m4a_file: input m4a filename (with output parent dir)
        :return: output file full path
        """

        # output m4a file will be saved at same dir with .m4a postfix
        input_path = path.join(audio_dir, m4a_file)
        output_path = path.join(audio_dir, m4a_file + ".wav")

        # run ffmpeg to convert audio format
        cmd_output = "----------------------------------------------------------"
        cmd_output += popen(f"ffmpeg -y -i {input_path} {output_path} 2>&1").read()
        cmd_output += "----------------------------------------------------------"

        BotLogger.log_debug(cmd_output)

        # return full path of output audio file
        return output_path



    @staticmethod
    def wav_to_m4a( audio_dir: str, wav_file: str ) -> str :
        """
        convert a wav audio file into mpeg4 audio file (.m4a) with postfix .m4a
        and the output audio file will be saved at the audio_dir

        :param audio_dir: input wav file dir path
        :param wav_file: input wav filename (with output parent dir)
        :return: output file full path
        """

        # output m4a file will be saved at same dir with .m4a postfix
        input_path = path.join(audio_dir, wav_file)
        output_path = path.join(audio_dir, wav_file + ".m4a")

        # run ffmpeg to convert audio format
        cmd_output = "----------------------------------------------------------"
        cmd_output += popen(f"ffmpeg -y -i {input_path} {output_path} 2>&1").read()
        cmd_output += "----------------------------------------------------------"

        BotLogger.log_debug(cmd_output)

        # return full path of output audio file
        return output_path


if __name__ == '__main__' :
    wav_output = AudioConvert.m4a_to_wav(BotConfig.get_audio_input_dir(), "test.input")
    m4a_output = AudioConvert.wav_to_m4a(BotConfig.get_audio_input_dir(), "test.input.wav")