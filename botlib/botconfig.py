from os import path, system
from pathlib import Path

import env_file


class BotConfig :
    """
    Global Configs of This Line Bot Project
    """
    
    # BotConfig.py path obj
    __THIS_FILE = Path(__file__)
    
    # project root dir abs path
    __PROJECT_ROOT = path.abspath(__THIS_FILE.parent.parent)
    
    # abs path for saving audio messages received from user
    __AUDIO_MESSAGE_TMP_DIR = path.join(__PROJECT_ROOT, "audio_input_tmp")

    # try to create input audio message tmp dir
    system(f"mkdir {__AUDIO_MESSAGE_TMP_DIR}")

    # abs path of .env file
    __ENV_FILE_PATH = path.join(__PROJECT_ROOT, ".env")

    # load .env file of this project
    __ENV_FILE = env_file.get(__ENV_FILE_PATH)

    # LINE BOT Channel Token & Secret
    __LINE_CHANNEL_TOKEN = str(__ENV_FILE.get("line_channel_access_token"))
    __LINE_CHANNEL_SECRET = str(__ENV_FILE.get("line_channel_secret"))

    # flask port
    __PORT = int(7777)


    # --------------------------------------------------------------------------------------------------------

    @staticmethod
    def get_project_root() :
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