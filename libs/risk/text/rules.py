import re
from dataclasses import dataclass

@dataclass(frozen=True)
class RuleMatch:
    reason: str
    span: tuple[int,int]
    matched_text: str

_RULES: list[tuple[str,re.Pattern]] = [
    ("distress_language_detected",re.compile(r"\b(stressed|anxious|panic|overwhelmed)\b",re.I)),
    ("repeat_complaint",re.compile(r"\b(complained\s+twice|again|multiple\s+times)\b",re.I)),
    ("misleading_information",re.compile(r"\b(told\s+me\s+wrong|misled|not\s+explained)\b",re.I)),
]

def apply_rules(text: str) -> list[RuleMatch]:
    matches: list[RuleMatch] = []
    for reason,pat in _RULES:
        for m in pat.finditer(text):
            matches.append(RuleMatch(reason=reason,span=(m.start(),m.end()),matched_text=m.group(0)))
    return matches