import hashlib
import json
from typing import Any


def stable_json_dumps(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)


def sha256_hex(text: str) -> str:
    h = hashlib.sha256()
    h.update(text.encode("utf-8"))
    return h.hexdigest()


def hash_payload(payload: Any) -> str:
    return sha256_hex(stable_json_dumps(payload))