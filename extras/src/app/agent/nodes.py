import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from app.agent.state import AgentState
from app.agent.tools import (
    search_clinics_by_city,
    search_clinics_by_specialty,
    search_vinmec_process,
    load_vinmec_processes,
    load_clinics,
)
from app.config import get_settings


# ──────────────────────────────────────────────
# Blocked topics & Disclaimers (spec §8)
# ──────────────────────────────────────────────
BLOCKED_TOPICS = [
    "kê đơn thuốc",
    "liều lượng thuốc cụ thể",
    "chẩn đoán bệnh",
    "phẫu thuật nên hay không",
    "so sánh bác sĩ cụ thể",
    "thông tin bệnh nhân khác",
]

DISCLAIMERS = {
    "HIGH": "⚠️ AI chỉ mang tính tham khảo. Vui lòng tham khảo bác sĩ.",
    "MEDIUM": "⚠️ Thông tin này cần bác sĩ xác nhận. Đừng tự chẩn đoán.",
    "LOW": "⚠️ Thông tin này cần bác sĩ xác nhận. Đừng tự chẩn đoán.",
    "out_of_scope": "Tôi chỉ hỗ trợ các câu hỏi liên quan đến y tế Vinmec.",
}

# Danh sách 14 chuyên khoa Vinmec (spec §5)
VINMEC_SPECIALTIES = [
    "Nội tim mạch", "Hô hấp", "Tiêu hóa", "Nội tiết",
    "Thần kinh", "Nội tổng quát", "Nhi", "Sản phụ khoa",
    "Da liễu", "Tai mũi họng", "Mắt", "Cơ xương khớp",
    "Ung bướu", "Thận - Tiết niệu",
]


def _get_llm():
    settings = get_settings()
    return ChatOpenAI(
        model=settings.llm_model,
        openai_api_key=settings.openai_api_key,
        temperature=settings.llm_temperature,
        max_tokens=settings.llm_max_tokens,
    )


# ──────────────────────────────────────────────
# Node 1: Intent Classification (spec §3)
# ──────────────────────────────────────────────
def reasoning_node(state: AgentState) -> dict:
    llm = _get_llm()
    system_prompt = """Bạn là bộ phân loại intent cho Vinmec AI Assistant.
Phân loại câu hỏi của user vào một trong các nhãn sau:
- tu_van_thong_tin: Câu hỏi về kết quả xét nghiệm, chỉ số y khoa, triệu chứng, thuốc, dinh dưỡng y tế
- ho_tro_dat_lich: Muốn đặt lịch khám, mô tả triệu chứng để đặt hẹn bác sĩ, TÌM ĐỊA CHỈ / PHÒNG KHÁM Vinmec, hỏi Vinmec ở đâu, tìm chi nhánh Vinmec
- tu_van_quy_trinh: Hỏi về nhập viện, viện phí, bảo hiểm, xuất viện, quy trình khám
- ngoai_domain: Câu hỏi không liên quan đến y tế hoặc dịch vụ Vinmec

Trả về JSON duy nhất (không markdown, không giải thích):
{
  "intent": "<tu_van_thong_tin | ho_tro_dat_lich | tu_van_quy_trinh | ngoai_domain>",
  "confidence": <0.0 - 1.0>,
  "reasoning": "<giải thích ngắn>"
}

QUAN TRỌNG về confidence:
- confidence KHÔNG phải là độ chắc chắn về phân loại intent
- confidence là MỨC ĐỘ TIN CẬY CỦA CÂU TRẢ LỜI Y KHOA mà AI có thể cung cấp
- Câu hỏi có chỉ số cụ thể (VD: "Glucose 6.8", "huyết áp 140/90") → confidence CAO (0.8-1.0)
- Câu hỏi mô tả triệu chứng mơ hồ (VD: "chóng mặt", "đau đầu", "mệt mỏi") → confidence THẤP (0.3-0.5) vì cần bác sĩ khám trực tiếp
- Câu hỏi về quy trình Vinmec cụ thể → confidence CAO
- Câu hỏi chung chung, không rõ ràng → confidence THẤP"""

    messages = [SystemMessage(content=system_prompt)] + list(state["messages"])
    response = llm.invoke(messages)

    try:
        content = response.content.strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        result = json.loads(content)
        raw_conf = result.get("confidence", 0.5)
        # Map float confidence → HIGH/MEDIUM/LOW (spec §4)
        if raw_conf >= 0.75:
            conf_level = "HIGH"
        elif raw_conf >= 0.50:
            conf_level = "MEDIUM"
        else:
            conf_level = "LOW"
        return {
            "intent": result.get("intent", "ngoai_domain"),
            "confidence": conf_level,
        }
    except (json.JSONDecodeError, AttributeError):
        return {"intent": "tu_van_thong_tin", "confidence": "LOW"}


