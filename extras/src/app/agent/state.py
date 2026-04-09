from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    intent: str | None  # "tu_van_thong_tin", "ho_tro_dat_lich", "tu_van_quy_trinh", "ngoai_domain"
    confidence: str | None  # "HIGH", "MEDIUM", "LOW"
    domain_valid: bool | None
    symptoms: str | None
    user_address: str | None
    clinic_results: list[dict] | None
    booking_data: dict | None
    booking_confirmed: bool
    needs_user_confirmation: bool
    final_response: str | None
    loop_count: int
