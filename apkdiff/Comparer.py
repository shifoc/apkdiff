from tqdm import tqdm
from concurrent.futures.thread import ThreadPoolExecutor
from typing import Dict, Optional, List

from apkdiff.MultiClassComparer import MultiClassComparer
from apkdiff.common import APKAnalysis
from androguard.core.analysis.analysis import ClassAnalysis
from apkdiff.utils import strip_class_name, strip_ast, get_strings
from apkdiff.PreparedClass import PreparedClass


class Comparer:
    classes: Dict[str, Optional[str]]

    def __init__(self, analysis1: APKAnalysis, analysis2: APKAnalysis, classes: List[str]):
        self.analysis1 = analysis1
        self.analysis2 = analysis2
        self.classes = {cls: None for cls in classes}
        self.prepared_classes: List[PreparedClass] = []

    @staticmethod
    def thread_prepare_class(class_name: str, analysis: ClassAnalysis) -> PreparedClass:
        ast = analysis.get_class().get_ast()
        return PreparedClass(class_name, analysis, ast, strip_ast(ast), get_strings(ast))

    def prepare_classes(self) -> None:
        with ThreadPoolExecutor(max_workers=32) as executor:
            futures = []
            for class_name in self.analysis2.analysis.classes:
                if strip_class_name(class_name) == '' or self.analysis2.analysis.classes[class_name].external:
                    continue
                futures.append(
                    executor.submit(self.thread_prepare_class, class_name, self.analysis2.analysis.classes[class_name]))

            for future, _ in zip(futures, tqdm(range(len(futures)))):
                self.prepared_classes.append(future.result())

            return class_name

    def compare_classes(self):
        self.prepare_classes()
        for class_to_match in self.classes:
            class_name = MultiClassComparer(self.analysis1.analysis.classes[class_to_match],
                                            self.prepared_classes).get_similar_class()
            self.classes[class_to_match] = class_name

    def compare(self):
        self.compare_classes()
        print(self.classes)