# ──────────────────────────────────────────────
# Node: Từ chối ngoài domain (spec §4 — 3.1)
# ──────────────────────────────────────────────
def refuse_node(state: AgentState) -> dict:
    msg = DISCLAIMERS["out_of_scope"]
    return {
        "final_response": (
            f"{msg}\n\n"
            "Bạn có thể hỏi tôi về:\n"
            "• Giải thích kết quả xét nghiệm, chỉ số y khoa\n"
            "• Hỗ trợ đặt lịch khám tại Vinmec\n"
            "• Quy trình nhập viện, viện phí, bảo hiểm"
        ),
        "messages": [AIMessage(content=msg)],
    }


# ──────────────────────────────────────────────
# Node: Domain Check (spec §4)
# ──────────────────────────────────────────────
def domain_check_node(state: AgentState) -> dict:
    llm = _get_llm()

    last_msg = _get_last_human_message(state)

    # Check blocked topics first (hard-coded, spec §8)
    msg_lower = last_msg.lower()
    for topic in BLOCKED_TOPICS:
        if topic in msg_lower:
            return {
                "domain_valid": False,
                "final_response": (
                    f"Xin lỗi, tôi không thể hỗ trợ yêu cầu liên quan đến **{topic}**.\n\n"
                    "Vì an toàn sức khỏe của bạn, vui lòng tham khảo trực tiếp bác sĩ "
                    "tại Vinmec hoặc gọi hotline **1900 232 389**."
                ),
                "messages": [AIMessage(content="Từ chối: chủ đề bị chặn.")],
            }

    system_prompt = """Câu hỏi sau có thuộc lĩnh vực y tế hoặc dịch vụ Vinmec không?
Câu hỏi: {query}

Trả về JSON: {{"in_domain": true/false, "reason": "..."}}

Lĩnh vực hợp lệ bao gồm: kết quả xét nghiệm, chỉ số sức khỏe,
triệu chứng bệnh, thuốc, dinh dưỡng y tế, quy trình khám bệnh,
thông tin phòng khám Vinmec, địa chỉ Vinmec, dịch vụ Vinmec.""".format(query=last_msg)

    response = llm.invoke([SystemMessage(content=system_prompt)])

    try:
        content = response.content.strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        result = json.loads(content)
        in_domain = result.get("in_domain", True)
    except (json.JSONDecodeError, AttributeError):
        in_domain = True  # Default: cho phép

    if not in_domain:
        return {
            "domain_valid": False,
            "final_response": DISCLAIMERS["out_of_scope"],
            "messages": [AIMessage(content=DISCLAIMERS["out_of_scope"])],
        }

    return {"domain_valid": True}


# ──────────────────────────────────────────────
# Node: Tư vấn thông tin y tế (spec §4 — Branch 1)
# ──────────────────────────────────────────────
def health_info_node(state: AgentState) -> dict:
    llm = _get_llm()
    confidence = state.get("confidence", "MEDIUM")

    # RAG: tìm quy trình liên quan làm context bổ sung
    last_msg = _get_last_human_message(state)
    rag_context = ""
    processes = search_vinmec_process(last_msg)
    if processes:
        rag_context = "\n\nTài liệu tham khảo:\n" + "\n".join(
            [f"- {p['title']}: {p['content'][:200]}" for p in processes[:3]]
        )

    system_prompt = f"""Bạn là trợ lý y tế AI của Vinmec. Giải thích thông tin y khoa cho bệnh nhân.

NGUYÊN TẮC BẮT BUỘC:
1. Luôn dùng ngôn ngữ đơn giản, dễ hiểu (không dùng thuật ngữ phức tạp)
2. Luôn kèm nguồn tài liệu tham khảo nếu có
3. Luôn thêm disclaimer: "AI chỉ mang tính tham khảo"
4. KHÔNG đưa ra chẩn đoán bệnh
5. KHÔNG kê đơn thuốc
6. Nếu confidence THẤP: hiển thị cảnh báo, khuyên gặp bác sĩ

Confidence level: {confidence}
{rag_context}

Trả lời bằng tiếng Việt."""

    messages = [SystemMessage(content=system_prompt)] + list(state["messages"])
    response = llm.invoke(messages)
    reply = response.content

    # Append disclaimer based on confidence (spec §8)
    disclaimer = DISCLAIMERS.get(confidence, DISCLAIMERS["MEDIUM"])
    if disclaimer not in reply:
        reply += f"\n\n{disclaimer}"

    # Source citation (spec §8)
    reply += "\n\n📄 *Nguồn: Vinmec AI · Tài liệu y khoa tham khảo*"

    return {
        "final_response": reply,
        "messages": [AIMessage(content=reply)],
    }


