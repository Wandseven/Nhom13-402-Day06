from langchain.tools import tool
# MOCK DATABASE
PATIENT_DATA = [
  {"patient_id": "VM001", "result": "Viêm họng cấp", "appointment_date": "2026-04-20"},
  {"patient_id": "VM002", "result": "Đau dạ dày nhẹ", "appointment_date": "2026-04-25"},
  {"patient_id": "VM003", "result": "Tăng huyết áp độ 1", "appointment_date": "2026-05-10"},
  {"patient_id": "VM004", "result": "Khám sức khỏe tổng quát - Bình thường", "appointment_date": None},
  {"patient_id": "VM005", "result": "Viêm xoang", "appointment_date": "2026-04-18"},
  {"patient_id": "VM006", "result": "Đau lưng cơ học", "appointment_date": "2026-04-30"},
  {"patient_id": "VM007", "result": "Tiểu đường type 2", "appointment_date": "2026-05-05"},
  {"patient_id": "VM008", "result": "Cảm cúm thông thường", "appointment_date": None},
  {"patient_id": "VM009", "result": "Thiếu máu nhẹ", "appointment_date": "2026-04-22"},
  {"patient_id": "VM010", "result": "Viêm phế quản", "appointment_date": "2026-04-28"},
  {"patient_id": "VM011", "result": "Dị ứng thời tiết", "appointment_date": None},
  {"patient_id": "VM012", "result": "Đau nửa đầu migraine", "appointment_date": "2026-05-12"},
  {"patient_id": "VM013", "result": "Viêm tai giữa", "appointment_date": "2026-04-21"},
  {"patient_id": "VM014", "result": "Khám tim mạch định kỳ", "appointment_date": "2026-05-15"},
  {"patient_id": "VM015", "result": "Rối loạn tiêu hóa", "appointment_date": "2026-04-19"},
  {"patient_id": "VM016", "result": "Đau khớp gối", "appointment_date": "2026-05-01"},
  {"patient_id": "VM017", "result": "Sốt siêu vi", "appointment_date": None},
  {"patient_id": "VM018", "result": "Viêm da dị ứng", "appointment_date": "2026-04-27"},
  {"patient_id": "VM019", "result": "Cao huyết áp", "appointment_date": "2026-05-08"},
  {"patient_id": "VM020", "result": "Khám thai định kỳ", "appointment_date": "2026-04-23"},
  {"patient_id": "VM021", "result": "Đau vai gáy", "appointment_date": "2026-04-29"},
  {"patient_id": "VM022", "result": "Viêm amidan", "appointment_date": "2026-04-26"},
  {"patient_id": "VM023", "result": "Khám tổng quát - Bình thường", "appointment_date": None},
  {"patient_id": "VM024", "result": "Gan nhiễm mỡ độ 1", "appointment_date": "2026-05-14"},
  {"patient_id": "VM025", "result": "Đau dạ dày mãn tính", "appointment_date": "2026-05-20"},
  {"patient_id": "VM026", "result": "Rối loạn tiền đình", "appointment_date": "2026-04-24"},
  {"patient_id": "VM027", "result": "Viêm họng mãn tính", "appointment_date": "2026-05-02"},
  {"patient_id": "VM028", "result": "Thiếu vitamin D", "appointment_date": None},
  {"patient_id": "VM029", "result": "Khám hậu COVID", "appointment_date": "2026-04-30"},
  {"patient_id": "VM030", "result": "Đau thần kinh tọa", "appointment_date": "2026-05-18"}
]




@tool
def check_date_of_next_appointment(patient_id: str) -> str:
    """Kiểm tra trong database và trả về lịch tái khám nếu có"""

    patient_id = patient_id.strip().upper() 
    for patient in PATIENT_DATA:
        if patient["patient_id"] == patient_id:
            if patient["appointment_date"]:
                return f"Lịch tái khám của bạn là vào {patient['appointment_date']}"
            else:
                return "Bạn chưa có lịch tái khám nào."
    return "Không tìm thấy thông tin bệnh nhân."

@tool 
def book_appointment(patient_id: str, date_time: str) -> str:
    """Đặt lịch tái khám mới cho bệnh nhân, cập nhật vào database và trả về xác nhận"""

    patient_id = patient_id.strip().upper()  
    for patient in PATIENT_DATA:
        if patient["patient_id"] == patient_id:
            patient["appointment_date"] = date_time
            break
    return f"Lịch tái khám của bạn đã được đặt vào {date_time}"

@tool
def cancel_appointment(patient_id: str) -> str:
    """Hủy lịch tái khám hiện tại của bệnh nhân, cập nhật vào database và trả về xác nhận"""

    patient_id = patient_id.strip().upper()  
    for patient in PATIENT_DATA:
        if patient["patient_id"] == patient_id:
            patient["appointment_date"] = None
            break
    return "Lịch tái khám của bạn đã được hủy bỏ."

@tool 
def get_diagnosis(patient_id: str) -> str:
    """Giải thích kết quả chẩn đoán của bệnh nhân dựa trên database"""

    patient_id = patient_id.strip().upper()  
    for patient in PATIENT_DATA:
        if patient["patient_id"] == patient_id:
            return f"Kết quả chẩn đoán của bạn là: {patient['result']}"
    return "Không tìm thấy thông tin bệnh nhân."
