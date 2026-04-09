from pydantic import BaseModel


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str
    conversation_history: list[ChatMessage] = []
    session_id: str | None = None


class ChatResponse(BaseModel):
    reply: str
    intent: str | None = None  # "tu_van_thong_tin", "ho_tro_dat_lich", "tu_van_quy_trinh", "ngoai_domain"
    confidence: str | None = None  # "HIGH", "MEDIUM", "LOW"
    needs_confirmation: bool = False
    booking_data: dict | None = None