# ──────────────────────────────────────────────
# Node: Phân tích triệu chứng (spec §5 — 4.1)
# ──────────────────────────────────────────────
def analyze_symptoms_node(state: AgentState) -> dict:
    llm = _get_llm()

    specialties_str = ", ".join(VINMEC_SPECIALTIES)

    system_prompt = f"""Dựa trên triệu chứng sau, hãy gợi ý 2-3 chuyên khoa phù hợp tại Vinmec.

Trả về JSON (không markdown):
{{
  "specialties": [
    {{
      "name": "Tên chuyên khoa",
      "reason": "Lý do phù hợp",
      "priority": 1
    }}
  ],
  "symptoms_summary": "Tóm tắt triệu chứng",
  "urgency": "low | medium | high"
}}

Danh sách chuyên khoa Vinmec: {specialties_str}.
Không markdown, chỉ JSON thuần."""

    messages = [SystemMessage(content=system_prompt)] + list(state["messages"])
    response = llm.invoke(messages)

    try:
        content = response.content.strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        result = json.loads(content)

        symptoms = result.get("symptoms_summary", "")
        specialties = result.get("specialties", [])
        urgency = result.get("urgency", "medium")

        if specialties:
            spec_list = "\n".join(
                [f"  {i+1}. **{s['name']}** — {s['reason']}" for i, s in enumerate(specialties)]
            )
            reply = (
                f"Tôi hiểu bạn đang gặp triệu chứng: **{symptoms}**\n\n"
                f"Tôi đề xuất các chuyên khoa phù hợp:\n{spec_list}\n\n"
                f"Bạn muốn đặt lịch khám chuyên khoa nào? Vui lòng cho tôi biết:\n"
                f"1. Họ tên\n2. Số điện thoại\n3. Thành phố (để tìm Vinmec gần nhất)\n4. Ngày giờ mong muốn"
            )
        else:
            reply = (
                f"Tôi hiểu bạn đang gặp triệu chứng: **{symptoms}**\n\n"
                f"Để tư vấn chính xác hơn, bạn vui lòng cho biết thêm chi tiết triệu chứng?"
            )

        if urgency == "high":
            reply = "🚨 **Triệu chứng có dấu hiệu nghiêm trọng.** Nếu đang trong tình trạng cấp cứu, vui lòng gọi **115** hoặc đến phòng cấp cứu Vinmec gần nhất.\n\n" + reply

        return {
            "symptoms": symptoms,
            "final_response": reply,
            "needs_user_confirmation": True,
            "messages": [AIMessage(content=reply)],
        }
    except (json.JSONDecodeError, AttributeError):
        reply = "Bạn có thể mô tả chi tiết hơn triệu chứng để tôi hỗ trợ tốt hơn không?"
        return {
            "final_response": reply,
            "needs_user_confirmation": True,
            "messages": [AIMessage(content=reply)],
        }


