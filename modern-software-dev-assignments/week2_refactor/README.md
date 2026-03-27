# Action Item Extractor

API web trích xuất action items từ ghi chú văn bản, hỗ trợ cả phương pháp heuristic (rule-based) và LLM qua Ollama.

---

## Tổng quan dự án

**Action Item Extractor** là ứng dụng FastAPI cho phép:

- **Trích xuất action items** từ văn bản ghi chú bằng hai phương pháp:
  - **Rule-based**: Phát hiện bullet (`-`, `*`, `•`, `1.`), checkbox (`[ ]`, `[todo]`), và các từ khóa (`todo:`, `action:`, `next:`)
  - **LLM (Ollama)**: Gửi ghi chú lên mô hình Ollama để phân tích và trả về JSON array các action items
- **Quản lý Notes**: Lưu và truy xuất ghi chú gốc
- **Quản lý Action Items**: Liệt kê, đánh dấu hoàn thành, lọc theo note

### Cấu trúc thư mục

```
week2_refactor/
├── app/
│   ├── main.py          # Điểm vào FastAPI, lifespan, route gốc
│   ├── db.py            # SQLite CRUD (notes, action_items)
│   ├── schemas.py       # Pydantic models
│   ├── settings.py      # Biến môi trường (DB, Ollama)
│   ├── routers/
│   │   ├── action_items.py   # /action-items/* 
│   │   └── notes.py         # /notes/*
│   └── services/
│       └── extract.py   # Rule-based và LLM extractors
├── frontend/
│   └── index.html       # Giao diện HTML đơn giản
├── tests/
│   └── __init__.py
└── data/                # SQLite DB (tự tạo)
    └── app.db
```

---

## Cài đặt / Thiết lập

### Yêu cầu

- Python 3.10+
- [Ollama](https://ollama.ai/) (chỉ khi dùng tính năng Extract LLM)

### 1. Cài đặt phụ thuộc

Dự án nằm trong repo dùng Poetry. Cài từ thư mục gốc:

```bash
cd modern-software-dev-assignments
poetry install
```

Hoặc cài thủ công với pip:

```bash
pip install fastapi uvicorn pydantic requests
```

### 2. (Tùy chọn) Cấu hình Ollama

Nếu dùng Extract LLM, cần Ollama chạy sẵn. Biến môi trường:

| Biến | Mô tả | Mặc định |
|------|-------|----------|
| `OLLAMA_HOST` | URL Ollama | `http://localhost:11434` |
| `OLLAMA_MODEL` | Model Ollama | `llama3.2:3b` |
| `OLLAMA_TIMEOUT_SEC` | Timeout (giây) | `60` |

### 3. (Tùy chọn) Đường dẫn cơ sở dữ liệu

| Biến | Mô tả | Mặc định |
|------|-------|----------|
| `WEEK2_DB_PATH` | Đường dẫn file SQLite | `./data/app.db` |

---

## Chạy máy chủ

Từ thư mục `week2_refactor`:

```bash
cd week2_refactor
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Hoặc với Poetry:

```bash
cd modern-software-dev-assignments
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Sau khi chạy:

- Web UI: [http://localhost:8000](http://localhost:8000)
- Swagger: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## API Endpoints

### Notes

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| `POST` | `/notes/` | Tạo note mới |
| `GET` | `/notes/` | Liệt kê tất cả notes |
| `GET` | `/notes/{note_id}` | Lấy một note theo ID |

#### Ví dụ

**Tạo note**

```bash
curl -X POST http://localhost:8000/notes/ \
  -H "Content-Type: application/json" \
  -d '{"content": "Meeting notes:\n- Review PR\n- Deploy to staging"}'
```

```json
{
  "id": 1,
  "content": "Meeting notes:\n- Review PR\n- Deploy to staging",
  "created_at": "2025-02-02T10:00:00"
}
```

**Liệt kê notes**

```bash
curl http://localhost:8000/notes/
```

**Lấy note theo ID**

```bash
curl http://localhost:8000/notes/1
```

---

### Action Items

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| `POST` | `/action-items/extract` | Trích xuất action items (rule-based) |
| `POST` | `/action-items/extract?use_llm=true` | Trích xuất action items (LLM) |
| `GET` | `/action-items/` | Liệt kê action items |
| `GET` | `/action-items/?note_id=1` | Liệt kê action items theo note |
| `POST` | `/action-items/{id}/done` | Đánh dấu hoàn thành/chưa hoàn thành |

#### Ví dụ

**Trích xuất (rule-based)**

```bash
curl -X POST http://localhost:8000/action-items/extract \
  -H "Content-Type: application/json" \
  -d '{
    "text": "- [ ] Set up database\n* implement API\n1. Write tests",
    "save_note": true
  }'
```

```json
{
  "note_id": 2,
  "items": [
    {"id": 1, "note_id": 2, "text": "Set up database", "done": false, "created_at": "..."},
    {"id": 2, "note_id": 2, "text": "implement API", "done": false, "created_at": "..."},
    {"id": 3, "note_id": 2, "text": "Write tests", "done": false, "created_at": "..."}
  ]
}
```

**Trích xuất (LLM)** — cần Ollama chạy sẵn

```bash
curl -X POST "http://localhost:8000/action-items/extract?use_llm=true" \
  -H "Content-Type: application/json" \
  -d '{"text": "Remember to email John and book the meeting room.", "save_note": false}'
```

**Liệt kê action items**

```bash
curl http://localhost:8000/action-items/
curl "http://localhost:8000/action-items/?note_id=1"
```

**Đánh dấu hoàn thành**

```bash
curl -X POST http://localhost:8000/action-items/1/done \
  -H "Content-Type: application/json" \
  -d '{"done": true}'
```

---

### Khác

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| `GET` | `/` | Trang HTML giao diện |
| `GET` | `/static/*` | Tệp tĩnh (frontend) |

---

## Chạy thử nghiệm (Tests)

### Cài đặt dev dependencies

```bash
poetry install --with dev
# hoặc
pip install pytest httpx
```

### Chạy toàn bộ tests

Từ thư mục gốc `modern-software-dev-assignments` (nơi có `pyproject.toml`):

```bash
cd modern-software-dev-assignments
poetry run pytest week2_refactor/tests -v
```

Hoặc nếu tests nằm trong `week2_refactor`:

```bash
cd week2_refactor
pytest tests -v
```

### Chạy tests extract

```bash
pytest week2_refactor/app/services/extract.py -v -k "extract"
```

### Chạy với coverage

```bash
poetry run pytest week2_refactor/tests -v --cov=app --cov-report=term-missing
```

**Lưu ý:** Thư mục `tests/` hiện chỉ có `__init__.py`. Có thể tham khảo `week2/tests/test_extract.py` và `week2/tests/test_extract_llm.py` để viết tests tương tự cho `week2_refactor`. Các tests extract service không cần HTTP client; tests API cần `TestClient` từ FastAPI và override DB path (ví dụ dùng file tạm) trong `conftest.py`.

---

## Schema API

### Request / Response

**ExtractRequest**

```json
{
  "text": "string (required, min 1 char)",
  "save_note": false
}
```

**ExtractResponse**

```json
{
  "note_id": 1,
  "items": [{"id": 1, "note_id": 1, "text": "...", "done": false, "created_at": "..."}]
}
```

**MarkDoneRequest**

```json
{"done": true}
```

**CreateNoteRequest**

```json
{"content": "string (required, min 1 char)"}
```

**NoteOut / ActionItemOut** — các trường `id`, `content`/`text`, `created_at`, và với action items: `note_id`, `done`.
