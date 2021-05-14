import datetime
import sqlite3

from pathlib import Path

# project lib
from botlib.botlogger import BotLogger



def create_activity( content: str, time_range: (datetime, datetime) ) -> str :
    """

    :param content:
    :param time_range:
    :return:
    """

    response = "新增活動成功"
    try :
        this_dir = Path(__file__).parent
        db = sqlite3.connect(Path.joinpath(this_dir, "test.db").__str__())
        cursor = db.cursor()

        start_datetime = time_range[0].strftime("%Y/%m/%d %H:%M")
        end_datetime = time_range[1].strftime("%Y/%m/%d %H:%M")
        start_datetime_value = time_range[0].strftime("%Y%m%d%H%M")
        end_datetime_value = time_range[1].strftime("%Y%m%d%H%M")

        cmd = f"""
            INSERT OR IGNORE INTO activities 
            VALUES ("{content}",
                    "{start_datetime_value}","{end_datetime_value}",
                    "{start_datetime}","{end_datetime}")"""

        # commit change
        cursor.execute(cmd)
        db.commit()
        db.close()

    except Exception as e :
        response = "新增活動失敗，請再次一次"
        BotLogger.exception(f"Exception {type(e).__name__} = {e}")

    finally :
        BotLogger.debug(f"""Create Activity : 
                Content = {content.__str__()}
                Time Range = {time_range.__str__()}
                Status = {response}""")

    return response


def search_activity( time_range: (datetime, datetime), keywords: list ) -> str or None :
    """

    :param keywords:
    :param time_range:
    :return:
    """

    response = None
    try :
        # open db
        this_dir = Path(__file__).parent
        db = sqlite3.connect(Path.joinpath(this_dir, "test.db").__str__())
        cursor = db.cursor()

        # select all data that that match keywords from db
        start_datetime_value = time_range[0].strftime("%Y%m%d%H%M")
        end_datetime_value = time_range[1].strftime("%Y%m%d%H%M")

        search_cmd = f"""
            SELECT content from activities WHERE 
                {start_datetime_value} <= end_datetime_value 
            AND 
                {end_datetime_value} >= start_datetime_value 
        """

        # should also match keywords
        for kw in keywords :
            search_cmd += f""" AND content LIKE "%{kw}%" """

        cursor.execute(search_cmd)

        result = cursor.fetchall()
        if result != [] and result is not None :
            # only fetch first column of first fetch
            response = result[0][0]

    except Exception as e :
        BotLogger.exception(f"Search Activity Error, {type(e).__name__} => {e}")

    return response