from langchain_core.messages import HumanMessage
from app.agent.graph import agent_graph
from app.agent.state import AgentState
from app.schemas.chat import ChatRequest, ChatResponse, ChatMessage


_QUOTA_MSG = (
    "⚠️ Hệ thống AI tạm thời quá tải (OpenAI API quota/rate limit). "
    "Vui lòng thử lại sau ít phút hoặc kiểm tra API key."
)

_ERROR_MSG = "Xin lỗi, đã có lỗi xảy ra trong quá trình xử lý. Vui lòng thử lại."


def _is_quota_error(exc: Exception) -> bool:
    name = type(exc).__name__
    msg = str(exc)
    return (
        "RateLimitError" in name
        or "AuthenticationError" in name
        or "429" in msg
        or "insufficient_quota" in msg
        or "rate limit" in msg.lower()
    )


async def handle_chat(request: ChatRequest) -> ChatResponse:
    """Main chat handler — runs the LangGraph agent."""

    # Build messages from conversation history
    messages = []
    for msg in request.conversation_history:
        if msg.role == "user":
            messages.append(HumanMessage(content=msg.content))
        else:
            from langchain_core.messages import AIMessage
            messages.append(AIMessage(content=msg.content))

    # Add current message
    messages.append(HumanMessage(content=request.message))

    # Initial state
    initial_state: AgentState = {
        "messages": messages,
        "intent": None,
        "confidence": None,
        "domain_valid": None,
        "symptoms": None,
        "user_address": None,
        "clinic_results": None,
        "booking_data": None,
        "booking_confirmed": False,
        "needs_user_confirmation": False,
        "final_response": None,
        "loop_count": 0,
    }

    # Run the agent graph
    try:
        result = await agent_graph.ainvoke(initial_state)
    except Exception as exc:
        if _is_quota_error(exc):
            return ChatResponse(
                reply=_QUOTA_MSG,
                intent="tu_van_thong_tin",
                confidence=None,
                needs_confirmation=False,
                booking_data=None,
            )
        return ChatResponse(
            reply=_ERROR_MSG,
            intent=None,
            confidence=None,
            needs_confirmation=False,
            booking_data=None,
        )

    return ChatResponse(
        reply=result.get("final_response", "Xin lỗi, tôi không thể xử lý yêu cầu này."),
        intent=result.get("intent"),
        confidence=result.get("confidence"),
        needs_confirmation=result.get("needs_user_confirmation", False),
        booking_data=result.get("booking_data"),
    )
