import env_file
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
    __PROJECT_ROOT = expanduser(__THIS_FILE.parent.parent)

    # abs path for saving audio messages received from user
    __AUDIO_INPUT_TMP = join(__PROJECT_ROOT, "audio_input_tmp")
    __AUDIO_OUTPUT_TMP = join(__PROJECT_ROOT, "audio_output_tmp")

    # try to create input audio message tmp dir
    system(f"mkdir {__AUDIO_INPUT_TMP}")
    system(f"mkdir {__AUDIO_OUTPUT_TMP}")

    # abs path of .env file
    __ENV_FILE_PATH = join(__PROJECT_ROOT, ".env")

    # load .env file of this project
    __ENV_FILE = env_file.get(__ENV_FILE_PATH)

    # LINE BOT Channel Token & Secret
    __LINE_CHANNEL_TOKEN = str(__ENV_FILE.get("line_channel_access_token"))
    __LINE_CHANNEL_SECRET = str(__ENV_FILE.get("line_channel_secret"))

    # flask port
    __PORT = int(7777)



    # --------------------------------------------------------------------------------------------------------

    @staticmethod
    def get_project_root() -> str :
        """
        get absolute path of the root dir of this project

        :return: absolute path of project root
        """
        return BotConfig.__PROJECT_ROOT



    @staticmethod
    def get_channel_token() -> str :
        """
        get channel token of my line bot

        :return: channel token string
        """
        return BotConfig.__LINE_CHANNEL_TOKEN



    @staticmethod
    def get_channel_secret() -> str :
        """
        get channel secret of my line bot

        :return: channel secret string
        """
        return BotConfig.__LINE_CHANNEL_SECRET



    @staticmethod
    def get_flask_app_port() -> int :
        """
        get port number of this flask app

        :return: port number
        """
        return BotConfig.__PORT



    # -------------------------------------------------------------------------------------------------------


    @staticmethod
    def get_audio_input_dir() -> str :
        """
        get full path of audio input tmp dir

        :return: audio input tmp dir path
        """
        return BotConfig.__AUDIO_INPUT_TMP



    @staticmethod
    def get_audio_output_dir() -> str :
        """
        get full path audio output tmp dir

        :return: audio output tmp dir path
        """
        return BotConfig.__AUDIO_OUTPUT_TMP



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


    # -------------------------------------------------------------------------------------------------------