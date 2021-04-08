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

    start_datetime = time_range[0].strftime("%Y/%m/%d %H:%M")
    end_datetime = time_range[1].strftime("%Y/%m/%d %H:%M")

    cmd = f"""INSERT OR IGNORE INTO activities VALUES("{content}","{start_datetime}","{end_datetime}")"""
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

    # open db
    this_dir = Path(__file__).parent
    db = sqlite3.connect(Path.joinpath(this_dir, "test.db"))
    cursor = db.cursor()

    # select all data that that match keywords from db
    keywords = proper_nouns + events + location
    conditions = f"""content LIKE "%{keywords[0]}%" """
    for kw in keywords[1 :] :
        conditions += f""" AND content LIKE "%{kw}%" """

    search_cmd = f"""SELECT * from activities WHERE {conditions}"""

    cursor.execute(search_cmd)
    results = cursor.fetchall()

    response = "找不到活動"
    for res in results :
        try :
            # get time range of this row
            start_datetime = datetime.datetime.strptime(res[1], "%Y/%m/%d %H:%M")
            end_datetime = datetime.datetime.strptime(res[2], "%Y/%m/%d %H:%M")

            # check time range
            if end_datetime < time_range[0] or start_datetime > time_range[1] :
                continue

            # use first match activity as response
            else :
                response = res[0]
                break

        except TypeError :
            BotLogger.exception(f"DB TIME RANGE TYPE ERROR : {res}, pass this data.")

        except Exception as e :
            BotLogger.exception(f"Search Activity Error, {type(e).__name__} => {e}")

    return response