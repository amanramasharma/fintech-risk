from dataclasses import dataclass

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from libs.ai.rag.retriever import Retriever
from libs.risk.decisioning.types import RiskDecision


_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "You write short compliance-friendly explanations. Do not invent facts. Use only the evidence given."),
    ("user", """
Decision:
Category: {category}
Score: {score}
Reasons: {reasons}

Evidence Retrieved:
{retrieved}

Write <=120 words. One paragraph.
""".strip()),
])


@dataclass(frozen=True)
class LangChainExplainer:
    retriever: Retriever
    llm: ChatOpenAI

    def explain(self, decision: RiskDecision) -> tuple[str, list[str]]:
        query = f"{decision.risk_category} | " + " ".join([r.value for r in decision.reasons])
        docs = self.retriever.retrieve(query, k=5)
        retrieved = "\n\n".join([d.text for d in docs])

        reasons = ", ".join([r.value for r in decision.reasons]) or "none"
        msg = _PROMPT.invoke({
            "category": str(decision.risk_category),
            "score": str(float(decision.risk_score)),
            "reasons": reasons,
            "retrieved": retrieved or "none",
        })
        out = self.llm.invoke(msg)
        return (str(out.content).strip(), [d.doc_id for d in docs])