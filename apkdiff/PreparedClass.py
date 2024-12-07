import dataclasses
from typing import List

from androguard.core.analysis.analysis import ClassAnalysis


@dataclasses.dataclass
class PreparedClass:
    name: str
    analysis: ClassAnalysis
    ast: dict
    stripped_ast: dict
    strings: List[str]
