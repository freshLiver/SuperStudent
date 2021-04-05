import datetime
import sqlite3

from pathlib import Path

# project lib
from botlib.botlogger import BotLogger



def create_activity( content: str, time_range: (datetime, datetime) ) -> str :
    # TODO call create activity function

    this_dir = Path(__file__).parent
    db = sqlite3.connect(Path.joinpath(this_dir, "test.db"))
    cursor = db.cursor()

    cmd = f"""INSERT OR IGNORE INTO activities VALUES("{content}")"""
    cursor.execute(cmd)
    db.commit()
    db.close()

    return "新增活動"


def search_activity( proper_nouns: list, events: list, time_range: (datetime, datetime), location: list ) -> str :
    # TODO call find activity function

    BotLogger.debug(f"people : {proper_nouns}")
    BotLogger.debug(f"events : {events}")
    BotLogger.debug(f"time_range : {time_range}")
    BotLogger.debug(f"location : {location}")

    return "查詢活動"