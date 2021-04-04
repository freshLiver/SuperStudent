from botlib.semantic_analyzer import SemanticAnalyzer
from botlib.services import match_service



if __name__ == '__main__' :
    text = "我想知道中時的新聞"
    analyzer = SemanticAnalyzer(text)
    analyzer.parse_content()
    res = match_service(analyzer)
    print(res)