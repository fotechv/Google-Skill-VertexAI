# =============================================================================
# CODING AGENT FROM SCRATCH - Bài giảng mô phỏng Agent lập trình đơn giản
# =============================================================================
# Chương trình tạo một coding assistant tương tác qua CLI, cho phép LLM gọi
# các tool (read_file, list_files, edit_file) để thực hiện tác vụ lập trình.
# =============================================================================

# Dùng để lấy signature của hàm (tên tham số, kiểu) cho mô tả tool
import inspect
import json  # Parse JSON trong output của LLM khi gọi tool
import os  # Truy cập biến môi trường (OPENAI_API_KEY)

from openai import OpenAI  # Client gọi API OpenAI (GPT)
from dotenv import load_dotenv  # Load biến môi trường từ file .env
from pathlib import Path  # Thao tác đường dẫn file an toàn, đa nền tảng
from typing import Any, Dict, List, Tuple  # Type hints cho Python

# Load các biến từ file .env vào os.environ (ví dụ OPENAI_API_KEY)
load_dotenv()

# Khởi tạo client OpenAI, dùng API key từ biến môi trường
# openai_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
# openai_client = OpenAI(
#     base_url="http://localhost:1234/v1",
#     api_key="lm-studio"  # fake key, LM Studio không check thật
# )
# # LM Studio: openai/gpt-oss-20b
# model_name = "openai/gpt-oss-20b"

openai_client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"  # chuỗi bất kỳ, Ollama không check
)
# Ollama Tên model (có thể cần đổi thành gpt-5 gpt-4o, gpt-4, v.v. tùy API)
# model="gpt-oss:20b",
model_name = "gpt-oss:20b"


# Prompt hệ thống mô tả vai trò của assistant và cách gọi tool
# {tool_list_repr} sẽ được thay thế bằng danh sách tool chi tiết
SYSTEM_PROMPT = """
You are a coding assistant whose goal it is to help us solve coding tasks. 
You have access to a series of tools you can execute. Hear are the tools you can execute:

{tool_list_repr}

When you want to use a tool, reply with exactly one line in the format: 'tool: TOOL_NAME({{JSON_ARGS}})' and nothing else.
Use compact single-line JSON with double quotes. After receiving a tool_result(...) message, continue the task.
If no tool is needed, respond normally.
"""

# Mã ANSI màu cho terminal: xanh dương (You), vàng (Assistant), reset
YOU_COLOR = "\u001b[94m"
ASSISTANT_COLOR = "\u001b[93m"
RESET_COLOR = "\u001b[0m"


def resolve_abs_path(path_str: str) -> Path:
    """
    Chuyển đường dẫn tương đối hoặc có ~ thành đường dẫn tuyệt đối.

    Ví dụ: file.py -> /Users/home/user/project/file.py

    :param path_str: Đường dẫn do người dùng cung cấp (có thể tương đối hoặc ~)
    :return: Đối tượng Path tuyệt đối, chuẩn hóa
    """
    path = Path(path_str).expanduser()  # Thay ~ bằng thư mục home
    if not path.is_absolute():  # Nếu là đường dẫn tương đối
        # Nối với cwd và resolve để ra path tuyệt đối
        path = (Path.cwd() / path).resolve()
    return path


def read_file_tool(filename: str) -> Dict[str, Any]:
    """
    Tool đọc toàn bộ nội dung file.

    :param filename: Tên hoặc đường dẫn file cần đọc
    :return: Dict chứa file_path và content (nội dung file)
    """
    full_path = resolve_abs_path(filename)  # Chuyển thành đường dẫn tuyệt đối

    # In ra để debug / xác nhận file đang đọc
    print("\n[TOOL read_file]")
    print("input filename:", filename)
    print("resolved path:", full_path)
    print("exists:", full_path.exists())

    with open(str(full_path), "r") as f:  # Mở file ở chế độ đọc (text)
        content = f.read()  # Đọc toàn bộ nội dung
    return {
        "file_path": str(full_path),
        "content": content
    }


