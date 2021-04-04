import re
import datetime
from dateutil.relativedelta import relativedelta

# project libs
from botlib.botlogger import BotLogger



class DatetimeConverter :
    """
    Convert Datetime String Value from CHT To Arabic Numeral
    """

    __NUMBER_CONVERT_DICT = {
        "零" : "0", "一" : "1", "二" : "2", "兩" : "2", "三" : "3", "四" : "4",
        "五" : "5", "六" : "6", "七" : "7", "八" : "8", "九" : "9", "十" : "10",
    }

    __YEAR___UNIT_LIST = ["年"]
    __MONTH__UNIT_LIST = ["月"]
    __WEEK___UNIT_LIST = ["週", "周", "星期", "禮拜"]
    __DATE___UNIT_LIST = ["日", "天", "號"]
    __HOUR___UNIT_LIST = ["時", "小時", "鐘頭", "點"]
    __MINUTE_UNIT_LIST = ["分", "分鐘"]

    __YEAR___UNIT_FMT = "年"
    __MONTH__UNIT_FMT = "月"
    __WEEK___UNIT_FMT = "(週|周|星期|禮拜)"
    __DATE___UNIT_FMT = "(日|天|號)"
    __HOUR___UNIT_FMT = "(小?時|鐘頭|點)"
    __MINUTE_UNIT_FMT = "分鐘?"

    __CHT_NUMBER_FMT = "[零一二兩三四五六七八九十]+"
    __CHT_DATETIME_FMT = f"({__CHT_NUMBER_FMT}個?{__YEAR___UNIT_FMT})?[的又]?"
    __CHT_DATETIME_FMT += f"({__CHT_NUMBER_FMT}個?{__MONTH__UNIT_FMT})?[的又]?"
    __CHT_DATETIME_FMT += f"({__CHT_NUMBER_FMT}個?{__WEEK___UNIT_FMT})?[的又]?"
    __CHT_DATETIME_FMT += f"({__CHT_NUMBER_FMT}個?{__DATE___UNIT_FMT})?[的又]?"
    __CHT_DATETIME_FMT += f"({__CHT_NUMBER_FMT}個?{__HOUR___UNIT_FMT})?[的又]?"
    __CHT_DATETIME_FMT += f"({__CHT_NUMBER_FMT}個?{__MINUTE_UNIT_FMT})?(之?後)?"
    __CHT_DATETIME_RULE = re.compile(__CHT_DATETIME_FMT)

    __ARABIC_NUMBER_FMT = "\d+"
    __ARABIC_NUMBER_RULE = re.compile(__ARABIC_NUMBER_FMT)
    __ARABIC_YEAR___RULE = re.compile(f"{__ARABIC_NUMBER_FMT}{__YEAR___UNIT_FMT}")
    __ARABIC_MONTH__RULE = re.compile(f"{__ARABIC_NUMBER_FMT}{__MONTH__UNIT_FMT}")
    __ARABIC_WEEK___RULE = re.compile(f"{__ARABIC_NUMBER_FMT}{__WEEK___UNIT_FMT}")
    __ARABIC_DATE___RULE = re.compile(f"{__ARABIC_NUMBER_FMT}{__DATE___UNIT_FMT}")
    __ARABIC_HOUR___RULE = re.compile(f"{__ARABIC_NUMBER_FMT}{__HOUR___UNIT_FMT}")
    __ARABIC_MINUTE_RULE = re.compile(f"{__ARABIC_NUMBER_FMT}{__MINUTE_UNIT_FMT}")

    __ARABIC_DATETIME_FMT = f"({__ARABIC_NUMBER_FMT}個?{__YEAR___UNIT_FMT})?[的又]?"
    __ARABIC_DATETIME_FMT += f"({__ARABIC_NUMBER_FMT}個?{__MONTH__UNIT_FMT})?[的又]?"
    __ARABIC_DATETIME_FMT += f"({__ARABIC_NUMBER_FMT}個?{__WEEK___UNIT_FMT})?[的又]?"
    __ARABIC_DATETIME_FMT += f"({__ARABIC_NUMBER_FMT}個?{__DATE___UNIT_FMT})?[的又]?"
    __ARABIC_DATETIME_FMT += f"({__ARABIC_NUMBER_FMT}個?{__HOUR___UNIT_FMT})?[的又]?"
    __ARABIC_DATETIME_FMT += f"({__ARABIC_NUMBER_FMT}個?{__MINUTE_UNIT_FMT})?"
    __ARABIC_DATETIME_RULE = re.compile(__ARABIC_DATETIME_FMT)

    __ARABIC_FUTURE_DATETIME_FMT = __ARABIC_DATETIME_FMT + f"之?後"
    __ARABIC_FUTURE_DATETIME_RULE = re.compile(__ARABIC_FUTURE_DATETIME_FMT)

    __ARABIC_DATETIME_RANGE_FMT = f"從?{__ARABIC_DATETIME_FMT}(到{__ARABIC_DATETIME_FMT})?"
    __ARABIC_DATETIME_RANGE_RULE = re.compile(__ARABIC_DATETIME_RANGE_FMT)

    __STD_DATE_FMT = "%Y年%m月%d日"
    __STD_DATETIME_FMT = f"{__STD_DATE_FMT}%H點%M分"


    # ----------------------------------------------------------------------------------

    @staticmethod
    def parse_common_date_words( any_cht_text: str ) -> str :

        now = datetime.datetime.now()
        date_fmt = DatetimeConverter.__STD_DATE_FMT

        # year
        year_rule = re.compile("[今明後]年")
        year_matches = year_rule.finditer(any_cht_text)
        for match in year_matches :
            year_text = match.group()
            year_shift = 0
            if "明" in year_text :
                year_shift = 1
            elif "後" in year_text :
                year_shift = 2
            year_text = str((now + relativedelta(years = year_shift)).year)
            any_cht_text = any_cht_text.replace(match.group(), f"{year_text}年")

        # month
        month_rule = re.compile("(這|下+)個?月")
        month_matches = month_rule.finditer(any_cht_text)
        for match in month_matches :
            month_text = match.group()
            month_shift = 0
            if "下" in month_text :
                for char in month_text :
                    month_shift += 1 if char == "下" else 0
            month_text = str((now + relativedelta(months = month_shift)).month)
            any_cht_text = any_cht_text.replace(match.group(), f"{month_text}月")

        # week
        week_rule = re.compile("(這|下+)個?(禮拜|星期|周|週)")
        week_matches = week_rule.finditer(any_cht_text)
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
            any_cht_text = any_cht_text.replace(match.group(), week_text)

        # day
        day_rule = re.compile("[今明後][天日]")
        day_matches = day_rule.finditer(any_cht_text)
        for match in day_matches :
            day_text = match.group()
            day_shift = 0
            if "明" in day_text :
                day_shift = 1
            elif "後" in day_text :
                day_shift = 2
            day_text = str((now + relativedelta(days = day_shift)).strftime(date_fmt))
            any_cht_text = any_cht_text.replace(match.group(), f"{day_text}")

        # TODO : 周X、週末、月底、月初

        return any_cht_text


    @staticmethod
    def simplify_cht_numeral_representations( cht_number_text: str ) -> str :
        """
        simplify cht numbers in raw_sentence for easier parsing

        for example :
        1. 二十 -> 二零
        2. 十二 -> 一二
        3. 二十三 -> 二三

        :param cht_number_text: target text that will be simplify
        :return: simplified cht_number_sentence
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
    def cht_to_arabic_numerals( simplified_cht_datetime_text: str ) -> str :
        """
        replace all cht number in text with corresponding arabic numerals

        :param simplified_cht_datetime_text: simplified text with cht numbers
        :return: result text
        """
        for char in DatetimeConverter.__NUMBER_CONVERT_DICT :
            simplified_cht_datetime_text = simplified_cht_datetime_text.replace(char, DatetimeConverter.__NUMBER_CONVERT_DICT[char])
        return simplified_cht_datetime_text


    @staticmethod
    def to_datetime( absolute_arabic_datetime_text: str, from_now = False ) -> datetime or None :
        """
        convert absolute datetime text with arabic numeral values to datetime instance

        :param absolute_arabic_datetime_text: absolute datetime text with arabic numeral values
        :param from_now: this datetime is delta_time from now
        :return: first match datetime instance, None if datetime not found in text
        """

        matches = DatetimeConverter.__ARABIC_DATETIME_RULE.search(absolute_arabic_datetime_text)

        # if no match text, return None
        if matches is None :
            return None

        match = matches.group()
        delta_time = datetime.timedelta(0)

        years = months = weeks = days = hours = minutes = -1

        # get year
        if any(sub in match for sub in DatetimeConverter.__YEAR___UNIT_LIST) :
            value_text = DatetimeConverter.__ARABIC_YEAR___RULE.search(match).group()
            years = int(DatetimeConverter.__ARABIC_NUMBER_RULE.search(value_text).group())
            delta_time += relativedelta(years = years)

        # get month
        if any(sub in match for sub in DatetimeConverter.__MONTH__UNIT_LIST) :
            value_text = DatetimeConverter.__ARABIC_MONTH__RULE.search(match).group()
            months = int(DatetimeConverter.__ARABIC_NUMBER_RULE.search(value_text).group())
            delta_time += relativedelta(months = months)

        # get week, NOTE : week only count for time delta
        if any(sub in match for sub in DatetimeConverter.__WEEK___UNIT_LIST) :
            value_text = DatetimeConverter.__ARABIC_WEEK___RULE.search(match).group()
            weeks = int(DatetimeConverter.__ARABIC_NUMBER_RULE.search(value_text).group())
            delta_time += relativedelta(weeks = weeks)

        # get day
        if any(sub in match for sub in DatetimeConverter.__DATE___UNIT_LIST) :
            value_text = DatetimeConverter.__ARABIC_DATE___RULE.search(match).group()
            days = int(DatetimeConverter.__ARABIC_NUMBER_RULE.search(value_text).group())
            delta_time += relativedelta(days = days)

        # get hour
        if any(sub in match for sub in DatetimeConverter.__HOUR___UNIT_LIST) :
            value_text = DatetimeConverter.__ARABIC_HOUR___RULE.search(match).group()
            hours = int(DatetimeConverter.__ARABIC_NUMBER_RULE.search(value_text).group())
            delta_time += relativedelta(hours = hours)

        # get minute
        if any(sub in match for sub in DatetimeConverter.__MINUTE_UNIT_LIST) :
            value_text = DatetimeConverter.__ARABIC_MINUTE_RULE.search(match).group()
            minutes = int(DatetimeConverter.__ARABIC_NUMBER_RULE.search(value_text).group())
            delta_time += relativedelta(minutes = minutes)

        now = datetime.datetime.now()
        if from_now is True :
            return now + delta_time
        else :
            predict = False
            if years != -1 :
                predict = True
            else :
                years = now.year if not predict else 0
            if months != -1 :
                predict = True
            else :
                months = now.month if not predict else 1
            if days != -1 :
                predict = True
            else :
                days = now.day if not predict else 1
            if hours != -1 :
                predict = True
            else :
                hours = now.hour if not predict else 0
            if minutes != -1 :
                predict = True
            else :
                minutes = now.minute if not predict else 0

            try :
                result = now.replace(years, months, days, hours, minutes, 0, 0)
                return result
            except ValueError as ve :
                BotLogger.exception(f"Illegal Datetime Value : {ve}")
                return None


    @staticmethod
    def get_std_future_datetime_text( relative_arabic_datetime_text: str ) -> str :
        """
        convert relative *future* datetime text to absolute datetime text base on current datetime
        
        :param relative_arabic_datetime_text: future datetime text with *arabic numeral* value
        :return: absolute datetime text with *arabic numeral* value
        """

        # relative time fmt
        search_result = DatetimeConverter.__ARABIC_FUTURE_DATETIME_RULE.search(relative_arabic_datetime_text)

        # no match future text
        if search_result is None :
            return relative_arabic_datetime_text

        # convert to abs date
        else :
            match_text = search_result.group()
            match_text_clean = match_text.replace("個", "").replace("又", "")

            # replace relative datetime with abs datetime
            final_datetime = DatetimeConverter.to_datetime(match_text_clean, from_now = True)

            return relative_arabic_datetime_text.replace(match_text, final_datetime.strftime(DatetimeConverter.__STD_DATETIME_FMT))


    @staticmethod
    def standardize_datetime( any_cht_sentence: str ) -> str :
        """
        Convert *un-simplified CHT datetime text* into datetime text with arabic numeral value   

        :param any_cht_sentence: any cht sentence 
        :return: datetime text with arabic numeral value
        """

        # convert "今天", "明天" and similar datetime words to abs time
        any_cht_sentence = DatetimeConverter.parse_common_date_words(any_cht_sentence)

        # extract cht datetime part
        match_iter = DatetimeConverter.__CHT_DATETIME_RULE.finditer(any_cht_sentence)
        non_empty_matches = { }
        for matches in match_iter :
            match_text = matches.group()
            if match_text != '' :
                non_empty_matches[match_text] = ""

        # if no match cht datetime sentence, return origin sentence
        if non_empty_matches == { } :
            return any_cht_sentence

        # simplify cht datetime parts and convert to datetime with arabic numeral value
        for match in non_empty_matches :
            tmp = DatetimeConverter.simplify_cht_numeral_representations(match)
            tmp = DatetimeConverter.cht_to_arabic_numerals(tmp)
            non_empty_matches[match] = tmp.replace("又", "").replace("個", "")

        # convert datetime description to abs datetime
        for match in (future_matches for future_matches in non_empty_matches if "後" in future_matches) :
            non_empty_matches[match] = DatetimeConverter.get_std_future_datetime_text(non_empty_matches[match])

        # replace origin datetime strings with new string
        result = any_cht_sentence
        for match in non_empty_matches :
            result = result.replace(match, f" {non_empty_matches[match]} ")

        return result


    @staticmethod
    def extract_datetime( any_cht_text: str ) -> (datetime, datetime) :
        """
        extract and convert datetime text with arabic numeral value to datetime instance from input cht text

        :param any_cht_text: any cht text
        :return: tuple of (datetime, None) or (start_datetime, end_datetime) extracted from input text
        """
        # target datetime format

        # remove useless chars and find datetime matches from it
        abs_sentence = DatetimeConverter.standardize_datetime(any_cht_text)
        clean_abs_sentence = re.sub("[\r\n\t ]", "", abs_sentence)
        matches_iter = DatetimeConverter.__ARABIC_DATETIME_RANGE_RULE.finditer(clean_abs_sentence)
        non_empty_matches = [match_iter.group() for match_iter in matches_iter if match_iter.group() != '']

        # if not find any datetime fmt, return today time range
        if non_empty_matches is [] :
            # today's datetime range
            today_begin = datetime.datetime.combine(datetime.date.today(), datetime.time())
            today_finish = today_begin + datetime.timedelta(days = 1, minutes = -1)
            return today_begin, today_finish

        # if find datetime description in text, parse it
        else :
            match = non_empty_matches[0]
            if "到" in match :
                time_range = match.split("到")
                start = DatetimeConverter.to_datetime(time_range[0])
                end = DatetimeConverter.to_datetime(time_range[1])
                return start, end
            else :
                return DatetimeConverter.to_datetime(match), None


if __name__ == '__main__' :

    # print(res)
    # res = DatetimeConverter.abs_future_time(res)
    text = "我想知道明天到後天有什麼活動"
    res = DatetimeConverter.extract_datetime(text)
    print(res)