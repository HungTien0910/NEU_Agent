# Backend (Python / FastAPI)

Mục tiêu:
- Auth + phân quyền (PostgreSQL)
- API query dữ liệu (Neo4j)
- Import/validate Excel
- Logs + settings

## Thư mục chính
- `app/main.py`: FastAPI entry
- `app/api/routers/`: route modules
- `app/core/`: config + permission
- `app/db/`: Neo4j + PostgreSQL clients
- `app/services/`: business logic
- `app/schemas/`: Pydantic schemas
- `app/models/`: SQLAlchemy models

## Quyền theo sheet
- `data:student`, `data:course`, `data:lecturer`, `data:academic`

User không có quyền sẽ nhận phản hồi: **không có quyền truy cập dữ liệu**.
