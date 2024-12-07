import argparse
from timeit import default_timer
from typing import List
from androguard.util import set_log
from apkdiff.utils import extract_apk
from apkdiff.common import *
from apkdiff.Comparer import Comparer

set_log('CRITICAL')


def compare(apk1: APK, dex1: Analysis, apk2: APK, dex2: Analysis, classes: List[str]) -> Comparer:
    result = Comparer(APKAnalysis(apk1, dex1), APKAnalysis(apk2, dex2), classes)
    result.compare()
    return result


def main():
    start = default_timer()
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("--path1", "-p1", dest="path1", type=str, required=True)
    parser.add_argument("--path2", "-p2", dest="path2", type=str, required=True)
    parser.add_argument("--jadx", "-j", dest="jadx", type=str, required=True)
    parser.add_argument("--temp_path", "-t", dest="temp_path", type=str, required=False, default='cache')
    args = parser.parse_args()
    apk1, dex1 = extract_apk(args.path1)
    if apk1 is None:
        return -1
    del apk1
    apk2, dex2 = extract_apk(args.path2)
    if apk2 is None:
        return -1
    del apk2
    classes_to_find = ['LV5/t;']  # Suppose to be LX5/s;
    result = compare(None, dex1, None, dex2, classes_to_find)
    print('The results are: ')
    print(result)
    print(f"It took {default_timer() - start} seconds to complete the run.")


if __name__ == "__main__":
    exit(main())
