import datetime

# project lib
from botlib.botlogger import BotLogger



def create_activity( people: list, events: list, time_range: (datetime, datetime), location: list ) -> str :
    # TODO call create activity function
    return "新增活動"


def find_activity( people: list, events: list, time_range: (datetime, datetime), location: list ) -> str :
    # TODO call find activity function

    BotLogger.debug(f"people : {people}")
    BotLogger.debug(f"events : {events}")
    BotLogger.debug(f"time_range : {time_range}")
    BotLogger.debug(f"location : {location}")

    return "查詢活動"