def list_files_tool(path: str) -> Dict[str, Any]:
    """
    Tool liệt kê các file và thư mục con trong một thư mục.

    :param path: Đường dẫn thư mục cần list
    :return: Dict chứa path và danh sách files (mỗi item có filename, type)
    """
    full_path = resolve_abs_path(path)

    print("\n[TOOL list_files]")
    print("input path:", path)
    print("resolved path:", full_path)
    print("cwd:", Path.cwd())

    all_files = []
    for item in full_path.iterdir():  # Duyệt từng item trong thư mục
        all_files.append({
            "filename": item.name,  # Tên file/thư mục
            "type": "file" if item.is_file() else "dir"  # Phân loại file hay dir
        })

    print("files found:", [f["filename"] for f in all_files])

    return {
        "path": str(full_path),
        "files": all_files
    }


def edit_file_tool(path: str, old_str: str, new_str: str) -> Dict[str, Any]:
    """
    Tool chỉnh sửa file: thay lần xuất hiện đầu tiên của old_str bằng new_str.
    Nếu old_str rỗng, tạo file mới hoặc ghi đè toàn bộ nội dung bằng new_str.

    :param path: Đường dẫn file cần sửa
    :param old_str: Chuỗi cần tìm và thay thế
    :param new_str: Chuỗi thay thế
    :return: Dict chứa path và action (created_file / edited / old_str not found)
    """
    full_path = resolve_abs_path(path)
    if old_str == "":  # Trường hợp tạo/ghi đè file mới
        full_path.write_text(new_str, encoding="utf-8")
        return {
            "path": str(full_path),
            "action": "created_file"
        }
    original = full_path.read_text(encoding="utf-8")  # Đọc nội dung hiện tại
    if original.find(old_str) == -1:  # Không tìm thấy old_str
        return {
            "path": str(full_path),
            "action": "old_str not found"
        }
    # Thay 1 lần xuất hiện đầu tiên
    edited = original.replace(old_str, new_str, 1)
    full_path.write_text(edited, encoding="utf-8")
    return {
        "path": str(full_path),
        "action": "edited"
    }


# Registry ánh xạ tên tool (string) -> hàm Python tương ứng
TOOL_REGISTRY = {
    "read_file": read_file_tool,
    "list_files": list_files_tool,
    "edit_file": edit_file_tool
}


def get_tool_str_representation(tool_name: str) -> str:
    """
    Tạo chuỗi mô tả tool để đưa vào system prompt.
    Lấy docstring và signature của hàm để LLM biết cách gọi.
    """
    tool = TOOL_REGISTRY[tool_name]  # Lấy hàm từ registry
    return f"""
    Name: {tool_name}
    Description: {tool.__doc__}
    Signature: {inspect.signature(tool)}
    """


def get_full_system_prompt():
    """
    Ghép system prompt gốc với danh sách mô tả tất cả các tool.
    """
    tool_str_repr = ""
    for tool_name in TOOL_REGISTRY:
        tool_str_repr += "TOOL\n===" + get_tool_str_representation(tool_name)
        tool_str_repr += f"\n{'=' * 15}\n"  # Phân cách giữa các tool
    # Thay {tool_list_repr} trong prompt
    print(f"prompt={tool_str_repr}")
    return SYSTEM_PROMPT.format(tool_list_repr=tool_str_repr)


def extract_tool_invocations(text: str) -> List[Tuple[str, Dict[str, Any]]]:
    """
    Parse output của LLM để tìm các dòng gọi tool dạng: tool: TOOL_NAME({...})

    :param text: Nội dung response từ LLM
    :return: List các tuple (tool_name, args_dict)
    """
    invocations = []
    for raw_line in text.splitlines():  # Duyệt từng dòng
        line = raw_line.strip()
        if not line.startswith("tool:"):  # Bỏ qua dòng không phải lệnh tool
            continue
        try:
            after = line[len("tool:"):].strip()  # Phần sau "tool:"
            # Tách tên tool và phần trong ngoặc (maxsplit=1)
            name, rest = after.split("(", 1)
            name = name.strip()
            if not rest.endswith(")"):  # Thiếu đóng ngoặc -> bỏ qua
                continue
            json_str = rest[:-1].strip()  # Bỏ ")" ở cuối, lấy chuỗi JSON
            args = json.loads(json_str)  # Parse JSON thành dict
            invocations.append((name, args))
        except Exception:  # JSON sai hoặc lỗi khác -> bỏ qua dòng này
            continue
    return invocations


