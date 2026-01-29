from pydantic import BaseModel, Field

class TextCase(BaseModel):
    case_id: str
    channel: str = Field(...,description="chat|email|call_note|complaint")
    text: str = Field(...,min_length=1)
    customer_id: str | None = None
    language: str = "en"