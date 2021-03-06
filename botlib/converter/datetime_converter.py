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

    __DATETIME_UNIT_FMT_MAP = {
        __YEAR___UNIT_FMT : "%Y年",
        __MONTH__UNIT_FMT : "%m月",
        __DATE___UNIT_FMT : "%d日",
        __HOUR___UNIT_FMT : "%H點",
        __MINUTE_UNIT_FMT : "%M分"
    }

    __STD_DATE_FMT = "%Y年%m月%d日"
    __STD_DATETIME_FMT = f"{__STD_DATE_FMT}%H點%M分"

    __CHT_NUMBER_FMT = "[零一二兩三四五六七八九十0123456789]+"
    __CHT_DATETIME_FMT = f"({__CHT_NUMBER_FMT}個?{__YEAR___UNIT_FMT})?[又]?"
    __CHT_DATETIME_FMT += f"({__CHT_NUMBER_FMT}個?{__MONTH__UNIT_FMT})?[又]?"
    __CHT_DATETIME_FMT += f"({__CHT_NUMBER_FMT}個?{__WEEK___UNIT_FMT})?[又]?"
    __CHT_DATETIME_FMT += f"({__CHT_NUMBER_FMT}個?{__DATE___UNIT_FMT})?[又]?"
    __CHT_DATETIME_FMT += f"({__CHT_NUMBER_FMT}個?{__HOUR___UNIT_FMT})?[又]?"
    __CHT_DATETIME_FMT += f"({__CHT_NUMBER_FMT}個?{__MINUTE_UNIT_FMT})?(之?前|後)?"
    __CHT_DATETIME_RULE = re.compile(__CHT_DATETIME_FMT)

    __ARABIC_NUMBER_FMT = "\d+"
    __ARABIC_NUMBER_RULE = re.compile(__ARABIC_NUMBER_FMT)
    __ARABIC_YEAR___RULE = re.compile(f"{__ARABIC_NUMBER_FMT}個?{__YEAR___UNIT_FMT}")
    __ARABIC_MONTH__RULE = re.compile(f"{__ARABIC_NUMBER_FMT}個?{__MONTH__UNIT_FMT}")
    __ARABIC_WEEK___RULE = re.compile(f"{__ARABIC_NUMBER_FMT}個?{__WEEK___UNIT_FMT}")
    __ARABIC_DATE___RULE = re.compile(f"{__ARABIC_NUMBER_FMT}個?{__DATE___UNIT_FMT}")
    __ARABIC_HOUR___RULE = re.compile(f"{__ARABIC_NUMBER_FMT}個?{__HOUR___UNIT_FMT}")
    __ARABIC_MINUTE_RULE = re.compile(f"{__ARABIC_NUMBER_FMT}個?{__MINUTE_UNIT_FMT}")

    __ARABIC_DATETIME_FMT = f"({__ARABIC_NUMBER_FMT}個?{__YEAR___UNIT_FMT})?[又]?"
    __ARABIC_DATETIME_FMT += f"({__ARABIC_NUMBER_FMT}個?{__MONTH__UNIT_FMT})?[又]?"
    __ARABIC_DATETIME_FMT += f"({__ARABIC_NUMBER_FMT}個?{__WEEK___UNIT_FMT})?[又]?"
    __ARABIC_DATETIME_FMT += f"({__ARABIC_NUMBER_FMT}個?{__DATE___UNIT_FMT})?[又]?"
    __ARABIC_DATETIME_FMT += f"({__ARABIC_NUMBER_FMT}個?{__HOUR___UNIT_FMT})?[又]?"
    __ARABIC_DATETIME_FMT += f"({__ARABIC_NUMBER_FMT}個?{__MINUTE_UNIT_FMT})?"
    __ARABIC_DATETIME_RULE = re.compile(__ARABIC_DATETIME_FMT)

    __ARABIC_FUTURE_DATETIME_RULE = re.compile(__ARABIC_DATETIME_FMT + "之?後")
    __ARABIC_PAST_DATETIME_RULE = re.compile(__ARABIC_DATETIME_FMT + "之?前")

    __ARABIC_DATETIME_RANGE_FMT = f"從?{__ARABIC_DATETIME_FMT}(到{__ARABIC_DATETIME_FMT})?"
    __ARABIC_DATETIME_RANGE_RULE = re.compile(__ARABIC_DATETIME_RANGE_FMT)


    # ----------------------------------------------------------------------------------

    @staticmethod
    def parse_common_date_words( any_text: str ) -> str :
        """
        將常見的日期表示（例如：昨天、前天、明年）轉換成實際的日期

        :param any_text: 要進行轉換的字串
        :return: 將原字串中將常見日期轉換成實際日期後的結果
        """

        now = datetime.datetime.now()
        date_fmt = DatetimeConverter.__STD_DATE_FMT

        # year，計算字串中所有與「年」相關的時間字串的「年位移」並替換掉原本的時間字串
        year_rule = re.compile("[前去今明後]年")
        year_matches = year_rule.finditer(any_text)
        for match in year_matches :
            year_text = match.group()
            year_shift = 0
            if "前" in year_text :
                year_shift = -2
            elif "去" in year_text :
                year_shift = -1
            elif "明" in year_text :
                year_shift = 1
            elif "後" in year_text :
                year_shift = 2
            year_text = str((now + relativedelta(years = year_shift)).year)
            any_text = any_text.replace(match.group(), f"{year_text}年")

        # month，計算字串中所有與「月」相關的時間字串的「月位移」並替換掉原本的時間字串
        month_rule = re.compile("(上+|這|下+)個?月")
        month_matches = month_rule.finditer(any_text)
        for match in month_matches :
            month_text = match.group()
            month_shift = 0
            if "下" in month_text :
                for char in month_text :
                    month_shift += 1 if char == "下" else 0
            elif "上" in month_text :
                for char in month_text :
                    month_shift += -1 if char == "上" else 0
            month_text = str((now + relativedelta(months = month_shift)).month)
            any_text = any_text.replace(match.group(), f"{month_text}月")

        # week，計算字串中所有與「周」相關的時間字串的「周位移」並替換掉原本的時間字串
        week_rule = re.compile("(上+|這|下+)個?(禮拜|星期|周|週)")
        week_matches = week_rule.finditer(any_text)
        this_week_start = now + relativedelta(days = -1 * now.weekday())
        this_week_end = this_week_start + relativedelta(days = 6)
        for match in week_matches :
            week_text = match.group()
            week_shift = 0
            if "下" in week_text :
                for char in week_text :
                    week_shift += 1 if char == "下" else 0
            elif "上" in week_text :
                for char in week_text :
                    week_shift += -1 if char == "上" else 0

            # 找到目標周的開頭以及結尾日期
            start_date = this_week_start + relativedelta(weeks = week_shift)
            end_date = start_date + relativedelta(days = 6)

            # 將原本的相對日期表示改用「日期範圍」表示
            week_text = f"{start_date.strftime(date_fmt)} 到 {end_date.strftime(date_fmt)}"
            any_text = any_text.replace(match.group(), week_text)

        # day，計算字串中所有與「日」相關的時間字串的「日位移」並替換掉原本的時間字串
        day_rule = re.compile("[前昨今明後][天日]")
        day_matches = day_rule.finditer(any_text)
        for match in day_matches :
            day_text = match.group()
            day_shift = 0
            if "明" in day_text :
                day_shift = 1
            elif "昨" in day_text :
                day_shift = -1
            elif "後" in day_text :
                day_shift = 2
            elif "前" in day_text :
                day_shift = -2
            day_text = str((now + relativedelta(days = day_shift)).strftime(date_fmt))
            any_text = any_text.replace(match.group(), f"{day_text}")

        # 處理其他比較沒有規律的常見時間表示
        # TODO : 周X、週末、月底、月初、年初、年末

        # 將原字串中將常見日期轉換成實際日期後的結果
        return any_text


    @staticmethod
    def simplify_cht_numeral_representations( cht_number_text: str ) -> str :
        """
        todo : comment for code
        將字串中的「中文數值」轉換為「便於阿拉伯數值化」的表示，例如：
            1. 二十 -> 二零
            2. 十二 -> 一二
            3. 二十三 -> 二三

        :param cht_number_text: 想簡化的字串
        :return: 簡化結果
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
    def cht_to_arabic_numerals( any_text: str ) -> str :
        """
        將字串中的「中文數值」轉換成「阿拉伯數值」

        :param any_text: 想進行轉換的字串
        :return: 轉換結果
        """
        for char in DatetimeConverter.__NUMBER_CONVERT_DICT :
            any_text = any_text.replace(char, DatetimeConverter.__NUMBER_CONVERT_DICT[char])
        return any_text


    @staticmethod
    def to_datetime( std_arabic_value_datetime_text: str, from_now = False, is_past = False ) -> datetime or None :
        """
        將「以阿拉伯數值表示的 年月日時分 字串」轉換成 datetime instance

        :param std_arabic_value_datetime_text: 以「以阿拉伯數值表示的 年月日時分 字串」
        :param from_now: 是否以當前時間為基準進行抽取，預設為 false
        :param is_past: 以當前時間作為基準「往過去」計算時間，預設為「往未來」找
        :return: 「第一個」符合條件的 datetime instance，若沒有則回傳 None
        """

        # 找出所有「以阿拉伯數值表示的 年月日時分 字串」
        matches = DatetimeConverter.__ARABIC_DATETIME_RULE.search(std_arabic_value_datetime_text)

        # 如果沒找到就回傳 None
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
        if from_now == True :
            return now + (-1 if is_past else +1) * delta_time
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
    def get_min_real_datetime_text( dt_str: str, dt: datetime.datetime ) -> str :

        # datetime format : value
        result_datetime_fmt = DatetimeConverter.__STD_DATETIME_FMT

        # 以原字串的最小時間單位作為基礎
        for fmt in DatetimeConverter.__DATETIME_UNIT_FMT_MAP.__reversed__() :
            if re.findall(fmt, dt_str) == [] :
                result_datetime_fmt = result_datetime_fmt.replace(DatetimeConverter.__DATETIME_UNIT_FMT_MAP[fmt], "")
            else :
                break

        # 以最簡表示取代原時間字串
        return dt.strftime(result_datetime_fmt)


    @staticmethod
    def get_real_datetime_text( arabic_value_datetime_text: str ) -> str :
        """
        以「阿拉伯數值」表示的「相對時間（例如：1個月3天5小時後、2天前）」的字串轉成 年月日時分 表示（以當前時間作為基準）
        
        :param arabic_value_datetime_text: 以「阿拉伯數值」表示的「相對時間」的字串
        :return: 基於當前時間，以「年月日時分」表示的時間字串
        """

        # 找出時間字串
        past_matches = DatetimeConverter.__ARABIC_PAST_DATETIME_RULE.finditer(arabic_value_datetime_text)
        future_matches = DatetimeConverter.__ARABIC_FUTURE_DATETIME_RULE.finditer(arabic_value_datetime_text)

        # 如果沒有符合條件的字串就回傳原字串
        if past_matches == future_matches is None :
            return arabic_value_datetime_text

        # 處理所有時間字串
        else :
            result = arabic_value_datetime_text

            # 找出所有相符字串並以長度進行排序
            past_texts = [past_match.group(0) for past_match in past_matches]
            past_texts.sort(key = len, reverse = True)
            future_texts = [future_match.group(0) for future_match in future_matches]
            future_texts.sort(key = len, reverse = True)

            # 處理所有過去字串
            for past_text in past_texts :
                clean_past_text = past_text.replace("個", "").replace("又", "")
                real_datetime = DatetimeConverter.to_datetime(clean_past_text, from_now = True, is_past = True)
                result = result.replace(past_text, DatetimeConverter.get_min_real_datetime_text(clean_past_text, real_datetime))

            # 處理所有未來字串
            for future_text in future_texts :
                clean_future_text = future_text.replace("個", "").replace("又", "")
                real_datetime = DatetimeConverter.to_datetime(clean_future_text, from_now = True)
                result = result.replace(future_text, DatetimeConverter.get_min_real_datetime_text(clean_future_text, real_datetime))

            return result


    @staticmethod
    def standardize_datetime( any_cht_sentence: str ) -> str :
        """
        將字串中「以中文表示」的 datetime 改用「年月日時分（數值為阿拉伯數字）」來表示

        :param any_cht_sentence: any cht sentence
        :return: 以「年月日時分（數值為阿拉伯數字）」進行表示的 datetime
        """

        # 將字串中 "今天", "明天" 之類常見的時間改用「年月日時分」表示
        any_cht_sentence = DatetimeConverter.parse_common_date_words(any_cht_sentence)

        # 將中文時間數值轉成阿拉伯數值

        # 抓出「數值為中文」的 datetime substring
        cht_datetime_matches = DatetimeConverter.__CHT_DATETIME_RULE.finditer(any_cht_sentence)
        datetime_dict = { }
        for cht_datetime_match in cht_datetime_matches :
            match_text = cht_datetime_match.group()
            # 只要有任何「數值為中文的 datetime substring」就建立字典（原時間字串：處理後的時間字串）
            if re.search(DatetimeConverter.__CHT_NUMBER_FMT, match_text) is not None :
                datetime_dict[match_text] = ""

        # 如果沒有任何「數值為中文的 datetime substring」就直接回傳原字串
        if datetime_dict == { } :
            return any_cht_sentence

        # 若有任何「數值為中文的 datetime substring」的話就分別進行轉換（轉成以阿拉伯數字表示的 datetime substring）
        for match in datetime_dict :
            # 先簡化「datetime substring 中的中文數值」，以便轉化成阿拉伯數字（例如：五十二 -> 五二）
            tmp = DatetimeConverter.simplify_cht_numeral_representations(match)

            # 將簡化後的中文數值轉成阿拉伯數值
            tmp = DatetimeConverter.cht_to_arabic_numerals(tmp)

            # 刪除多餘字，並且將處理後的結果存到原字串的字典（原字串：處理後的結果）
            datetime_dict[match] = tmp.replace("又", "").replace("個", "")

        # 將「相對時間（阿拉伯數值）的字串」轉換成絕對時間（例如：1 天後 -> 3月3日, 1 天前 -> 3月1日，假設今天為三月二號）
        # 非相對時間的則會直接回傳原字串
        for datetime_text in datetime_dict :
            datetime_dict[datetime_text] = DatetimeConverter.get_real_datetime_text(datetime_dict[datetime_text])

        # 利用建立的字典（原時間字串：處理後的時間字串）替換掉原句的中文時間字串
        result = any_cht_sentence
        for match in datetime_dict :
            result = result.replace(match, f"{datetime_dict[match]}")

        # 回傳處理後的字串
        return result


    @staticmethod
    def extract_datetime( any_text: str ) -> (datetime, datetime) :
        """
        抽取出以「中文數值」表示的時間字串中的時間範圍，依序回經過數個步驟：
            1. 將原字串轉換成以「年月日時分」表示的時間字串
            2. 找出「以中文數值表示的時間字串」
            3. 判斷是否為「時間範圍」，然後抽取時間並進行對應處理
            4. 回傳時間範圍


        :param any_text: 想抽取時間的字串
        :return: 抽取出的（起始時間,結束時間）的 tuple，如果沒找到則會回傳當天時間（00:00 ~ 23:59）
        """

        # 轉換成以「年月日時分（阿拉伯數值）」表示的時間字串
        clean_any_text = re.sub("[\r\n\t ]", "", any_text)
        std_datetime_sentence = DatetimeConverter.standardize_datetime(clean_any_text)

        # 移除多餘的字，並找出所有以「阿拉伯數值」表示的時間字串
        std_datetime_matches = DatetimeConverter.__ARABIC_DATETIME_RANGE_RULE.finditer(std_datetime_sentence)
        std_datetime_texts = [match.group() for match in std_datetime_matches if match.group() != '']

        # 如果沒有找到符合的時間字串就還傳今天時間（00:00 ~ 23:59）作為預設
        if std_datetime_texts == [] :
            today_begin = datetime.datetime.combine(datetime.date.today(), datetime.time())
            today_finish = today_begin + datetime.timedelta(days = 1, minutes = -1)
            return today_begin, today_finish

        # 有任何符合的時間字串就進行抽取
        else :
            match = std_datetime_texts[0]

            # 如果有找到時間範圍（時間1 到 時間2）就回傳找到的範圍
            if "到" in match :
                time_range = match.split("到")
                start = DatetimeConverter.to_datetime(time_range[0])
                end = DatetimeConverter.to_datetime(time_range[1])
                return start, end

            # TODO 如果只是單一時間就將時間結尾設成當天結束（23:59）並回傳範圍
            else :
                start = DatetimeConverter.to_datetime(match)
                end = start.replace(hour = 23, minute = 59)
                return start, end


if __name__ == '__main__' :

    # print(res)
    # res = DatetimeConverter.abs_future_time(res)
    text = "5天三小時後有什麼活動"
    res = DatetimeConverter.standardize_datetime(text)
    print(res)