import unittest
from Group_13_Spec_day5VinAi.src.tools import (
    check_date_of_next_appointment,
    book_appointment,
    cancel_appointment,
    get_diagnosis,
    PATIENT_DATA
)
import copy

class TestTools(unittest.TestCase):
    def setUp(self):
        # Sao lưu dữ liệu gốc để reset sau mỗi test
        self.original_data = copy.deepcopy(PATIENT_DATA)
        print(f"SetUp: VM001 appointment: {next(p for p in PATIENT_DATA if p['patient_id'] == 'VM001')['appointment_date']}, id: {id(PATIENT_DATA)}")

    def tearDown(self):
        # Reset dữ liệu về trạng thái ban đầu
        global PATIENT_DATA
        PATIENT_DATA = self.original_data
        print(f"TearDown: VM001 appointment: {next(p for p in PATIENT_DATA if p['patient_id'] == 'VM001')['appointment_date']}, id: {id(PATIENT_DATA)}")

    # def test_check_date_of_next_appointment_with_appointment(self):
    #     # Test với bệnh nhân có lịch tái khám
    #     expected = "Lịch tái khám của bạn là vào 2026-04-20"
    #     result = check_date_of_next_appointment.invoke({"patient_id": "VM001"})
    #     print(f"Result: {result}, Expected: {expected}")
    #     self.assertEqual(result, expected)

    # def test_check_date_of_next_appointment_without_appointment(self):
    #     # Test với bệnh nhân không có lịch tái khám
    #     result = check_date_of_next_appointment.invoke({"patient_id": "VM011"})
    #     expected = "Bạn chưa có lịch tái khám nào."
    #     self.assertEqual(result, expected)

    # def test_check_date_of_next_appointment_not_found(self):
    #     # Test với bệnh nhân không tồn tại
    #     result = check_date_of_next_appointment.invoke({"patient_id": "VM999"})
    #     expected = "Không tìm thấy thông tin bệnh nhân."
    #     self.assertEqual(result, expected)

    # def test_book_appointment(self):
    #     # Test đặt lịch tái khám
    #     result = book_appointment.invoke({"patient_id": "VM004", "date_time": "2026-06-01"})
    #     expected = "Lịch tái khám của bạn đã được đặt vào 2026-06-01"
    #     self.assertEqual(result, expected)
    #     # Kiểm tra dữ liệu đã được cập nhật
    #     patient = next(p for p in PATIENT_DATA if p["patient_id"] == "VM004")
    #     self.assertEqual(patient["appointment_date"], "2026-06-01")        

    
    # def test_cancel_appointment(self):
    #     # Test hủy lịch tái khám
    #     result = cancel_appointment.invoke({"patient_id": "VM001"})
    #     expected = "Lịch tái khám của bạn đã được hủy bỏ."
    #     self.assertEqual(result, expected)
    #     # Kiểm tra dữ liệu đã được cập nhật
    #     patient = next(p for p in PATIENT_DATA if p["patient_id"] == "VM001")
    #     print(f"After cancel: {patient['appointment_date']}")
    #     self.assertIsNone(patient["appointment_date"])

    def test_explain_diagnosis_found(self):
        # Test giải thích chẩn đoán với bệnh nhân tồn tại
        result = get_diagnosis.invoke({"patient_id": "VM001"})
        expected = "Kết quả chẩn đoán của bạn là: Viêm họng cấp"
        self.assertEqual(result, expected)

    def test_explain_diagnosis_not_found(self):
        # Test giải thích chẩn đoán với bệnh nhân không tồn tại
        result = get_diagnosis.invoke({"patient_id": "VM999"})
        expected = "Không tìm thấy thông tin bệnh nhân."
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()