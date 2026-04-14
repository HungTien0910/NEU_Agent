# NEU Data Query System

Hệ thống truy vấn dữ liệu học vụ theo dạng chat cho NEU, gồm:
- `frontend` (Nuxt 3): giao diện Admin/User.
- `backend` (FastAPI): API xác thực, phân quyền, import dữ liệu, truy vấn.
- `ai_core` (Python): phân loại intent, sinh Cypher, tóm tắt kết quả.
- `docker-compose.yml`: chạy full stack (PostgreSQL, Neo4j, Redis, Backend, Frontend).

## Kiến trúc tổng quan

- Frontend gọi API backend qua `NUXT_PUBLIC_API_BASE`.
- Backend xử lý auth/quyền, đọc dữ liệu từ PostgreSQL + Neo4j.
- Backend gọi AI Core để chuyển câu hỏi tự nhiên -> Cypher và summary.
- Redis dùng cho cache/context/rate-limit (tùy luồng xử lý).

## Cấu trúc thư mục

```text
neu_agent/
├── ai_core/
├── backend/
├── frontend/
├── data/
├── docs/
├── figma_redesign/
└── docker-compose.yml
```

## Yêu cầu môi trường

- Docker + Docker Compose
- Python 3.10+ (khuyến nghị)
- Node.js 18+ và npm

## Chạy nhanh (Local Dev)

### 1) Khởi động toàn bộ services bằng Docker Compose

Từ thư mục root:

```bash
docker compose up -d --build
```

Service mặc định:
- PostgreSQL: `localhost:55432`
- Neo4j HTTP: `localhost:17474`
- Neo4j Bolt: `localhost:17687`
- Redis: `localhost:16379`
- Backend API: `http://localhost:1111`
- Frontend: `http://localhost:3003`

Nếu cần truyền biến môi trường cho backend/frontend khi chạy compose:

```bash
OPENAI_API_KEY=... OPENAI_MODEL=gpt-4o docker compose up -d --build
```

### 2) Chạy backend/frontend riêng lẻ (tuỳ chọn - local dev)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 1111 --reload
```

Backend đọc biến môi trường từ `backend/.env`.

Biến quan trọng:
- `pg_dsn`
- `neo4j_uri`, `neo4j_user`, `neo4j_password`
- `redis_url`
- `openai_api_key`, `openai_model`
- SMTP: `smtp_host`, `smtp_port`, `smtp_user`, `smtp_password`, ...

### 3) Chạy frontend (Nuxt 3)

```bash
cd frontend
npm install
npm run dev
```

Frontend mặc định chạy ở `http://localhost:3003`.

Thiết lập API backend:

```bash
# frontend/.env
NUXT_PUBLIC_API_BASE=http://localhost:1111
```

## Dữ liệu mẫu

File dữ liệu mẫu đặt tại:

`data/university_mock_academic_student_5000.xlsx`

## Ghi chú

- Thư mục `data/postgres`, `data/neo4j`, `data/redis` là volume runtime local.
- Log chạy nền có thể nằm trong `nohup/`.
- Các artifact build/cache đã được ignore trong `.gitignore`.
