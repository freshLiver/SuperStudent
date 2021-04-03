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
    __ABSOLUTE_DATE_FMT = "%Y年%m月%d日"
    __ABSOLUTE_DATETIME_FMT = f"{__ABSOLUTE_DATE_FMT}%H點%M分"

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
    def parse_common_date_words( cht_sentence: str ) -> str :

        now = datetime.datetime.now()
        date_fmt = DatetimeConverter.__ABSOLUTE_DATE_FMT

        # year
        year_rule = re.compile("[今明後]年")
        year_matches = year_rule.finditer(cht_sentence)
        for match in year_matches :
            year_text = match.group()
            year_shift = 0
            if "明" in year_text :
                year_shift = 1
            elif "後" in year_text :
                year_shift = 2
            year_text = str((now + relativedelta(years = year_shift)).year)
            cht_sentence = cht_sentence.replace(match.group(), f"{year_text}年")

        # month
        month_rule = re.compile("(這|下+)個?月")
        month_matches = month_rule.finditer(cht_sentence)
        for match in month_matches :
            month_text = match.group()
            month_shift = 0
            if "下" in month_text :
                for char in month_text :
                    month_shift += 1 if char == "下" else 0
            month_text = str((now + relativedelta(months = month_shift)).month)
            cht_sentence = cht_sentence.replace(match.group(), f"{month_text}月")

        # week
        week_rule = re.compile("(這|下+)個?(禮拜|星期|周|週)")
        week_matches = week_rule.finditer(cht_sentence)
        for match in week_matches :
            week_text = match.group()
            week_shift = 0
            if "下" in week_text :
                for char in week_text :
                    week_shift += 1 if char == "下" else 0

            # get start and end day of target week
            start_date = now + relativedelta(weeks = week_shift, days = -1 * now.weekday())
            end_date = start_date + relativedelta(days = 6)

            # replace origin match text by "start 到 end"
            week_text = f"{start_date.strftime(date_fmt)} 到 {end_date.strftime(date_fmt)}"
            cht_sentence = cht_sentence.replace(match.group(), week_text)

        # day
        day_rule = re.compile("[今明後][天日]")
        day_matches = day_rule.finditer(cht_sentence)
        for match in day_matches :
            day_text = match.group()
            day_shift = 0
            if "明" in day_text :
                day_shift = 1
            elif "後" in day_text :
                day_shift = 2
            day_text = str((now + relativedelta(days = day_shift)).strftime(date_fmt))
            cht_sentence = cht_sentence.replace(match.group(), f"{day_text}")

        # TODO : 周X、週末、月底、月初

        return cht_sentence


    @staticmethod
    def simplify_cht_numeral_representations( cht_number_sentence: str ) -> str :
        """
        simplify cht numbers in raw_sentence for easier parsing

        for example :
        1. 二十 -> 二零
        2. 十二 -> 一二
        3. 二十三 -> 二三

        :param cht_number_sentence: target text that will be simplify
        :return: simplified cht_number_sentence
        """

        match = re.search("[一二三四五六七八九]十[一二三四五六七八九]?", cht_number_sentence)
        if match is not None :
            text = match.group()
            if text[-1] == "十" :
                value = text.replace("十", "零")
            else :
                value = text.replace("十", "")

            cht_number_sentence = cht_number_sentence.replace(text, value)

        match = re.search("十[一二三四五六七八九]", cht_number_sentence)
        if match is not None :
            value = match.group().replace("十", "一")
            cht_number_sentence = cht_number_sentence.replace(match.group(), value)

        return cht_number_sentence


    @staticmethod
    def cht_to_arabic_numerals( simplified_cht_sentence: str ) -> str :
        """
        replace all cht number in text with corresponding arabic numerals

        :param simplified_cht_sentence: simplified text with cht numbers
        :return: result text
        """
        for char in DatetimeConverter.__NUMBER_CONVERT_DICT :
            simplified_cht_sentence = simplified_cht_sentence.replace(char, DatetimeConverter.__NUMBER_CONVERT_DICT[char])
        return simplified_cht_sentence


    @staticmethod
    def get_absolute_datetime( relative_arabic_datetime: str ) -> str :
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
    def parse_datetime( cht_sentence: str ) -> str :
        """
        Convert *un-simplified CHT datetime text* into datetime text with arabic numeral value   

        :param cht_sentence: any cht sentence 
        :return: datetime text with arabic numeral value
        """

        # convert "今天", "明天" and similar datetime words to abs time
        cht_sentence = DatetimeConverter.parse_common_date_words(cht_sentence)

        # extract cht datetime part
        match_iter = DatetimeConverter.__CHT_DATETIME_RULE.finditer(cht_sentence)
        non_empty_matches = { }
        for matches in match_iter :
            match_text = matches.group()
            if match_text != '' :
                non_empty_matches[match_text] = ""

        # if no match cht datetime sentence, return origin sentence
        if non_empty_matches == { } :
            return cht_sentence

        # simplify cht datetime parts and convert to datetime with arabic numeral value
        for match in non_empty_matches :
            tmp = DatetimeConverter.simplify_cht_numeral_representations(match)
            tmp = DatetimeConverter.cht_to_arabic_numerals(tmp)
            non_empty_matches[match] = tmp.replace("又", "").replace("個", "")

        # convert datetime description to abs datetime
        for match in (future_matches for future_matches in non_empty_matches if "後" in future_matches) :
            non_empty_matches[match] = DatetimeConverter.get_absolute_datetime(non_empty_matches[match])

        # replace origin datetime strings with new string
        result = cht_sentence
        for match in non_empty_matches :
            result = result.replace(match, f" {non_empty_matches[match]} ")

        return result


if __name__ == '__main__' :

    # print(res)
    # res = DatetimeConverter.abs_future_time(res)
    res = DatetimeConverter.parse_common_date_words("下禮拜有活動")
    print(res)