# ──────────────────────────────────────────────
# Node: Tìm phòng khám & xử lý đặt lịch (spec §5 — 4.2)
# ──────────────────────────────────────────────
def fetch_clinic_node(state: AgentState) -> dict:
    llm = _get_llm()

    system_prompt = """Bạn là trợ lý đặt lịch khám Vinmec. Dựa vào thông tin người dùng cung cấp trong cuộc hội thoại, trích xuất JSON:
{
  "patient_name": "<họ tên hoặc null>",
  "patient_phone": "<số điện thoại hoặc null>",
  "city": "<thành phố hoặc null>",
  "appointment_date": "<ngày khám hoặc null>",
  "appointment_time": "<giờ khám hoặc null>",
  "specialty": "<chuyên khoa hoặc null>",
  "query_type": "<booking hoặc location>"
}
Nếu user chỉ hỏi địa chỉ/phòng khám/chi nhánh Vinmec mà KHÔNG muốn đặt lịch, đặt query_type = "location".
Nếu user muốn đặt lịch khám, đặt query_type = "booking".
Không markdown, chỉ JSON thuần."""

    messages = [SystemMessage(content=system_prompt)] + list(state["messages"])
    response = llm.invoke(messages)

    try:
        content = response.content.strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        info = json.loads(content)
    except (json.JSONDecodeError, AttributeError):
        info = {}

    city = info.get("city")
    specialty = info.get("specialty")
    query_type = info.get("query_type", "booking")

    # Tìm phòng khám phù hợp
    clinics = []
    if city:
        clinics = search_clinics_by_city(city)
    if not clinics and specialty:
        clinics = search_clinics_by_specialty(specialty)

    # ── Location-only query: chỉ trả địa chỉ, không cần booking info ──
    if query_type == "location":
        if clinics:
            clinic_list = "\n".join(
                [f"  - **{c['name']}** — {c['address']}, {c['city']} (📞 {c['phone']})" for c in clinics[:5]]
            )
            reply = (
                f"Các phòng khám Vinmec tại **{city or 'gần bạn'}**:\n{clinic_list}\n\n"
                f"Bạn có muốn đặt lịch khám tại một trong các phòng khám trên không?"
            )
        else:
            all_clinics = load_clinics()
            clinic_list = "\n".join(
                [f"  - **{c['name']}** — {c['address']}, {c['city']} (📞 {c['phone']})" for c in all_clinics[:5]]
            )
            reply = (
                f"Xin lỗi, tôi không tìm thấy Vinmec tại **{city}**. "
                f"Dưới đây là một số phòng khám Vinmec khác:\n{clinic_list}"
            )
        return {
            "final_response": reply,
            "clinic_results": [_clinic_summary(c) for c in clinics[:5]],
            "messages": [AIMessage(content=reply)],
        }

    # ── Booking query: cần đầy đủ thông tin ──
    missing = []
    if not info.get("patient_name"):
        missing.append("họ tên")
    if not info.get("patient_phone"):
        missing.append("số điện thoại")
    if not city:
        missing.append("thành phố")
    if not info.get("appointment_date"):
        missing.append("ngày khám")
    if not info.get("appointment_time"):
        missing.append("giờ khám")

    if missing:
        reply = f"Để đặt lịch, tôi cần thêm thông tin: **{', '.join(missing)}**. Bạn vui lòng cung cấp nhé!"
        return {
            "final_response": reply,
            "needs_user_confirmation": True,
            "clinic_results": [_clinic_summary(c) for c in clinics[:3]],
            "messages": [AIMessage(content=reply)],
        }

    if not clinics:
        reply = f"Xin lỗi, tôi không tìm thấy phòng khám Vinmec tại **{city}**. Bạn có muốn tìm ở thành phố khác không?"
        return {
            "final_response": reply,
            "needs_user_confirmation": True,
            "messages": [AIMessage(content=reply)],
        }

    chosen = clinics[0]
    booking_data = {
        "patient_name": info["patient_name"],
        "patient_phone": info["patient_phone"],
        "symptoms": state.get("symptoms") or "",
        "clinic_id": chosen["id"],
        "clinic_name": chosen["name"],
        "specialty": specialty or "",
        "appointment_date": info["appointment_date"],
        "appointment_time": info["appointment_time"],
        "source": "ai_assistant",
    }

    clinic_list = "\n".join(
        [f"  - **{c['name']}** — {c['address']}, {c['city']} (📞 {c['phone']})" for c in clinics[:3]]
    )

    reply = (
        f"Tôi tìm thấy các phòng khám Vinmec gần bạn:\n{clinic_list}\n\n"
        f"📋 **Thông tin đặt lịch:**\n"
        f"  - Bệnh nhân: {info['patient_name']}\n"
        f"  - SĐT: {info['patient_phone']}\n"
        f"  - Chuyên khoa: {specialty}\n"
        f"  - Phòng khám: {chosen['name']}\n"
        f"  - Ngày: {info['appointment_date']}\n"
        f"  - Giờ: {info['appointment_time']}\n\n"
        f"Bạn xác nhận đặt lịch này không? (Có/Không)"
    )

    return {
        "final_response": reply,
        "booking_data": booking_data,
        "clinic_results": [_clinic_summary(c) for c in clinics[:3]],
        "needs_user_confirmation": True,
        "messages": [AIMessage(content=reply)],
    }


