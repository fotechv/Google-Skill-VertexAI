
Đây là file code Python thực hiện kỹ thuật **Reflexion** trong AI. File này minh họa cách AI tự cải thiện code dựa trên feedback từ test failures.

## **Trọng tâm chính**
**Reflexion** - Kỹ thuật AI tự reflection và improvement:
- Generate code ban đầu
- Test với test suite
- Phân tích failures
- Refactor code dựa trên feedback
- Test lại cho đến khi pass

## **Cấu trúc code**

### **Test Suite Definition**
- `SPECIALS`: Set các ký tự đặc biệt cho password validation
- `TEST_CASES`: 4 test cases với expected results:
  - `"Password1!"` → `True` (valid)
  - `"password1!"` → `False` (missing uppercase)
  - `"Password!"` → `False` (missing digit)
  - `"Password1"` → `False` (missing special)

### **Core Functions**

#### **[extract_code_block()](cci:1://file:///d:/MyProjects/AI%20Develop/modern-software-dev-assignments/week1/rag.py:90:0-100:23)** (dòng 31-38)
- Extract Python code từ AI response
- Hỗ trợ cả ```python``` và `````` formats

#### **[load_function_from_code()](cci:1://file:///d:/MyProjects/AI%20Develop/modern-software-dev-assignments/week1/reflexion.py:40:0-46:15)** (dòng 41-47)
- Execute code string để load function
- Trả về callable `is_valid_password`

#### **[evaluate_function()](cci:1://file:///d:/MyProjects/AI%20Develop/modern-software-dev-assignments/week1/reflexion.py:49:0-78:41)** (dòng 50-79)
- Test function với TEST_CASES
- Phân tích failures với detailed diagnostics
- Return (passed, failures_list)

#### **[generate_initial_function()](cci:1://file:///d:/MyProjects/AI%20Develop/modern-software-dev-assignments/week1/reflexion.py:81:0-90:55)** (dòng 82-91)
- Generate code ban đầu từ SYSTEM_PROMPT
- Sử dụng temperature=0.2 để giảm randomness

#### **[your_build_reflexion_context()](cci:1://file:///d:/MyProjects/AI%20Develop/modern-software-dev-assignments/week1/reflexion.py:93:0-98:13)** (dòng 94-99)
- **TODO** - Build context cho reflexion step
- Hiện tại return empty string

#### **[apply_reflexion()](cci:1://file:///d:/MyProjects/AI%20Develop/modern-software-dev-assignments/week1/reflexion.py:101:0-117:55)** (dòng 102-118)
- Gọi AI với reflexion_prompt + context
- Generate improved code

#### **[run_reflexion_flow()](cci:1://file:///d:/MyProjects/AI%20Develop/modern-software-dev-assignments/week1/reflexion.py:120:0-148:16)** (dòng 121-149)
- **Main flow**:
  1. Generate initial code
  2. Test và collect failures
  3. Apply reflexion để improve
  4. Test lại improved code

## **Luồng hoạt động Reflexion**

1. **Initial Generation** - AI viết `is_valid_password()` function
2. **Test Execution** - Run function với test cases
3. **Failure Analysis** - Phân tích tại sao test failed
4. **Reflexion** - AI nhận feedback và improve code
5. **Re-test** - Test improved version
6. **Success/Failure** - Kết quả cuối cùng

## **Mục đích học thuật**
- **Self-Improvement** - AI học từ mistakes
- **Feedback Loop** - Test → Analyze → Improve cycle
- **Code Debugging** - AI tự fix bugs
- **Iterative Development** - Quá trình development lặp lại

## **Bạn cần làm**
1. **Điền `YOUR_REFLEXION_PROMPT`** (dòng 18) - Hướng dẫn AI cách reflex
2. **Cập nhật [your_build_reflexion_context](cci:1://file:///d:/MyProjects/AI%20Develop/modern-software-dev-assignments/week1/reflexion.py:93:0-98:13)** (dòng 99) - Build context từ failures

Đây là kỹ thuật quan trọng để AI có thể tự debug và improve code quality qua iterative feedback.


Đã cập nhật cả hai phần:

## **YOUR_REFLEXION_PROMPT**
```python
"""
You are a code improvement assistant. Analyze the test failures and suggest improvements to the code.
Focus on fixing the specific issues that caused failures while maintaining the overall logic.
Return only a single fenced Python code block with the improved implementation.
"""
```

## **your_build_reflexion_context**
```python
def your_build_reflexion_context(prev_code: str, failures: List[str]) -> str:
    failures_text = "\n".join(f"- {failure}" for failure in failures)
    return f"""Previous code:
```python
{prev_code}
```

Test failures:
{failures_text}

Please fix the issues and provide an improved implementation."""
```

**Key points:**
- **Reflexion Prompt** hướng dẫn AI tập trung vào fixing specific issues
- **Context Builder** tạo structured feedback với:
  - Previous code trong fenced block
  - List của test failures
  - Clear instruction để fix issues

Bây giờ AI có thể:
1. Nhận detailed feedback về test failures
2. Phân tích specific issues (missing uppercase, digit, special chars)
3. Generate improved `is_valid_password()` function
4. Fix bugs dựa trên concrete test results

Đây là entire reflexion loop để AI tự improve code quality.