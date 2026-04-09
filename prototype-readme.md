# Prototype — Vinmec AI chatbot

## Mô tả
Chatbot tư vấn bệnh nhân, trả lời giải đáp các thông số y khoa, hỗ trợ bệnh nhân đặt lịch khám theo khu vực và tư vấn giải đáp các quy trình phức tạp như nhập viện, bảo hiểm,...

## Level: Working prototype
- UI build bằng Claude sonnet 4.6
- 1 demo chính chạy thật với OpenAI API: nhập thông tin/yêu cầu -> tư vấn/đặt lịch/giải đáp

## Links
- Prototype:
- Video demo (backup): https://drive.google.com/file/d/1aJbyE7A1mWFVYHVGiz8SexhHunW-jqAR/view?usp=drive_link

## Tools
- UI: Claude sonnet 4.6 gen từ workflow + screenshot app Vinmec
- AI: Call API model GPT-4o
- Prompt: system prompt + one-shot example

## Phân công
| Thành viên | Phần | Output |
|-----------|------|--------|
| Nguyễn Tuấn Kiệt | AI Canvas + Sketch | spec-final.md phần 1 |
| Mã Khoa Học  | User stories 4 paths 2 feature + slide | spec-final.md phần 2, demo_slides.pdf |
| Nguyễn Hữu Nam | User stories 4 paths 1 feature | spec-final.md phần 2 |
| Nguyễn Việt Trung | ROI 3 kịch bản + mock prototype | spec-final.md phần 5 |
| Trần Ngô Hồng Hà | failure modes + Mini AI spec | spec-final.md phần 4 + 6 |
| Hà Việt Khánh | Eval metrics + threshold | spec-final.md phần 3 |