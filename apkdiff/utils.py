import re
from androguard.misc import AnalyzeAPK
from androguard.core.apk import APK
from androguard.core.analysis.analysis import Analysis
from typing import Optional, Tuple, List, Any

_SCRAMBLED_NAME_RE: re.Pattern = re.compile(r"(?:\w+(?:/\w+)+)|(?:^\w{,2}$)")
_SCRAMBLED_WHITELIST = [
    'android',
    'androidx',
    'java',
    'kotlin'
]


def strip_class_name(class_name: str) -> str:
    matches = _SCRAMBLED_NAME_RE.findall(class_name)
    if len(matches) == 0:
        return class_name
    for group in matches:
        if group.split('/')[0] not in _SCRAMBLED_WHITELIST and group.split('/')[0][1:] not in _SCRAMBLED_WHITELIST:
            class_name = class_name.replace(group, '')
    return class_name


def extract_apk(apk_path: str) -> Tuple[Optional[APK], Optional[Analysis]]:
    print("[+] Running androguard to decompile the apk.")
    try:
        apk, _, dx = AnalyzeAPK(apk_path)
    except Exception as e:
        print(e)
        print(f"Error processing {apk_path}.")
        return None, None
    print("[+] Androguard processed the apk.")
    return apk, dx


def strip_ast(ast: dict) -> dict:
    def _strip(value: Any) -> Any:
        if isinstance(value, str):
            return strip_class_name(value)
        if isinstance(value, list):
            return [_strip(item) for item in value]
        if isinstance(value, tuple):
            return tuple(_strip(item) for item in value)
        if isinstance(value, dict):
            return {key: _strip(value[key]) for key in value.keys()}
        if isinstance(value, bool) or isinstance(value, int) or isinstance(value, float) or value is None:
            return value
        raise ValueError(f"Wrong type! {type(value)}")

    return _strip(ast)


def get_strings(ast: dict) -> List[str]:
    def _get_strings(value: Any) -> List[str]:
        if isinstance(value, list):
            if len(value) == 3 and value[0] == 'Literal' and value[2] == ('java/lang/String', 0):
                return [value[1]]
            return [string for item in value for string in _get_strings(item)]
        if isinstance(value, dict):
            return [item for key in value.keys() for item in _get_strings(value[key])]
        return []

    return _get_strings(ast)
