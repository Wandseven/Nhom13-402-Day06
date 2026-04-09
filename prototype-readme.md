# Prototype — Vinmec AI chatbot

## Mô tả
Chatbot tư vấn bệnh nhân, trả lời giải đáp các thông số y khoa, hỗ trợ bệnh nhân đặt lịch khám theo khu vực và tư vấn giải đáp các quy trình phức tạp như nhập viện, bảo hiểm,...

## Level: Working prototype
- UI build bằng Claude sonnet 4.6
- 1 demo chính chạy thật với OpenAI API: nhập thông tin/yêu cầu -> tư vấn/đặt lịch/giải đáp

## Links
- Prototype: https://github.com/Wandseven/Nhom13-402-Day06
- Video demo (backup): https://drive.google.com/file/d/1aJbyE7A1mWFVYHVGiz8SexhHunW-jqAR/view?usp=drive_link

## Tools
- UI: Claude sonnet 4.6 gen từ workflow + screenshot app Vinmec
- AI: Call API model GPT-4o
- Prompt: system prompt + one-shot example

## Phân công
| Thành viên | Phần | Output |
|-----------|------|--------|
| Nguyễn Tuấn Kiệt | AI Canvas + Sketch + tools | spec-final.md phần 1, app/agent/tools |
| Mã Khoa Học  | User stories 4 paths 2 feature + slide + workflow design + testing | spec-final.md phần 2, demo_slides.pdf |
| Nguyễn Hữu Nam | User stories 4 paths 1 feature + agent logic | spec-final.md phần 2, app/agent |
| Nguyễn Việt Trung | ROI 3 kịch bản + mock prototype + frontend | spec-final.md phần 5, static, mock_v4.html |
| Trần Ngô Hồng Hà | failure modes + Mini AI spec + API + service | spec-final.md phần 4 + 6, app/api, services |
| Hà Việt Khánh | Eval metrics + threshold + database | spec-final.md phần 3, app/db, model, schema |