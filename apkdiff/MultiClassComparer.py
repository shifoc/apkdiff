from concurrent.futures.thread import ThreadPoolExecutor
from typing import List, Tuple

from androguard.core.analysis.analysis import ClassAnalysis
from tqdm import tqdm

from apkdiff.PreparedClass import PreparedClass
from apkdiff.utils import strip_ast, get_strings, strip_class_name
from deepdiff import DeepDiff
from apkdiff.common import ClassWeights


class MultiClassComparer:

    def __init__(self, class1: ClassAnalysis, classes: List[PreparedClass]) -> None:
        self.class1 = class1
        class1_ast = class1.get_class().get_ast()
        self.class1_ast = strip_ast(class1_ast)
        self.class1_strings = get_strings(class1_ast)
        self.classes = classes

    def compare_ast(self, class2: PreparedClass) -> float:
        try:
            diff = DeepDiff(self.class1_ast, class2.stripped_ast, cache_size=10000, get_deep_distance=True)
        except Exception as e:
            print(e)
            return 0
        if diff == {}:
            return 100
        return 100 - 100 * diff.get('deep_distance', 0)

    def compare_strings(self, class2: PreparedClass) -> float:
        try:
            diff = DeepDiff(self.class1_strings, class2.strings, cache_size=10000, get_deep_distance=True)
        except:
            return 0
        if diff == {}:
            return 100
        return 100 - 100 * diff.get('deep_distance', 0)

    def compare_methods(self) -> float:
        # methods = self.class1.get_class().get_methods()
        # methods = self.class2.get_class().get_methods()
        return 100

    def compare_xrefs(self) -> float:
        # xrefs1 = self.class1.get_xref_from()
        # xrefs2 = self.class2.get_xref_from()
        return 100

    def compare_fields(self) -> float:
        return 100

    def get_confidence(self, class2: PreparedClass) -> float:
        confidence = self.compare_ast(class2) * ClassWeights.AST_CONFIDENCE
        confidence += self.compare_strings(class2) * ClassWeights.STRINGS_CONFIDENCE
        confidence += self.compare_methods() * ClassWeights.METHODS_CONFIDENCE
        confidence += self.compare_fields() * ClassWeights.FIELDS_CONFIDENCE
        confidence += self.compare_xrefs() * ClassWeights.XREF_CONFIDENCE
        return confidence

    @staticmethod
    def thread_compare_class(self: 'MultiClassComparer', class2: PreparedClass) -> Tuple[PreparedClass, float]:
        return class2, self.get_confidence(class2)

    def get_similar_class(self) -> str:
        with ThreadPoolExecutor(max_workers=32) as executor:
            futures = []
            for other_class in self.classes:
                if strip_class_name(other_class.name) == '':
                    continue
                futures.append(executor.submit(self.thread_compare_class, self, other_class))

            confidence = 0
            class_name = ''
            for future, _ in zip(futures, tqdm(range(len(self.classes)))):
                current_class, current_confidence = future.result()
                if current_confidence > confidence:
                    confidence = current_confidence
                    class_name = current_class.name

            return class_name
