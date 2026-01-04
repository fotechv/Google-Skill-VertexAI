
Đây là file code Python thực hiện kỹ thuật **Self-Consistency Prompting** trong AI. File này kiểm tra độ nhất quán của AI model khi giải quyết cùng một bài toán nhiều lần.

## **Trọng tâm chính**
**Self-Consistency** - Kỹ thuật cải thiện độ chính xác bằng cách:
- Chạy cùng prompt nhiều lần (5 lần)
- Sử dụng `temperature=1` để tạo sự đa dạng
- Majority vote trên các câu trả lời
- Chọn đáp án xuất hiện nhiều nhất

## **Cấu trúc code**

### **Cấu hình**
- `NUM_RUNS_TIMES = 5`: Số lần chạy test
- `YOUR_SYSTEM_PROMPT`: **TODO** - Prompt cần điền
- `USER_PROMPT`: Bài toán về chuyến đi xe đạp 60 dặm
- `EXPECTED_OUTPUT = "Answer: 25"`: Đáp án đúng

### **Hàm chính**

#### **[extract_final_answer()](cci:1://file:///d:/MyProjects/AI%20Develop/modern-software-dev-assignments/week1/chain_of_thought.py:50:0-65:23)** (dòng 25-39)
- Trích xuất câu trả lời cuối cùng từ output của AI
- Tìm dòng bắt đầu bằng "Answer:"
- Chuẩn hóa thành format "Answer: <số>"

#### **[demo_your_prompt()](cci:1://file:///d:/MyProjects/AI%20Develop/modern-software-dev-assignments/week1/chain_of_thought.py:68:0-91:16)** (dòng 42-80)
- Chạy prompt 5 lần với `temperature=1`
- Lưu tất cả answers vào list
- Đếm tần suất mỗi answer với `Counter`
- Chọn majority answer (xuất hiện nhiều nhất)
- So sánh với expected output

## **Luồng hoạt động**

1. **AI nhận system prompt** + user prompt
2. **Chạy 5 lần** với temperature=1 (tạo diversity)
3. **Extract answers** từ mỗi lần chạy
4. **Majority voting** - Chọn answer phổ biến nhất
5. **Compare** với expected result

## **Bài toán ví dụ**
> Henry đi xe đạp 60 dặm, dừng sau 20 dặm, dừng lần nữa 15 dặm trước khi kết thúc. Hỏi quãng đường giữa 2 lần dừng?

**Answer: 25** (60 - 15 - 20 = 25)

## **Mục đích học thuật**
- **Consistency Testing**: Kiểm tra AI có nhất quán không
- **Majority Voting**: Cải thiện accuracy bằng statistical approach
- **Temperature Effects**: Test impact của randomness
- **Prompt Engineering**: Tìm prompt tốt nhất cho consistency

## **Bạn cần làm**
Điền `YOUR_SYSTEM_PROMPT` (dòng 12) để AI:
- Giải toán logic nhất quán
- Tránh sai sót tính toán
- Đưa ra cùng đáp án qua nhiều lần chạy

Kỹ thuật này giúp giảm lỗi random và tăng reliability của AI model.

Đây là ví dụ cho `YOUR_SYSTEM_PROMPT` để đạt consistency cao nhất:

```python
YOUR_SYSTEM_PROMPT = """You are a precise mathematical problem solver. Always solve step-by-step and show your work.

For word problems:
1. Identify the given numbers and what they represent
2. Determine what the question is asking for
3. Set up the calculation clearly
4. Solve step by step
5. Double-check your answer makes sense

Important: Be consistent in your reasoning. The same problem should always yield the same answer.

Now solve the problem and provide the final answer on the last line as "Answer: <number>"."""
```

**Hoặc phiên bản tập trung vào consistency:**

```python
YOUR_SYSTEM_PROMPT = """You are a logical reasoning expert. For consistency:

1. Break down the problem into clear steps
2. Verify each step before proceeding
3. Use the same logical approach every time
4. Check your final answer against the problem statement

The problem: Henry's bike trip analysis
- Total distance: 60 miles
- First stop: after 20 miles  
- Second stop: 15 miles before end
- Find: distance between stops

Solve methodically and give final answer as "Answer: <number>"."""
```

**Key points cho consistency:**
- **Structured approach** - Luôn theo cùng quy trình
- **Step-by-step reasoning** - Tránh skip logic
- **Verification** - Kiểm tra lại kết quả
- **Clear methodology** - Method rõ ràng, lặp lại được

Prompt này giúp AI giải toán cùng cách mỗi lần, tăng khả năng majority vote ra đáp án đúng "Answer: 25".