# ──────────────────────────────────────────────
# Node: Xác nhận và lưu booking (spec §5 — 4.3)
# ──────────────────────────────────────────────
def confirm_booking_node(state: AgentState) -> dict:
    booking = state.get("booking_data")
    if not booking:
        return {
            "final_response": "Chưa có thông tin đặt lịch. Bạn muốn đặt lịch khám không?",
            "messages": [AIMessage(content="Chưa có thông tin đặt lịch.")],
        }

    reply = (
        f"✅ **Đặt lịch thành công!**\n\n"
        f"  - Bệnh nhân: {booking['patient_name']}\n"
        f"  - Phòng khám: {booking['clinic_name']}\n"
        f"  - Chuyên khoa: {booking.get('specialty', 'N/A')}\n"
        f"  - Ngày: {booking['appointment_date']}\n"
        f"  - Giờ: {booking['appointment_time']}\n\n"
        f"Vui lòng đến trước giờ hẹn 15-30 phút để hoàn tất thủ tục đăng ký.\n"
        f"Mang theo CMND/CCCD và thẻ BHYT (nếu có).\n\n"
        f"📞 Nếu cần hỗ trợ, gọi hotline **1900 232 389**."
    )

    return {
        "final_response": reply,
        "booking_confirmed": True,
        "messages": [AIMessage(content=reply)],
    }


# ──────────────────────────────────────────────
# Node: Tư vấn quy trình Vinmec (spec §6 — Branch 3)
# ──────────────────────────────────────────────
def process_guide_node(state: AgentState) -> dict:
    llm = _get_llm()

    last_msg = _get_last_human_message(state)

    processes = search_vinmec_process(last_msg)
    if not processes:
        keywords = ["nhập viện", "xuất viện", "viện phí", "bảo hiểm", "khám tổng quát", "đặt lịch"]
        for kw in keywords:
            if kw in last_msg.lower():
                processes = search_vinmec_process(kw)
                break

    if processes:
        context = "\n\n---\n\n".join(
            [f"**{p['title']}**\n{p['content']}" for p in processes]
        )
        system_prompt = f"""Bạn là trợ lý Vinmec. Dựa vào thông tin quy trình dưới đây, hãy hướng dẫn bệnh nhân từng bước cụ thể, rõ ràng và thân thiện.

THÔNG TIN QUY TRÌNH:
{context}

NGUYÊN TẮC:
- Trình bày từng bước rõ ràng, đánh số thứ tự
- Nêu giấy tờ cần thiết nếu có
- Nêu thời gian ước tính nếu biết
- Trả lời bằng tiếng Việt, ngắn gọn, dễ hiểu
- Nếu cần thêm thông tin, hướng dẫn gọi hotline 1900 232 389"""
    else:
        all_procs = "\n\n---\n\n".join(
            [f"**{p['title']}**\n{p['content']}" for p in load_vinmec_processes()]
        )
        system_prompt = f"""Bạn là trợ lý Vinmec. Dưới đây là tất cả quy trình có sẵn. Hãy trả lời câu hỏi bệnh nhân dựa trên thông tin phù hợp nhất.

{all_procs}

Nếu không có quy trình phù hợp, hướng dẫn bệnh nhân gọi hotline 1900 232 389.
Trả lời bằng tiếng Việt."""

    messages = [SystemMessage(content=system_prompt)] + list(state["messages"])
    response = llm.invoke(messages)

    reply = response.content
    reply += "\n\n📄 *Nguồn: Vinmec AI · Cơ sở dữ liệu quy trình Vinmec*"

    return {
        "final_response": reply,
        "messages": [AIMessage(content=reply)],
    }


# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────
def _get_last_human_message(state: AgentState) -> str:
    for m in reversed(state["messages"]):
        if hasattr(m, "content") and (not hasattr(m, "type") or m.type == "human"):
            return m.content
    return ""


def _clinic_summary(clinic: dict) -> dict:
    return {
        "id": clinic["id"],
        "name": clinic["name"],
        "address": f"{clinic['address']}, {clinic['city']}",
        "phone": clinic["phone"],
        "specialties": clinic["specialties"],
    }
