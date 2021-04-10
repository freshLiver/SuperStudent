import logging
from botlib import BotConfig



class BotLogger :
    # -------------------------------------------- class variables  --------------------------------------------

    if BotConfig.LOG_LEVEL.lower() == "info" :
        __LOGGER_MODE = logging.INFO
    elif BotConfig.LOG_LEVEL.lower() == "warning" :
        __LOGGER_MODE = logging.WARNING
    elif BotConfig.LOG_LEVEL.lower() == "error" :
        __LOGGER_MODE = logging.ERROR
    elif BotConfig.LOG_LEVEL.lower() == "critical" :
        __LOGGER_MODE = logging.CRITICAL
    else :
        __LOGGER_MODE = logging.DEBUG

    __LOGGER_FORMAT = "=== %(levelname)s \tLOG === \n%(message)s"

    logging.basicConfig(level = __LOGGER_MODE, format = __LOGGER_FORMAT)
    __LOGGER = logging.getLogger()


    # -------------------------------------------- class methods  --------------------------------------------
    @staticmethod
    def debug( msg: str ) :
        BotLogger.__LOGGER.debug(msg)


    @staticmethod
    def info( msg: str ) :
        BotLogger.__LOGGER.info(msg)


    @staticmethod
    def warning( msg: str ) :
        BotLogger.__LOGGER.warning(msg)


    @staticmethod
    def error( msg: str ) :
        BotLogger.__LOGGER.error(msg)


    @staticmethod
    def critical( msg: str ) :
        BotLogger.__LOGGER.critical(msg)


    @staticmethod
    def exception( msg: str ) :
        BotLogger.__LOGGER.exception(msg, exc_info = True)