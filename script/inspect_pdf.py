"""
inspect_pdf.py — 檢查 PDF 擷取品質
用法: python script/inspect_pdf.py <pdf_path> [page_number]
"""

import sys
import pdfplumber


def inspectText(path: str, page: int = 0):
    """擷取指定頁的純文字"""
    with pdfplumber.open(path) as pdf:
        text = pdf.pages[page].extract_text()
    print(f"=== 文字 (第 {page + 1} 頁) ===")
    print(text)


def inspectTables(path: str, page: int = 0):
    """擷取指定頁的所有表格"""
    with pdfplumber.open(path) as pdf:
        tables = pdf.pages[page].extract_tables()
    print(f"=== 表格 (第 {page + 1} 頁，共 {len(tables)} 個) ===")
    for i, table in enumerate(tables):
        print(f"\n--- 表格 {i + 1} ---")
        for row in table:
            print(row)


def inspectAll(path: str, page: int = 0):
    """同時顯示文字和表格"""
    inspectText(path, page)
    print()
    inspectTables(path, page)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python script/inspect_pdf.py <pdf_path> [page_number]")
        sys.exit(1)

    pdf_path = sys.argv[1]
    page_num = int(sys.argv[2]) - 1 if len(sys.argv) >= 3 else 0

    inspectAll(pdf_path, page_num)
