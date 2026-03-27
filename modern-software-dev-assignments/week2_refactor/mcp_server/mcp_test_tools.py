from simple_mcp import read_file_tool, list_files_tool, edit_file_tool

print(list_files_tool("."))

print(edit_file_tool("test.txt", "", "Hello MCP"))

print(read_file_tool("test.txt"))