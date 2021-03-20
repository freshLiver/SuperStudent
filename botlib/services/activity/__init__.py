import datetime

# project lib
from botlib.botlogger import BotLogger



def create_activity( people: list, events: list, time_range: (datetime, datetime), location: list ) -> str :
    return "Create Activity()"


def find_activity( people: list, events: list, time_range: (datetime, datetime), location: list ) -> str :
    BotLogger.log_debug(f"people : {people}")
    BotLogger.log_debug(f"events : {events}")
    BotLogger.log_debug(f"time_range : {time_range}")
    BotLogger.log_debug(f"location : {location}")

    return "Find Activity()"