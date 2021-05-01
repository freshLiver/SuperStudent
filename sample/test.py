from botlib.semantic_analyzer import SemanticAnalyzer
from botlib.services import match_service



if __name__ == '__main__' :
    # text = "三月七號台南火車站有發放免費便當的活動"
    # text = "六月四號成大資工系館會舉辦專題展"
    text = "用台語告訴我今天tvbs關於火災的報導"
    analyzer = SemanticAnalyzer(text)
    analyzer.parse_content()
    res = match_service(analyzer)
    print(res)
