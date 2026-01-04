
Đây là file code Python để thực hiện kỹ thuật **Chain of Thought (CoT)** trong AI. File này kiểm tra khả năng của mô hình ngôn ngữ trong việc giải quyết bài toán toán học phức tạp.

## **Mục đích chính**
- Thử nghiệm prompt engineering để mô hình AI suy nghĩ từng bước (step-by-step reasoning)
- Giải bài toán tính modulo: `3^{12345} (mod 100)`

## **Cấu trúc code**

### **Import và cấu hình**
- `os`, `re`: Thư viện hệ thống và regex
- `dotenv`, `ollama`: Tải biến môi trường và kết nối AI model
- `NUM_RUNS_TIMES = 5`: Số lần thử nghiệm tối đa

### **Prompt variables**
- `YOUR_SYSTEM_PROMPT`: **TODO** - Bạn cần điền system prompt ở đây
- `USER_PROMPT`: Yêu cầu giải bài toán và trả lời cuối cùng
- `EXPECTED_OUTPUT = "Answer: 43"`: Đáp án đúng mong muốn

### **Hàm chính**

#### **[extract_final_answer()](cci:1://file:///d:/MyProjects/AI%20Develop/modern-software-dev-assignments/week1/chain_of_thought.py:24:0-39:23)** (dòng 25-40)
- Trích xuất câu trả lời cuối cùng từ output dài của AI
- Tìm dòng cuối cùng bắt đầu bằng "Answer:"
- Chuẩn hóa định dạng "Answer: <số>"

#### **[test_your_prompt()](cci:1://file:///d:/MyProjects/AI%20Develop/modern-software-dev-assignments/week1/chain_of_thought.py:42:0-65:16)** (dòng 43-66)
- Chạy test đến 5 lần
- Gọi `ollama.chat()` với model `llama3.1:8b`
- So sánh output với đáp án expected
- In "SUCCESS" nếu đúng

### **Cách hoạt động**
1. AI nhận system prompt và user prompt
2. AI suy nghĩ từng bước để giải `3^{12345} (mod 100)`
3. Extract final answer so sánh với "Answer: 43"
4. Lặp lại tối đa 5 lần nếu chưa đúng

## **Bạn cần làm**
Điền `YOUR_SYSTEM_PROMPT` (dòng 11) với prompt hướng dẫn AI suy nghĩ logic từng bước để giải bài toán modulo này.