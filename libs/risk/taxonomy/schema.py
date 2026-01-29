from pydantic import BaseModel,Field

class CategoryThresholds(BaseModel):
    score_high: float = Field(...,ge=0.0,le=1.0)
    score_medium: float = Field(...,ge=0.0,le=1.0)

class CategoryConfig(BaseModel):
    label: str
    severity: float = Field(...,ge=0.0,le=1.0)
    reasons: list[str] = Field(default_factory=list)
    thresholds: CategoryThresholds

class TaxonomyConfig(BaseModel):
    version: str
    owner: str
    description: str | None = None
    categories: dict[str,CategoryConfig] = Field(default_factory=dict)

    def iter_reason_codes(self):
        for _,cat in self.categories.items():
            for r in cat.reasons:
                yield r