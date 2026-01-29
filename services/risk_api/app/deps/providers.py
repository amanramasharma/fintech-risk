from pathlib import Path
import hashlib
import os
import shutil

from libs.ai.embeddings.gateway import EmbeddingsGateway, EmbeddingsGatewayConfig
from libs.ai.embeddings.providers.openai_provider import OpenAIEmbeddingsConfig, OpenAIEmbeddingsProvider

from libs.ai.llm.gateway import LLMGateway, LLMGatewayConfig
from libs.ai.llm.providers.openai_provider import OpenAIChatConfig, OpenAIChatProvider

from libs.audit.writer import PostgresAuditWriter
from libs.ml.fraud.loader import load_fraud_model
from libs.ml.registry.interface import ModelRef

from libs.risk.decisioning.engine import DecisionEngine
from libs.risk.explanations.generator import ExplanationGenerator
from libs.risk.fraud.engine import FraudEngine
from libs.risk.fraud.scorer import FraudScorer
from libs.risk.orchestrator import RiskOrchestrator
from libs.risk.service import RiskService
from libs.risk.taxonomy.loader import load_taxonomy
from libs.risk.text.embeddings import TextEmbeddingsClient
from libs.risk.text.engine import TextRiskEngine
from libs.risk.text.label_index import build_label_index, load_label_index, save_label_index

from ..settings import Settings


def _file_hash(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()[:12]


class LocalModelRegistry:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir

    def load(self, ref: ModelRef, dest_dir: Path) -> Path:
        src = self.base_dir / ref.name / ref.version
        if not src.exists():
            raise FileNotFoundError(f"local model not found: {src}")

        dest_dir.mkdir(parents=True, exist_ok=True)
        for p in src.iterdir():
            if p.is_file():
                shutil.copy2(p, dest_dir / p.name)
        return dest_dir


def build_risk_service(settings: Settings) -> RiskService:
    taxonomy_path = Path(settings.taxonomy_path)
    taxonomy = load_taxonomy(taxonomy_path)

    registry = LocalModelRegistry(Path(os.getenv("LOCAL_MODEL_DIR", "artifacts")))
    ref = ModelRef(name=settings.fraud_model_name, version=settings.fraud_model_version)

    fraud_bundle = load_fraud_model(registry=registry, ref=ref, cache_dir=Path(settings.model_cache_dir))
    fraud_engine = FraudEngine(scorer=FraudScorer(bundle=fraud_bundle))

    emb_provider = OpenAIEmbeddingsProvider(OpenAIEmbeddingsConfig(api_key=settings.openai_api_key, model=settings.embeddings_model))
    emb_gateway = EmbeddingsGateway(EmbeddingsGatewayConfig(provider="openai", model=settings.embeddings_model), emb_provider)
    text_emb = TextEmbeddingsClient(gateway=emb_gateway)

    sig = _file_hash(taxonomy_path)
    label_index_path = Path(settings.label_index_path).with_name(
        f"label_index__{sig}__{settings.embeddings_model.replace('/','_')}.json"
    )

    if label_index_path.exists():
        label_index = load_label_index(label_index_path)
    else:
        labels = sorted(set(taxonomy.iter_reason_codes()))
        label_index = build_label_index(emb_gateway, labels)
        save_label_index(label_index, label_index_path)

    text_engine = TextRiskEngine(embeddings=text_emb, label_index=label_index)

    orchestrator = RiskOrchestrator(
        decision_engine=DecisionEngine(taxonomy=taxonomy),
        fraud_engine=fraud_engine,
        text_engine=text_engine,
    )

    audit_writer = PostgresAuditWriter(dsn=settings.postgres_dsn, env=settings.env, service_name="risk_api")

    explainer = None
    if settings.openai_api_key:
        llm_provider = OpenAIChatProvider(
            OpenAIChatConfig(
                api_key=settings.openai_api_key,
                model=getattr(settings, "llm_model", "gpt-4o-mini"),
                temperature=float(getattr(settings, "llm_temperature", 0.2)),
                timeout_seconds=30,
            )
        )
        llm = LLMGateway(
            LLMGatewayConfig(
                provider="openai",
                model=getattr(settings, "llm_model", "gpt-4o-mini"),
                timeout_seconds=30,
            ),
            llm_provider,
        )
        explainer = ExplanationGenerator(llm=llm)

    return RiskService(orchestrator=orchestrator, audit_writer=audit_writer, explainer=explainer)