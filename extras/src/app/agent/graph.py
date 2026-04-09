from langgraph.graph import StateGraph, END
from app.agent.state import AgentState
from app.agent.nodes import (
    reasoning_node,
    refuse_node,
    domain_check_node,
    health_info_node,
    analyze_symptoms_node,
    fetch_clinic_node,
    confirm_booking_node,
    process_guide_node,
)


def _has_symptom_analysis(state: AgentState) -> bool:
    """Check if the conversation already contains a symptom analysis from AI."""
    for m in state.get("messages", []):
        if hasattr(m, "type") and m.type == "ai" and hasattr(m, "content"):
            content = m.content
            # AI already suggested specialties and asked for booking info
            if ("chuyên khoa" in content and "Họ tên" in content) or \
               ("chuyên khoa phù hợp" in content) or \
               ("Số điện thoại" in content and "Thành phố" in content):
                return True
    return False


def _route_intent(state: AgentState) -> str:
    intent = state.get("intent")
    if intent == "ngoai_domain":
        return "refuse"
    elif intent == "ho_tro_dat_lich":
        # If symptoms already analyzed OR user just asks for clinic location → go to fetch_clinic
        if _has_symptom_analysis(state):
            return "fetch_clinic"
        # Check if it's a location/address query (no symptoms mentioned)
        last_msg = ""
        for m in reversed(state.get("messages", [])):
            if hasattr(m, "type") and m.type == "human":
                last_msg = m.content.lower()
                break
        location_keywords = ["địa chỉ", "ở đâu", "chi nhánh", "phòng khám", "tìm vinmec", "vinmec ở"]
        if any(kw in last_msg for kw in location_keywords):
            return "fetch_clinic"
        return "analyze_symptoms"
    elif intent == "tu_van_quy_trinh":
        return "process_guide"
    else:
        # tu_van_thong_tin → domain check first
        return "domain_check"


def _route_domain(state: AgentState) -> str:
    if state.get("domain_valid") is False:
        # Domain check failed or blocked topic → final_response already set
        return END
    return "health_info"


def _route_booking(state: AgentState) -> str:
    if state.get("booking_confirmed"):
        return END
    if state.get("booking_data") and not state.get("needs_user_confirmation"):
        return "confirm_booking"
    return END


def build_graph() -> StateGraph:
    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("reasoning", reasoning_node)
    graph.add_node("refuse", refuse_node)
    graph.add_node("domain_check", domain_check_node)
    graph.add_node("health_info", health_info_node)
    graph.add_node("analyze_symptoms", analyze_symptoms_node)
    graph.add_node("fetch_clinic", fetch_clinic_node)
    graph.add_node("confirm_booking", confirm_booking_node)
    graph.add_node("process_guide", process_guide_node)

    # Entry point
    graph.set_entry_point("reasoning")

    # Routing from reasoning
    graph.add_conditional_edges(
        "reasoning",
        _route_intent,
        {
            "refuse": "refuse",
            "domain_check": "domain_check",
            "analyze_symptoms": "analyze_symptoms",
            "fetch_clinic": "fetch_clinic",
            "process_guide": "process_guide",
        },
    )

    # Domain check → health_info or END (blocked)
    graph.add_conditional_edges(
        "domain_check",
        _route_domain,
        {
            "health_info": "health_info",
            END: END,
        },
    )

    # Terminal nodes
    graph.add_edge("refuse", END)
    graph.add_edge("health_info", END)
    graph.add_edge("process_guide", END)

    # Booking flow
    graph.add_edge("analyze_symptoms", END)
    graph.add_edge("fetch_clinic", END)
    graph.add_edge("confirm_booking", END)

    return graph.compile()


# Singleton compiled graph
agent_graph = build_graph()
