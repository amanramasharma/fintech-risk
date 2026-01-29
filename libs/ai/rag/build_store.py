import argparse
from pathlib import Path

from libs.ai.embeddings.gateway import EmbeddingsGateway, EmbeddingsGatewayConfig
from libs.ai.embeddings.providers.openai_provider import OpenAIEmbeddingsConfig, OpenAIEmbeddingsProvider
from libs.ai.rag.vector_store import FaissVectorStore, VectorDoc
from libs.risk.taxonomy.loader import load_taxonomy


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--taxonomy", type=str, default="configs/risk_taxonomy.yaml")
    ap.add_argument("--out", type=str, default="artifacts/rag_store")
    ap.add_argument("--openai-key", type=str, required=True)
    ap.add_argument("--emb-model", type=str, default="text-embedding-3-small")
    args = ap.parse_args()

    provider = OpenAIEmbeddingsProvider(OpenAIEmbeddingsConfig(api_key=args.openai_key, model=args.emb_model))
    gateway = EmbeddingsGateway(EmbeddingsGatewayConfig(provider="openai", model=args.emb_model), provider)

    tax = load_taxonomy(Path(args.taxonomy))

    docs: list[VectorDoc] = []
    texts: list[str] = []

    for cat_key, cat in tax.categories.items():
        txt = f"Category: {cat_key}\nLabel: {cat.label}\nSeverity: {cat.severity}\nReasons: {', '.join(cat.reasons)}"
        docs.append(VectorDoc(doc_id=f"cat::{cat_key}", text=txt, metadata={"type":"taxonomy_category","category":cat_key}))
        texts.append(txt)

    vectors = [gateway.embed(t).vector for t in texts]

    store = FaissVectorStore(dim=len(vectors[0]))
    store.add(vectors=vectors, docs=docs)
    store.save(Path(args.out))

    print(f"saved rag store to: {args.out}")


if __name__ == "__main__":
    main()