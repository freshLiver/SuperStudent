import logging


class Logger :
    # -------------------------------------------- class variables  --------------------------------------------
    logging.basicConfig(level = logging.DEBUG, format = "%(message)s")
    __LOGGER = logging.getLogger()
    
    
    # -------------------------------------------- class methods  --------------------------------------------
    @staticmethod
    def log_debug( msg: str ) :
        Logger.__LOGGER.debug(f"DEBUG LOG: {msg}")
    
    
    @staticmethod
    def log_info( msg: str ) :
        Logger.__LOGGER.info(f"INFO LOG: {msg}")
    
    
    @staticmethod
    def log_warning( msg: str ) :
        Logger.__LOGGER.warning(f"WARNING LOG: {msg}")
    
    
    @staticmethod
    def log_error( msg: str ) :
        Logger.__LOGGER.error(f"ERROR LOG: {msg}")
    
    
    @staticmethod
    def log_critical( msg: str ) :
        Logger.__LOGGER.critical(f"CRITICAL LOG: {msg}")
    
    
    @staticmethod
    def log_exception( msg: str ) :
        Logger.__LOGGER.exception(f"EXCEPTION LOG: {msg}", exc_info = True)