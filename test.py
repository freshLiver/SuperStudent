from botlib.semantic_analyzer import SemanticAnalyzer
from botlib.services import service_matching



if __name__ == '__main__' :
    text = "今天晚上有什麼活動"
    analyzer = SemanticAnalyzer(text)
    analyzer.parse_content()
    res = service_matching(analyzer)
    print(res)