def execute_llm_call(conversation: List[Dict[str, str]]):
    """
    Gửi conversation lên OpenAI API và lấy nội dung response.

    :param conversation: List các message {role, content}
    :return: Chuỗi nội dung message của assistant
    """
    response = openai_client.chat.completions.create(
        model=model_name,
        messages=conversation,
        max_completion_tokens=2000
    )
    msg = response.choices[0].message

    # DEBUG: xem model trả về gì
    # print("DEBUG msg.content =", repr(msg.content))
    # print("DEBUG msg.tool_calls =", getattr(msg, "tool_calls", None))

    # return msg.content or ""  # Lấy text từ choice đầu tiên

    # baonx add here
    # đoạn code này xử lý cho model chạy bằng Ollama
    print("\n====== LLM RAW RESPONSE ======")
    print("content:", repr(msg.content))
    print("tool_calls:", msg.tool_calls)
    print("================================\n")

    if msg.content:
        return msg.content

    tool_calls = getattr(msg, "tool_calls", None) or []
    if tool_calls:
        tc = tool_calls[0]
        name = tc.function.name
        args_str = tc.function.arguments or "{}"

        print("[DEBUG] tool_call detected")
        print("raw tool name:", name)
        print("raw args:", args_str)

        # normalize name ngay tại đây
        if "." in name:
            name = name.split(".")[-1]
        if ":" in name:
            name = name.split(":")[-1]

        # đảm bảo args là JSON 1 dòng
        try:
            args = json.loads(args_str)
            args_str = json.dumps(args, ensure_ascii=False)
        except Exception:
            pass

        print("normalized tool name:", name)

        return f"tool: {name}({args_str})"

    return ""

def run_coding_agent_loop():
    """
    Vòng lặp chính: đọc input người dùng -> gọi LLM -> nếu LLM gọi tool thì thực thi
    và đưa kết quả lại vào conversation -> lặp cho đến khi LLM trả lời bình thường.
    """
    print(get_full_system_prompt())  # In system prompt ra màn hình (debug/info)
    conversation = [{
        "role": "system",
        "content": get_full_system_prompt()
    }]
    while True:  # Vòng lặp chính: đợi input người dùng
        try:
            # Nhập với màu xanh
            user_input = input(f"{YOU_COLOR}You:{RESET_COLOR}")
        except (KeyboardInterrupt, EOFError):  # Ctrl+C hoặc EOF -> thoát
            break
        conversation.append({
            "role": "user",
            "content": user_input.strip()
        })
        while True:  # Vòng lặp con: xử lý tool calls nếu có
            assistant_response = execute_llm_call(conversation)  # Gọi LLM
            tool_invocations = extract_tool_invocations(assistant_response)  # Parse xem có gọi tool không

            print("\n------ PARSED TOOL INVOCATIONS ------")
            print(tool_invocations)
            print("------------------------------------\n")

            if not tool_invocations:  # Không có tool call -> in response và thoát vòng con
                print(f"{ASSISTANT_COLOR}Assistant:{RESET_COLOR}: {assistant_response}")
                conversation.append({
                    "role": "assistant",
                    "content": assistant_response
                })
                break
            for name, args in tool_invocations:  # Thực thi từng tool call
                tool = TOOL_REGISTRY[name]
                resp = ""
                print(name, args)  # In tool name và args
                if name == "read_file":
                    resp = tool(args.get("filename", "."))
                elif name == "list_files":
                    resp = tool(args.get("path", "."))
                elif name == "edit_file":
                    resp = tool(args.get("path", "."),
                                args.get("old_str", ""),
                                args.get("new_str", ""))

                print(f"[DEBUG] tool_call resp={resp}")

                conversation.append({
                    "role": "user",
                    # Đưa kết quả tool vào conversation
                    "content": f"tool_result({json.dumps(resp)})"
                })


if __name__ == "__main__":
    # Mục đích là cho tool gọi đúng hàm tương ứng với text input
    # You: List files in the current directory
    # You: Read the file README.md
    # You: Add a comment at the top of simple_mcp.py that says "# MCP Server"
    run_coding_agent_loop()
