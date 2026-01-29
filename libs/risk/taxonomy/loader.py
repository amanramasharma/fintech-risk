from pathlib import Path
import yaml

from libs.risk.taxonomy.schema import TaxonomyConfig


_DEFAULT_PATH = Path("configs/risk_taxonomy.yaml")


def load_taxonomy(path: Path | None = None) -> TaxonomyConfig:
    p = path or _DEFAULT_PATH
    raw = yaml.safe_load(p.read_text(encoding="utf-8"))
    return TaxonomyConfig.model_validate(raw)