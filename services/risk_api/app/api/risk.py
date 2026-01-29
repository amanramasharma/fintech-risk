from fastapi import APIRouter, Query
from ..deps.container import get_container
from libs.risk.orchestrator import RiskRequest

router = APIRouter(prefix="/risk", tags=["risk"])

from dataclasses import asdict, is_dataclass

def dump_obj(x):
    if x is None:
        return None
    if hasattr(x, "model_dump"):
        return x.model_dump()
    if hasattr(x, "dict"):
        return x.dict()
    if is_dataclass(x):
        return asdict(x)
    if hasattr(x, "__dict__"):
        return dict(x.__dict__)
    return x
def _dump(x):
    if x is None:
        return None
    if hasattr(x, "model_dump"):
        return x.model_dump()
    if hasattr(x, "__dict__"):
        return dict(x.__dict__)
    return x

@router.post("/score")
def score(req: RiskRequest, explain: int = Query(0)):
    c = get_container()
    out = c.risk_service.score(req, explain=bool(explain))

    resp = {
    "decision": out.decision.model_dump(),
    "audit": dump_obj(out.audit),
}

    if out.explanation:
        resp["explanation"] = out.explanation

    return resp
