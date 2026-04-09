**Nhóm:** 13
**Track:** ☐ VinFast · ☑ Vinmec · ☐ VinUni-VinSchool · ☐ XanhSM · ☐ Open

**Problem statement (1 câu):** 
*Bệnh nhân thường gặp khó khăn khi hiểu kết quả khám, đặt lịch tái khám và chuẩn bị trước khi đến bệnh viện; AI giúp giải thích thông tin y khoa, nhắc lịch và hướng dẫn bệnh nhân rõ ràng hơn.*

---

# 1. AI Product Canvas *(Nguyễn Tuấn Kiệt - 2A202600232)*

|             | Value                                                                                                                                                | Trust                                                                                                                           | Feasibility                                                                        |
| ----------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| **Câu hỏi** | User nào? Pain gì? AI giải gì?                                                                                                                       | Khi AI sai thì sao? User sửa bằng cách nào?                                                                                     | Cost/latency bao nhiêu? Risk chính?                                                |
| **Trả lời** | *Bệnh nhân. Pain: Không hiểu kết quả khám, quên lịch tái khám, không biết chuẩn bị gì. AI: Giải thích kết quả, nhắc lịch, hướng dẫn trước khi khám.* | *AI sai → Bệnh nhân xem nguồn từ tài liệu chính thức của Vinmec hoặc hỏi lại bác sĩ. Có cảnh báo "AI chỉ mang tính tham khảo".* | *~$0.02/user, latency < 3s. Risk: Giải thích sai thông tin y khoa, gây hiểu nhầm.* |

**Automation hay augmentation?**
☐ Automation · ☑ Augmentation

**Justify:**
*AI hỗ trợ bệnh nhân hiểu thông tin, nhưng quyết định y khoa vẫn thuộc về bác sĩ.*

---

### Learning signal

**1. User correction đi vào đâu?**
___ Feedback của bệnh nhân lưu vào database để cải thiện model giải thích.

**2. Product thu signal gì để biết tốt lên hay tệ đi?**
___ Tỷ lệ bệnh nhân đọc xong hiểu (thumb up/down), số lần hỏi lại cùng một câu hỏi.

**3. Data thuộc loại nào?**
☐ User-specific · ☑ Domain-specific · ☑ Human-judgment · ☐ Real-time · ☐ Khác: ___

**Có marginal value không?**
___ Có. Feedback từ bệnh nhân giúp AI hiểu cách diễn đạt dễ hiểu hơn với người không chuyên.

---

# 2. User Stories — 4 paths *(Mã Khoa Học - 2A202600474 + Nguyễn Hữu Nam - 2A202600397)*

### Feature: *Tư vấn bệnh nhân*

**Trigger:**
*Chatbot tự reasoning khi user hỏi về chỉ số xét nghiệm, hoặc thông tin y khoa*

| Path                           | Câu hỏi thiết kế                                           | Mô tả                                                                           |
| ------------------------------ | ---------------------------------------------------------- | ------------------------------------------------------------------------------- |
| Happy — AI đúng, tự tin        | User thấy gì? Flow kết thúc ra sao?                        | *AI giải thích chỉ số/xét nghiệm rõ ràng, dễ hiểu. User hiểu và yên tâm.*       |
| Low-confidence — AI không chắc | System báo "không chắc" bằng cách nào? User quyết thế nào? | *AI hiển thị cảnh báo "Thông tin cần bác sĩ xác nhận" và gợi ý liên hệ bác sĩ.* |

### Feature: *Hỗ trợ đặt lịch*

**Trigger:**
*Chatbot tự reasoning khi user hỏi về triệu chứng và thể hiện nhu cầu đặt lịch khám (vd: "tôi muốn khám", "đặt lịch giúp tôi")*

| Path                           | Câu hỏi thiết kế                                           | Mô tả                                                                                                   |
| ------------------------------ | ---------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| Happy — AI đúng, tự tin        | User thấy gì? Flow kết thúc ra sao?                        | *AI vừa tư vấn sơ bộ triệu chứng, vừa chủ động đề xuất đặt lịch với chuyên khoa phù hợp. Thu thập địa điểm, thời gian → đưa lịch để user xác nhận.*    |
| Low-confidence — AI không chắc | System báo "không chắc" bằng cách nào? User quyết thế nào? | *AI không chắc về mức độ nghiêm trọng hoặc chuyên khoa → hỏi thêm (triệu chứng chi tiết, thời gian bị) trước khi đề xuất đặt lịch.*                         |
| Failure — AI sai               | User biết AI sai bằng cách nào? Recover ra sao?            | *AI hiểu sai địa chỉ user, đề xuất phòng khám không phù hợp. User nhận ra qua thông tin hiển thị và không tiếp tục.*               |
| Correction — user sửa          | User sửa bằng cách nào? Data đó đi vào đâu?                | *User chỉnh lại địa chỉ. Hệ thống lưu để cải thiện mapping vị trí và đề xuất phòng khám chính xác hơn.* |

### Feature: *Tư vấn quy trình*

**Trigger:**
*Chatbot tự reasoning khi user hỏi về quy trình khám, nhập viện, viện phí hoặc thủ tục*

| Path                           | Câu hỏi thiết kế                                           | Mô tả                                                                                            |
| ------------------------------ | ---------------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| Happy — AI đúng, tự tin        | User thấy gì? Flow kết thúc ra sao?                        | *AI hướng dẫn từng bước quy trình (đăng ký, khám, xét nghiệm, thanh toán) rõ ràng.*              |
| Low-confidence — AI không chắc | System báo "không chắc" bằng cách nào? User quyết thế nào? | *AI yêu cầu thêm thông tin (loại dịch vụ, bảo hiểm, cơ sở cụ thể) trước khi hướng dẫn chi tiết.* |

---

# 3. Eval metrics + threshold *(Hà Việt Khánh - 2A202600055)*

**Optimize precision hay recall?**
☑ Precision · ☐ Recall

**Tại sao?**
*Trong y tế, thông tin sai có thể gây hoang mang cho bệnh nhân.*

| Metric                       | Threshold | Red flag (dừng khi) |
| ---------------------------- | --------- | ------------------- |
| *Accuracy (giải thích đúng)* | *≥90%*    | *< 80%*             |
| *User satisfaction*          | *≥80%*    | *< 60%*             |
| *Latency*                    | *< 3s*    | *> 8s*              |

---



---

# 5. ROI 3 kịch bản *(Nguyễn Việt Trung - 2A202600244)*

|                | Conservative         | Realistic                  | Optimistic                        |
| -------------- | -------------------- | -------------------------- | --------------------------------- |
| **Assumption** | *100 bệnh nhân/ngày* | *500 bệnh nhân/ngày*       | *Toàn bộ Vinmec*                  |
| **Cost**       | *$10/ngày*           | *$50/ngày*                 | *$200/ngày*                       |
| **Benefit**    | *Giảm tải CSKH*      | *Giảm 20% cuộc gọi hỗ trợ* | *Cải thiện trải nghiệm bệnh nhân* |
| **Net**        | *Hòa vốn*            | *ROI 2x*                   | *ROI 5x*                          |

**Kill criteria:**
*Dừng dự án nếu bệnh nhân đánh giá tiêu cực > 40%*

---
