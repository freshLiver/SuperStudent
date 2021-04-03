# project libs
from botlib import BotConfig
from botlib.converter.datetime_converter import DatetimeConverter
from botlib.semantic_analyzer import SemanticAnalyzer
from botlib.services import match_service



if __name__ == '__main__' :
    text = "十天後成大操場有活動"
    analyzer = SemanticAnalyzer(text)
    analyzer.parse_content()
    res = match_service(analyzer)
    print(res)