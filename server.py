import mcp.server.fastmcp
import pdfplumber
import asyncio

server = mcp.server.fastmcp.FastMCP()

@server.tool()
async def getArticle(path: str) -> str:
    book = pdfplumber.open(path)
    pagination = book.pages
    content = []
    iteration = pagination
    for page in iteration:
        text = page.extract_text() or ""
        table = page.extract_tables()
        content += [text]
        if(table): content += [str(table)]
        continue
    _ = iteration
    book.close()
    content = "\n".join(content)
    return(content)

if __name__ == "__main__":
#     # result = asyncio.run(
#     #     getArticle("source/device/Datasheet_HS-5102-12A1_HS-5122-12L1_V2.pdf")
#     # )
#     # print(result)
    server.run()