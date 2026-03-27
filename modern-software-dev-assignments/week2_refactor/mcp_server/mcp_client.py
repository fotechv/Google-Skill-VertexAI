import asyncio
from fastmcp import Client

# python # Connect to FastMCP server client = Client("http://localhost:8080")
# List available resources resources = await client.list_resources()
# Call a tool result = await client.call_tool("my_tool", {"param": "value"})

# client = Client("SimpleMCPTestServer")
# client = Client("http://localhost:8080")

async def main():
    # Kết nối tới MCP server
    # client = Client("http://localhost:8080")  #
    client = Client("http://127.0.0.1:8080")
    print(client)

    async with client:
        print("=== Connected to MCP Server ===\n")

        # 1️⃣ List available tools
        tools = await client.list_tools()

        print("=== Available Tools ===")
        for tool in tools:
            print(f"- Name: {tool.name}")
            print(f"  Description: {tool.description}")
            print(f"  Input Schema: {tool.input_schema}")
            print()

        # 2️⃣ (Optional) Gọi thử tool đầu tiên nếu có
        if tools:
            first_tool = tools[0]
            print(f"=== Calling tool: {first_tool.name} ===")

            # Ví dụ truyền param rỗng (tuỳ tool yêu cầu)
            result = await client.call_tool(first_tool.name, {})

            print("Result:")
            print(result)

if __name__ == "__main__":
    asyncio.run(main())
