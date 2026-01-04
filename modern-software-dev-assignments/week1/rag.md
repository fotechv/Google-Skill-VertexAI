
Đây là file code Python thực hiện kỹ thuật **RAG (Retrieval-Augmented Generation)** trong AI. File này minh họa cách AI sử dụng external knowledge để trả lời câu hỏi.

## **Mục đích chính**
**RAG** - Kỹ thuật kết hợp:
- **Retrieval**: Tìm kiếm thông tin relevant từ knowledge base
- **Generation**: AI sử dụng thông tin đó để生成 câu trả lời chính xác

## **Cấu trúc code**

### **Data Loading**
- `DATA_FILES`: List path đến file `api_docs.txt` (chứa API documentation)
- [load_corpus_from_files()](cci:1://file:///d:/MyProjects/AI%20Develop/modern-software-dev-assignments/week1/rag.py:15:0-26:17): Load nội dung từ external files
- `CORPUS`: Knowledge base chứa API docs

### **Task Definition**
- `QUESTION`: Yêu cầu viết Python function `fetch_user_name()` để gọi API
- `REQUIRED_SNIPPETS`: Các code fragments bắt buộc phải có:
  - `def fetch_user_name(`
  - `requests.get`
  - [/users/](cci:7://file:///users:0:0-0:0)
  - `X-API-Key`
  - `return`

### **Core Functions**

#### **[YOUR_CONTEXT_PROVIDER()](cci:1://file:///d:/MyProjects/AI%20Develop/modern-software-dev-assignments/week1/rag.py:53:0-58:13)** (dòng 54-59)
- **TODO** - Function chọn relevant documents từ corpus
- Hiện tại return `[]` (không cung cấp context)

#### **[make_user_prompt()](cci:1://file:///d:/MyProjects/AI%20Develop/modern-software-dev-assignments/week1/rag.py:61:0-75:5)** (dòng 62-76)
- Tạo prompt với context + task + requirements
- Nếu có context, thêm vào prompt
- Nếu không, hiển thị "(no context provided)"

#### **[test_your_prompt()](cci:1://file:///d:/MyProjects/AI%20Develop/modern-software-dev-assignments/week1/rag.py:91:0-118:16)** (dòng 92-119)
- Chạy test 5 lần với `temperature=0.0`
- Extract code block từ AI response
- Kiểm tra tất cả `REQUIRED_SNIPPETS` có mặt không
- Success nếu tất cả required code có mặt

## **Luồng hoạt động RAG**

1. **Load Corpus** - Đọc API docs từ external file
2. **Retrieve Context** - Chọn relevant documents (TODO)
3. **Augment Prompt** - Thêm context vào user prompt
4. **Generate Response** - AI viết code dựa trên context
5. **Validate Output** - Kiểm tra code có đủ requirements không

## **Mục đích học thuật**
- **Context Utilization** - Test AI có dùng external knowledge không
- **Retrieval Strategy** - Làm sao chọn relevant documents
- **Grounded Generation** - AI trả lời dựa trên provided context
- **Code Generation** - Viết function từ documentation

## **Bạn cần làm**
1. **Điền `YOUR_SYSTEM_PROMPT`** (dòng 40) - Hướng dẫn AI sử dụng context
2. **Cập nhật [YOUR_CONTEXT_PROVIDER](cci:1://file:///d:/MyProjects/AI%20Develop/modern-software-dev-assignments/week1/rag.py:53:0-58:13)** (dòng 59) - Trả về relevant documents

Đây là kỹ thuật quan trọng để AI có thể truy cập knowledge base và trả lời câu hỏi dựa trên external documentation.



Đã cập nhật cả hai phần:

## **YOUR_SYSTEM_PROMPT**
```python
"""You are a Python code generator who uses provided API documentation to write functions.

Rules:
1. Use ONLY the context information provided
2. Follow the exact API specifications shown in the documentation
3. Include necessary imports
4. Handle authentication exactly as documented
5. Return only what the task specifies

Generate clean, functional Python code based on the given API documentation."""
```

## **YOUR_CONTEXT_PROVIDER**
```python
def YOUR_CONTEXT_PROVIDER(corpus: List[str]) -> List[str]:
    # Return all available corpus documents to provide full API documentation context
    return corpus
```

**Key points:**
- **System Prompt** hướng dẫn AI tuân thủ API docs và chỉ dùng provided context
- **Context Provider** trả về toàn bộ corpus để AI có đầy đủ API documentation
- AI sẽ có đủ thông tin để viết function `fetch_user_name()` với đúng API calls, authentication headers, và return format

Bây giờ AI có thể truy cập API documentation và generate code chính xác theo requirements.


## Như vậy bản chất của RAG là viết prompt cho AI Model để tạo một function nào đó và thực thi công việc nào đó à? Tại sao develop chủ động viết luôn hàm đấy mà phải mô tả cho AI viết

Chính xác! Bạn đã nhận ra điểm quan trọng về RAG. Đây là sự khác biệt giữa traditional development và RAG approach:

## **RAG không phải để thay thế developer**

### **Mục đích thực tế của RAG:**

1. **Dynamic Code Generation**
   - AI tạo code dựa trên **real-time data** (API docs thay đổi liên tục)
   - Không cần hardcode logic khi data source thường xuyên cập nhật

2. **Knowledge Integration**
   - Khi có **hàng ngàn API documents** khác nhau
   - AI tự động select relevant info và generate appropriate code

3. **Template-based Generation**
   - Generate **boilerplate code** cho nhiều similar tasks
   - Ví dụ: CRUD operations cho 100+ database tables

4. **Natural Language to Code**
   - User mô tả requirement bằng **ngôn ngữ tự nhiên**
   - AI chuyển thành code executable

### **Khi nào RAG hữu ích:**

✅ **Nên dùng RAG:**
- API documentation thay đổi liên tục
- Cần generate code cho nhiều similar tasks
- User không biết programming, chỉ mô tả bằng text
- Integration với external knowledge bases

❌ **Không nên dùng RAG:**
- Function logic cố định, không đổi
- Performance critical applications
- Simple, well-defined functions
- Production code cần maintainability

### **Ví dụ thực tế:**

**Traditional:**
```python
def fetch_user_name(user_id, api_key):
    # Hardcoded logic
    response = requests.get(f"https://api.example.com/users/{user_id}", 
                           headers={"X-API-Key": api_key})
    return response.json()["name"]
```

**RAG approach:**
- AI đọc API docs mới nhất
- Tự động generate code với updated endpoints
- Handle authentication changes automatically

**Kết luận:** RAG là công cụ cho **dynamic, knowledge-driven tasks**, không phải để thay thế developer viết functions đơn giản. Nó mạnh khi cần integrate real-time knowledge và generate code tự động.