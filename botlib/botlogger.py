import logging



class BotLogger :
    # -------------------------------------------- class variables  --------------------------------------------
    logging.basicConfig(level = logging.INFO, format = "%(message)s")
    __LOGGER = logging.getLogger()



    # -------------------------------------------- class methods  --------------------------------------------
    @staticmethod
    def log_debug( msg: str ) :
        BotLogger.__LOGGER.debug(f"==> DEBUG LOG: {msg}")



    @staticmethod
    def log_info( msg: str ) :
        BotLogger.__LOGGER.info(f"==> INFO LOG: {msg}")



    @staticmethod
    def log_warning( msg: str ) :
        BotLogger.__LOGGER.warning(f"==> WARNING LOG: {msg}")



    @staticmethod
    def log_error( msg: str ) :
        BotLogger.__LOGGER.error(f"==> ERROR LOG: {msg}")



    @staticmethod
    def log_critical( msg: str ) :
        BotLogger.__LOGGER.critical(f"==> CRITICAL LOG: {msg}")



    @staticmethod
    def log_exception( msg: str ) :
        BotLogger.__LOGGER.exception(f"==> EXCEPTION LOG: {msg}", exc_info = True)