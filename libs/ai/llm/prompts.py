from dataclasses import dataclass


@dataclass(frozen=True)
class Prompt:
    version: str
    template: str

    def render(self, **kwargs) -> str:
        return self.template.format(**kwargs)


EXPLAIN_DECISION_V1 = Prompt(
    version="explain_decision_v1",
    template="""
You generate a compliance-friendly explanation for a FinTech risk decision.

Hard rules:
- Use ONLY the facts in Evidence. Do not infer or assume anything.
- Do NOT change currency or country. If currency is present, reuse it exactly (e.g., GBP).
- Keep it <= 90 words.
- Output ONLY plain text. No bullet points, no headings.

Risk Category: {risk_category}
Risk Score (0-1): {risk_score}

Reasons:
{reasons}

Evidence:
{evidence}

Write the explanation now.
""".strip(),
)

EXPLAIN_DECISION_STRUCTURED_V1 = Prompt(
    version="explain_decision_structured_v1",
    template="""
You are a compliance-grade AI generating a structured explanation for a FinTech risk decision.

Rules:
- Do NOT invent facts
- Use ONLY the evidence and inputs provided
- Be precise and regulator-friendly
- Output MUST be valid JSON and match the schema exactly
- Do NOT include any extra text outside JSON

Risk Category: {risk_category}
Risk Score (0-1): {risk_score}

Matched Reasons:
{reasons}

Evidence:
{evidence}

Per-category scores:
{per_category_scores}

{format_instructions}
""".strip(),
)