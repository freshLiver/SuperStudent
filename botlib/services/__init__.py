from enum import Enum

# project libs
from botlib.semantic_analyzer import SemanticAnalyzer



class Services(Enum) :
    UNKNOWN = -1
    NEWS = 0
    ACTIVITY = 1


# ------------------------------------------------------------------------------------------------------------


def service_matching( analyzer: SemanticAnalyzer ) -> str or None :
    # TODO
    pass