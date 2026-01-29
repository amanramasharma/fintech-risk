from pydantic import BaseModel,Field
from libs.risk.decisioning.evidence import Evidence
from libs.risk.decisioning.provenance import DecisionProvenance
from libs.risk.decisioning.reasons import ReasonCode
from libs.risk.text.rules import apply_rules
from libs.risk.text.schema import TextCase
from libs.risk.text.similarity import top_hits
from libs.risk.text.embeddings import TextEmbeddingsClient
from libs.risk.text.label_index import LabelIndex
from libs.risk.text.retrieval import CaseRetriever
from libs.ai.rag.retriever import Retriever
from libs.ai.rag.vector_store import VectorDoc


class TextSignals(BaseModel):
    base_score: float = Field(...,ge=0.0,le=1.0)
    reasons: list[ReasonCode]
    evidence: list[Evidence]
    provenance: DecisionProvenance
    debug: dict


def _to_reason(s: str) -> ReasonCode | None:
    try:
        return ReasonCode(s)
    except Exception:
        return None


class TextRiskEngine:
    def __init__(self, embeddings: TextEmbeddingsClient, label_index: LabelIndex, case_retriever: CaseRetriever | None = None, rag: Retriever | None = None):
        self.embeddings = embeddings
        self.label_index = label_index
        self.case_retriever = case_retriever
        self.rag = rag

    def detect(self, case: TextCase) -> TextSignals:
        reasons: list[ReasonCode] = []
        evidence: list[Evidence] = []
        seen: set[str] = set()

        rule_hits = apply_rules(case.text)
        for h in rule_hits:
            rc = _to_reason(h.reason)
            if rc and rc.value not in seen:
                seen.add(rc.value)
                reasons.append(rc)
            evidence.append(Evidence(source="text.rules",description=f"Matched rule phrase for {h.reason}",value={"span":h.span,"text":h.matched_text},threshold=None,metadata={"case_id":case.case_id,"channel":case.channel},))

        emb = self.embeddings.embed(case.text).vector
        hits = top_hits(emb,self.label_index.vectors,k=3)
        base = max((h.score for h in hits), default=0.0)

        for hit in hits:
            if hit.score >= 0.70:
                rc = _to_reason(hit.label)
                if rc and rc.value not in seen:
                    seen.add(rc.value)
                    reasons.append(rc)
                evidence.append(Evidence(source="text.embedding_similarity",description="High semantic similarity to risk label",value={"label":hit.label,"score":hit.score},threshold=0.70,metadata={"case_id":case.case_id,"channel":case.channel,"embedding_model":self.label_index.model},))

        retrieved_cases = []
        if self.case_retriever is not None:
            retrieved_cases = self.case_retriever.retrieve(case.text, k=3)
            for r in retrieved_cases:
                if r.score >= 0.75:
                    evidence.append(Evidence(source="text.case_retrieval",description="Similar past case retrieved (evidence only)",value={"case_id":r.case_id,"score":r.score,"text":r.text[:280]},threshold=0.75,metadata={"case_id":case.case_id,"channel":case.channel},))

        rag_docs: list[VectorDoc] = []
        if self.rag is not None:
            rag_docs = self.rag.retrieve(case.text, k=3)
            for d in rag_docs:
                evidence.append(Evidence(source="rag.taxonomy",description="Retrieved taxonomy context (evidence only)",value={"doc_id":d.doc_id,"type":d.metadata.get("type"),"category":d.metadata.get("category"),"text":d.text[:400]},threshold=None,metadata={"case_id":case.case_id,"channel":case.channel},))

        prov = DecisionProvenance(engine="text_risk_engine",model_name=f"embeddings:{self.label_index.model}",model_version="v1",prompt_version=None,)
        return TextSignals(base_score=float(min(1.0,base)),reasons=reasons,evidence=evidence,provenance=prov,debug={"rule_hits":[h.reason for h in rule_hits],"top_hits":[h.model_dump() for h in hits],"retrieved_cases":[{"case_id":r.case_id,"score":r.score} for r in retrieved_cases],"rag_docs":[{"doc_id":d.doc_id,"type":d.metadata.get("type")} for d in rag_docs],},)