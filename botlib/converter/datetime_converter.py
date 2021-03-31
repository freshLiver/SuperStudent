import re
import datetime
from dateutil.relativedelta import relativedelta



class DatetimeConverter :
    """
    Convert Datetime String Value from CHT To Arabic Numeral
    """

    __NUMBER_CONVERT_DICT = {
        "零" : "0", "一" : "1", "二" : "2", "兩" : "2", "三" : "3", "四" : "4",
        "五" : "5", "六" : "6", "七" : "7", "八" : "8", "九" : "9", "十" : "10",
    }

    __YEAR_UNIT_LIST = ["年"]
    __MONTH_UNIT_LIST = ["月"]
    __WEEK_UNIT_LIST = ["週", "周", "星期", "禮拜"]
    __DATE_UNIT_LIST = ["日", "天", "號"]
    __HOUR_UNIT_LIST = ["時", "小時", "鐘頭", "點"]
    __MINUTE_UNIT_LIST = ["分", "分鐘"]

    __YEAR_UNIT_FMT = "年"
    __MONTH_UNIT_FMT = "月"
    __WEEK_UNIT_FMT = "(週|周|星期|禮拜)"
    __DATE_UNIT_FMT = "(日|天|號)"
    __HOUR_UNIT_FMT = "(小?時|鐘頭|點)"
    __MINUTE_UNIT_FMT = "分鐘?"

    __CHT_NUMBERS = "[零一二兩三四五六七八九十]+"
    __CHT_DATETIME_FMT = f"({__CHT_NUMBERS}{__YEAR_UNIT_FMT})?又?"
    __CHT_DATETIME_FMT += f"({__CHT_NUMBERS}個?{__MONTH_UNIT_FMT})?又?"
    __CHT_DATETIME_FMT += f"({__CHT_NUMBERS}個?{__WEEK_UNIT_FMT})?又?"
    __CHT_DATETIME_FMT += f"({__CHT_NUMBERS}{__DATE_UNIT_FMT})?又?"
    __CHT_DATETIME_FMT += f"({__CHT_NUMBERS}個?{__HOUR_UNIT_FMT})?又?"
    __CHT_DATETIME_FMT += f"({__CHT_NUMBERS}{__MINUTE_UNIT_FMT})?(之?後)?"

    __CHT_DATETIME_RULE = re.compile(__CHT_DATETIME_FMT)

    __ARABIC_NUMBER_RULE = re.compile("\d+")
    __ABSOLUTE_DATETIME_FMT = "%Y年%m月%d日%H點%M分"

    __ARABIC_YEAR_RULE = re.compile(f"\d+{__YEAR_UNIT_FMT}")
    __ARABIC_MONTH_RULE = re.compile(f"\d+{__MONTH_UNIT_FMT}")
    __ARABIC_WEEK_RULE = re.compile(f"\d+{__WEEK_UNIT_FMT}")
    __ARABIC_DATE_RULE = re.compile(f"\d+{__DATE_UNIT_FMT}")
    __ARABIC_HOUR_RULE = re.compile(f"\d+{__HOUR_UNIT_FMT}")
    __ARABIC_MINUTE_RULE = re.compile(f"\d+{__MINUTE_UNIT_FMT}")

    __ARABIC_DATETIME_FMT = f"(\d+{__YEAR_UNIT_FMT})?"
    __ARABIC_DATETIME_FMT += f"(\d+{__MONTH_UNIT_FMT})?"
    __ARABIC_DATETIME_FMT += f"(\d+{__WEEK_UNIT_FMT})?"
    __ARABIC_DATETIME_FMT += f"(\d+{__DATE_UNIT_FMT})?"
    __ARABIC_DATETIME_FMT += f"(\d+{__HOUR_UNIT_FMT})?"
    __ARABIC_DATETIME_FMT += f"(\d+{__MINUTE_UNIT_FMT})?"
    __ARABIC_DATETIME_FMT += f"之?後"

    __ARABIC_DATETIME_RULE = re.compile(__ARABIC_DATETIME_FMT)


    # ----------------------------------------------------------------------------------

    @staticmethod
    def to_simplified_cht_number( cht_number_text: str ) -> str :
        """
        simplify cht numbers in raw_sentence for easier parsing

        for example :
        1. 二十 -> 二零
        2. 十二 -> 一二
        3. 二十三 -> 二三

        :param cht_number_text: target text that will be simplify
        :return: simplified raw_text
        """

        match = re.search("[一二三四五六七八九]十[一二三四五六七八九]?", cht_number_text)
        if match is not None :
            text = match.group()
            if text[-1] == "十" :
                value = text.replace("十", "零")
            else :
                value = text.replace("十", "")

            cht_number_text = cht_number_text.replace(text, value)

        match = re.search("十[一二三四五六七八九]", cht_number_text)
        if match is not None :
            value = match.group().replace("十", "一")
            cht_number_text = cht_number_text.replace(match.group(), value)

        return cht_number_text


    @staticmethod
    def to_arabic_numerals( simplified_text: str ) -> str :
        """
        replace all cht number in text with corresponding arabic numerals

        :param simplified_text: simplified text with cht numbers
        :return: result text
        """
        for char in DatetimeConverter.__NUMBER_CONVERT_DICT :
            simplified_text = simplified_text.replace(char, DatetimeConverter.__NUMBER_CONVERT_DICT[char])
        return simplified_text


    @staticmethod
    def get_abs_future_datetime( relative_arabic_datetime: str ) -> str :
        """
        convert relative *future* datetime to absolute datetime base on current date and time
        
        :param relative_arabic_datetime: future datetime text with *arabic numeral* value
        :return: absolute datetime text with *arabic numeral* value
        """

        # get current time info
        now = datetime.datetime.now()

        # relative time fmt
        search_result = DatetimeConverter.__ARABIC_DATETIME_RULE.search(relative_arabic_datetime)

        # no match future text
        if search_result is None :
            return relative_arabic_datetime

        # convert to abs date
        else :
            delta_time = datetime.timedelta(0)
            relative_date = search_result.group()

            # have year
            if any(sub in relative_date for sub in DatetimeConverter.__YEAR_UNIT_LIST) :
                value_text = DatetimeConverter.__ARABIC_YEAR_RULE.search(relative_date).group()
                value = int(DatetimeConverter.__ARABIC_NUMBER_RULE.search(value_text).group())
                delta_time += relativedelta(years = value)
            # have month
            if any(sub in relative_date for sub in DatetimeConverter.__MONTH_UNIT_LIST) :
                value_text = DatetimeConverter.__ARABIC_MONTH_RULE.search(relative_date).group()
                value = int(DatetimeConverter.__ARABIC_NUMBER_RULE.search(value_text).group())
                delta_time += relativedelta(months = value)
            # have week
            if any(sub in relative_date for sub in DatetimeConverter.__WEEK_UNIT_LIST) :
                value_text = DatetimeConverter.__ARABIC_WEEK_RULE.search(relative_date).group()
                value = int(DatetimeConverter.__ARABIC_NUMBER_RULE.search(value_text).group())
                delta_time += relativedelta(weeks = value)
            # have day
            if any(sub in relative_date for sub in DatetimeConverter.__DATE_UNIT_LIST) :
                value_text = DatetimeConverter.__ARABIC_DATE_RULE.search(relative_date).group()
                value = int(DatetimeConverter.__ARABIC_NUMBER_RULE.search(value_text).group())
                delta_time += relativedelta(days = value)
            # have hour
            if any(sub in relative_date for sub in DatetimeConverter.__HOUR_UNIT_LIST) :
                value_text = DatetimeConverter.__ARABIC_HOUR_RULE.search(relative_date).group()
                value = int(DatetimeConverter.__ARABIC_NUMBER_RULE.search(value_text).group())
                delta_time += relativedelta(hours = value)
            # have minute
            if any(sub in relative_date for sub in DatetimeConverter.__MINUTE_UNIT_LIST) :
                value_text = DatetimeConverter.__ARABIC_MINUTE_RULE.search(relative_date).group()
                value = int(DatetimeConverter.__ARABIC_NUMBER_RULE.search(value_text).group())
                delta_time += relativedelta(minutes = value)

            # replace relative datetime with abs datetime
            final_datetime = now + delta_time

            return relative_arabic_datetime.replace(relative_date, final_datetime.strftime(DatetimeConverter.__ABSOLUTE_DATETIME_FMT))


    @staticmethod
    def get_abs_datetime_sentence( un_simplified_cht_datetime: str ) -> str :
        """
        Convert *un-simplified CHT datetime text* into datetime text with arabic numeral value   

        :param un_simplified_cht_datetime: *un-simplified* CHT datetime text
        :return: datetime text with arabic numeral value
        """

        # extract cht datetime part
        match_iter = DatetimeConverter.__CHT_DATETIME_RULE.finditer(un_simplified_cht_datetime)
        non_empty_matches = { }
        for matches in match_iter :
            match_text = matches.group()
            if match_text != '' :
                non_empty_matches[match_text] = ""

        # if no match, return origin sentence
        if non_empty_matches == { } :
            return un_simplified_cht_datetime

        # simplify cht datetime parts and convert to datetime with arabic numeral value
        for match in non_empty_matches :
            tmp = DatetimeConverter.to_simplified_cht_number(match)
            tmp = DatetimeConverter.to_arabic_numerals(tmp)
            non_empty_matches[match] = tmp.replace("又", "").replace("個", "")
        print(non_empty_matches)

        # convert future datetime to abs datetime
        for match in (future_matches for future_matches in non_empty_matches if "後" in future_matches) :
            non_empty_matches[match] = DatetimeConverter.get_abs_future_datetime(non_empty_matches[match])

        # replace origin datetime strings with new string
        result = un_simplified_cht_datetime
        for match in non_empty_matches :
            result = result.replace(match, f" {non_empty_matches[match]} ")

        return result


if __name__ == '__main__' :

    # print(res)
    # res = DatetimeConverter.abs_future_time(res)
    res = DatetimeConverter.get_abs_datetime_sentence("光復操場一年又二週又二十一小時之後有活動會在五點二十五分舉行")
    print(res)