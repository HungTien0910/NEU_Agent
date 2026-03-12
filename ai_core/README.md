# AI Core

Mục tiêu:
- Nhận câu hỏi → sinh Cypher hợp lệ
- Kiểm tra quyền theo sheet
- Gợi ý biểu đồ
- Trả về bảng + biểu đồ + summary
- Ưu tiên rule-based, fallback sang AI khi cần
- Câu hỏi thường trả lời như chatbot

## Cấu trúc
- `prompts/`: system prompts cho data/chat
- `templates/`: schema graph + response format JSON
- `utils/`: helper đọc file, xử lý text

## Env
- `OPENAI_API_KEY`
- `OPENAI_MODEL=gpt-4o`
