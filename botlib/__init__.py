import configparser
from os import system
from os.path import expanduser, join
from pathlib import Path



class BotConfig :
    """
    Global Configs of This Line Bot Project
    """

    # BotConfig.py path obj
    __THIS_FILE = Path(__file__)

    # project root dir abs path
    PROJECT_ROOT = expanduser(__THIS_FILE.parent.parent)

    # abs path for saving audio messages received from user
    AUDIO_INPUT_TMP_DIR = join(PROJECT_ROOT, "audio_input_tmp")
    AUDIO_OUTPUT_TMP_DIR = join(PROJECT_ROOT, "audio_output_tmp")

    # try to create input audio message tmp dir
    system(f"mkdir {AUDIO_INPUT_TMP_DIR}")
    system(f"mkdir {AUDIO_OUTPUT_TMP_DIR}")

    # abs path of config.ini file
    __CONFIG_FILE = configparser.ConfigParser()
    __CONFIG_FILE.read(join(PROJECT_ROOT, "config.ini"))

    # LINE BOT Channel Token & Secret
    LINE_CHANNEL_TOKEN = str(__CONFIG_FILE["LINEBOT"]["line_channel_access_token"])
    LINE_CHANNEL_SECRET = str(__CONFIG_FILE["LINEBOT"]["line_channel_secret"])

    # flask port
    PORT = int(__CONFIG_FILE["GENERAL"]["port"])
    HANLP_URL = "http://140.116.245.157:7778/HANLP"
    HANLP_TEST_URL = "http://140.116.245.157:7778/HANLP"

    # log level
    LOG_LEVEL = "info"

    # lab api tokens
    LAB_NER_TOKEN = str(__CONFIG_FILE["LABAPI"]["lab_ner_token"])
    LAB_C2T_TOKEN = str(__CONFIG_FILE["LABAPI"]["lab_c2t_token"])

    # lab api hosts and ports
    LAB_NER_HOST_PORT = ("140.116.245.151", 9921)
    LAB_C2T_HOST_PORT = ("140.116.245.147", 50010)


    # -------------------------------------------------------------------------------------------------------

    @staticmethod
    def file_path_from( target_dir: str, filename: str, postfix = ".input" ) -> Path :
        """
        get full file path from target dir

        :param target_dir: full path of target dir
        :param filename: filename (without parent dir name and postfix)
        :param postfix: filename postfix
        :return: Path obj of this file
        """

        # get file path
        file_path = join(target_dir, f"{filename}{postfix}")

        # return Path obj
        return Path(expanduser(file_path))