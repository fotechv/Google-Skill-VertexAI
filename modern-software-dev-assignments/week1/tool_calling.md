
Đây là file code Python thực hiện kỹ thuật **Tool Calling** trong AI. File này minh họa cách AI có thể gọi và thực thi các công cụ cụ thể.

## **Trọng tâm chính**
**Tool Calling** - Kỹ thuật cho phép AI model:
- Nhận diện khi nào cần sử dụng công cụ
- Tạo JSON call để gọi tool
- Thực thi tool và nhận kết quả

## **Cấu trúc code**

### **Phần 1: Tool Implementation (dòng 14-66)**
- [_annotation_to_str()](cci:1://file:///d:/MyProjects/AI%20Develop/modern-software-dev-assignments/week1/tool_calling.py:16:0-25:40): Chuyển AST annotation thành string
- [_list_function_return_types()](cci:1://file:///d:/MyProjects/AI%20Develop/modern-software-dev-assignments/week1/tool_calling.py:28:0-39:18): Parse file Python, lấy danh sách function và return type
- [output_every_func_return_type()](cci:1://file:///d:/MyProjects/AI%20Develop/modern-software-dev-assignments/week1/tool_calling.py:42:0-51:61): **Tool chính** - Trả về danh sách "function_name: return_type"
- Sample functions: [add()](cci:1://file:///d:/MyProjects/AI%20Develop/modern-software-dev-assignments/week1/tool_calling.py:55:0-56:16), [greet()](cci:1://file:///d:/MyProjects/AI%20Develop/modern-software-dev-assignments/week1/tool_calling.py:59:0-60:28) để test
- `TOOL_REGISTRY`: Đăng ký các tool có thể gọi

### **Phần 2: Prompt Scaffolding (dòng 68-169)**
- `YOUR_SYSTEM_PROMPT`: **TODO** - System prompt hướng dẫn AI gọi tool
- [extract_tool_call()](cci:1://file:///d:/MyProjects/AI%20Develop/modern-software-dev-assignments/week1/tool_calling.py:86:0-98:77): Parse JSON từ output của AI
- [run_model_for_tool_call()](cci:1://file:///d:/MyProjects/AI%20Develop/modern-software-dev-assignments/week1/tool_calling.py:101:0-111:37): Gọi AI model để tạo tool call
- [execute_tool_call()](cci:1://file:///d:/MyProjects/AI%20Develop/modern-software-dev-assignments/week1/tool_calling.py:114:0-132:23): Thực thi tool từ JSON call
- [demo_your_prompt()](cci:1://file:///d:/MyProjects/AI%20Develop/modern-software-dev-assignments/week1/tool_calling.py:140:0-163:16): Hàm test chính

## **Luồng hoạt động**

1. **AI nhận system prompt** hướng dẫn cách gọi tool
2. **AI tạo JSON call** với format:
   ```json
   {
     "tool": "output_every_func_return_type",
     "args": {"file_path": "path/to/file"}
   }
   ```
3. **Parse và validate** JSON call
4. **Execute tool** với arguments
5. **Compare output** với expected result

## **Mục đích học thuật**
- **Function Calling**: AI học cách gọi hàm chính xác
- **Structured Output**: AI tạo JSON format đúng
- **Tool Selection**: AI chọn tool phù hợp với task
- **Parameter Passing**: AI truyền arguments đúng cách

## **Bạn cần làm**
Điền `YOUR_SYSTEM_PROMPT` (dòng 73) để hướng dẫn AI:
- Nhận diện khi nào cần gọi tool
- Format JSON call đúng chuẩn
- Truyền parameters chính xác

Đây là kỹ thuật quan trọng để AI có thể tương tác với external APIs và databases.

Đây là ví dụ cho `YOUR_SYSTEM_PROMPT` để hướng dẫn AI gọi tool đúng cách:

```python
YOUR_SYSTEM_PROMPT = """You are an AI assistant that can call tools to analyze Python files.

When asked to perform a task, you must call the appropriate tool by responding with a JSON object in this exact format:

{
  "tool": "tool_name",
  "args": {
    "parameter_name": "parameter_value"
  }
}

Available tools:
- output_every_func_return_type: Returns a list of function names and their return types from a Python file
  - Parameters: file_path (string, optional) - path to the Python file to analyze

Rules:
1. Always respond with valid JSON only
2. Do not include any explanatory text outside the JSON
3. Use the exact tool name and parameter names shown above
4. If file_path is not provided, it will default to the current file

Now call the tool to analyze the current file."""
```

**Hoặc phiên bản ngắn gọn hơn:**

```python
YOUR_SYSTEM_PROMPT = """You must call tools by responding with JSON only.

Format:
{
  "tool": "output_every_func_return_type", 
  "args": {"file_path": ""}
}

Available tool: output_every_func_return_type - analyzes Python file functions and return types.

Respond with JSON tool call now."""
```

**Key points trong prompt:**
- Chỉ yêu cầu JSON output, không có text thừa
- Format JSON rõ ràng với `tool` và `args`
- List available tools và parameters
- Hướng dẫn AI gọi tool ngay lập tức

Prompt này sẽ làm AI hiểu được cách tạo tool call JSON đúng format để thực thi function [output_every_func_return_type()](cci:1://file:///d:/MyProjects/AI%20Develop/modern-software-dev-assignments/week1/tool_calling.py:42:0-51:61).


# Như vậy về cơ bản là chức năng trong file này là đưa ra prompt phù hợp để AI model đưa ra biến chính xác để call tool đúng không

Đúng vậy! Bạn đã hiểu đúng trọng tâm của file này.

## **Mục đích chính**
File này kiểm tra khả năng **prompt engineering** để AI model:
- Hiểu khi nào cần gọi tool
- Tạo JSON call **chính xác** với đúng format
- Truyền đúng **parameters** cho tool

## **Luồng hoạt động**

1. **AI nhận system prompt** → Hướng dẫn cách gọi tool
2. **AI tạo JSON output** → Format: `{"tool": "name", "args": {...}}`
3. **Code parse JSON** → Validate và extract tool name + args
4. **Execute tool** → Gọi function từ `TOOL_REGISTRY`
5. **Compare results** → Kiểm tra output có khớp expected không

## **Điểm mấu chốt**
- **Prompt quality** quyết định AI có tạo JSON đúng format không
- **JSON parsing** kiểm tra AI có tuân thủ rules không
- **Tool execution** verify AI truyền parameters đúng không
- **Output validation** đảm bảo AI gọi tool đúng cách

## **Kỹ thuật được test**
- **Function Calling** - AI học cách gọi hàm
- **Structured Output** - AI tạo JSON format chuẩn
- **Parameter Passing** - AI truyền arguments đúng
- **Tool Selection** - AI chọn tool phù hợp

Về cơ bản, đây là bài tập **prompt engineering** để làm cho AI model hiểu và thực thi tool calling một cách chính xác. Prompt càng tốt, AI càng tạo ra JSON call đúng chuẩn.
