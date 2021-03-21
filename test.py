from botlib.semantic_analyzer import SemanticAnalyzer
from botlib.services import service_matching



if __name__ == '__main__' :
    text = "2020年12月16號到2021年06月30日在成大圖書館會進行實境遊戲"
    analyzer = SemanticAnalyzer(text)
    analyzer.parse_content()
    res = service_matching(analyzer)
    print(res)