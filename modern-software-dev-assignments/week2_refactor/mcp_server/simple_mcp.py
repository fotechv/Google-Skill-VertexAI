# =============================================================================
# SIMPLE MCP SERVER - Máy chủ MCP đơn giản với các tool thao tác file
# =============================================================================
# Chương trình tạo một MCP (Model Context Protocol) server, cung cấp các tool
# read_file, list_files, edit_file để AI assistant có thể đọc, liệt kê và sửa file.
# Chạy bằng: python simple_mcp.py (hoặc thông qua MCP client như Cursor)
# =============================================================================

from pathlib import Path  # Thao tác đường dẫn file an toàn, đa nền tảng
# Type hints (Dict, List cho chú thích kiểu)
from typing import Any, Dict, List
# Thư viện tạo MCP server; decorator @mcp.tool đăng ký hàm thành tool
from fastmcp import FastMCP

# Khởi tạo instance FastMCP - đây là server MCP với tên "SimpleMCPTestServer"
mcp = FastMCP(name="SimpleMCPTestServer")


def resolve_abs_path(path_str: str) -> Path:
    """
    Chuyển đường dẫn tương đối hoặc có ~ thành đường dẫn tuyệt đối.

    Ví dụ: file.py -> /Users/home/mihail/modern-software-dev-lectures/file.py

    :param path_str: Đường dẫn do người dùng cung cấp (có thể tương đối hoặc ~)
    :return: Đối tượng Path tuyệt đối, chuẩn hóa
    """
    path = Path(path_str).expanduser()  # Thay ~ bằng thư mục home của user
    if not path.is_absolute():  # Nếu là đường dẫn tương đối
        # Nối với thư mục hiện tại, resolve ra path tuyệt đối
        path = (Path.cwd() / path).resolve()
    return path


@mcp.tool  # Decorator đăng ký hàm này là MCP tool - AI có thể gọi qua protocol
def read_file_tool(filename: str) -> Dict[str, Any]:
    """
    Tool đọc toàn bộ nội dung file.

    :param filename: Tên hoặc đường dẫn file cần đọc
    :return: Dict chứa file_path và content (nội dung file)
    """
    full_path = resolve_abs_path(filename)  # Chuyển thành đường dẫn tuyệt đối
    print(full_path)  # In ra màn hình để debug / xác nhận file đang đọc
    # TODO (mihail): Be more defensive in the file reading here
    with open(str(full_path), "r") as f:  # Mở file ở chế độ đọc text
        content = f.read()  # Đọc toàn bộ nội dung
    return {
        "file_path": str(full_path),
        "content": content
    }


@mcp.tool  # Đăng ký làm MCP tool
def list_files_tool(path: str) -> Dict[str, Any]:
    """
    Tool liệt kê các file và thư mục con trong một thư mục.

    :param path: Đường dẫn thư mục cần list
    :return: Dict chứa path và danh sách files (mỗi item có filename, type)
    """
    full_path = resolve_abs_path(path)
    all_files = []
    for item in full_path.iterdir():  # Duyệt từng item (file hoặc dir) trong thư mục
        all_files.append({
            "filename": item.name,  # Tên file hoặc thư mục
            "type": "file" if item.is_file() else "dir"  # Phân loại: file hay thư mục
        })
    return {
        "path": str(full_path),
        "files": all_files
    }


@mcp.tool  # Đăng ký làm MCP tool
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
    p = Path(full_path)  # Đảm bảo dùng Path cho read_text/write_text
    if old_str == "":  # Trường hợp tạo file mới hoặc ghi đè toàn bộ
        p.write_text(new_str, encoding="utf-8")  # Ghi nội dung mới vào file
        return {
            "path": str(full_path),
            "action": "created_file"
        }
    original = p.read_text(encoding="utf-8")  # Đọc nội dung hiện tại
    if original.find(old_str) == -1:  # Không tìm thấy old_str trong file
        return {
            "path": str(full_path),
            "action": "old_str not found"
        }
    # Thay 1 lần xuất hiện đầu tiên
    edited = original.replace(old_str, new_str, 1)
    p.write_text(edited, encoding="utf-8")  # Ghi nội dung đã sửa trở lại file
    return {
        "path": str(full_path),
        "action": "edited"
    }


if __name__ == "__main__":
    # Chỉ chạy server khi file được thực thi trực tiếp (không import)
    # Với transport 'stdio' → không có port nào cả.
    # mcp.run()  # Khởi động MCP server, lắng nghe và xử lý các tool invocation
    # Chạy qua port
    mcp.run(transport="http", port=8080)