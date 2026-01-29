from dataclasses import dataclass
from threading import Lock
from libs.risk.service import RiskService
from .providers import build_risk_service
from ..settings import Settings

@dataclass
class Container:
    settings: Settings
    risk_service: RiskService

_container: Container | None = None
_lock = Lock()

def get_container() -> Container:
    if _container is None:
        raise RuntimeError("Container not initialized. Call init_container() at startup.")
    return _container

def init_container(settings: Settings) -> Container:
    global _container
    if _container is not None:
        return _container
    with _lock:
        if _container is not None:
            return _container
        risk_service = build_risk_service(settings)
        _container = Container(settings=settings,risk_service=risk_service)
        return _container