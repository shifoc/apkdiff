import dataclasses
import enum
from typing import Dict
from androguard.core.analysis.analysis import Analysis
from androguard.core.apk import APK

SESSION_CACHE_FILE = 'session.cache'


class ClassWeights(float, enum.Enum):
    AST_CONFIDENCE = 50 / 100
    STRINGS_CONFIDENCE = 20 / 100
    XREF_CONFIDENCE = 10 / 100
    METHODS_CONFIDENCE = 5 / 100
    FIELDS_CONFIDENCE = 5 / 100


class ClassMatchResult:
    pass


@dataclasses.dataclass
class APKAnalysis:
    apk: APK
    analysis: Analysis
