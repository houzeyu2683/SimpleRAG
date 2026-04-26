from __future__ import annotations
from collections import Counter
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

import fitz  # PyMuPDF
import pdfplumber
import structlog

log = structlog.get_logger()


class ChunkType(str, Enum):
    text = "text"
    table = "table"
    image_caption = "image_caption"


@dataclass
class ParsedChunk:
    text: str
    page: int
    chunk_type: ChunkType
    metadata: dict = field(default_factory=dict)


@dataclass
class ParseResult:
    chunks: list[ParsedChunk]
    page_count: int
    image_dir: Path


# ── Font-size heading detection ───────────────────────────────────────────────

def _collect_body_font_size(doc: fitz.Document) -> float:
    """Return the modal (most common) font size — this is the body text size."""
    sizes: list[float] = []
    for page in doc:
        for block in page.get_text("dict")["blocks"]:
            if block.get("type") != 0:
                continue
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    if span["text"].strip():
                        sizes.append(round(span["size"], 1))
    if not sizes:
        return 11.0
    return Counter(sizes).most_common(1)[0][0]


def _heading_level(font_size: float, body_size: float) -> int:
    """0 = body text, 1 = H1, 2 = H2."""
    if body_size <= 0:
        return 0
    ratio = font_size / body_size
    if ratio >= 1.4:
        return 1
    if ratio >= 1.15:
        return 2
    return 0


# ── Table extraction (pdfplumber) ─────────────────────────────────────────────

def _extract_tables(pdf_path: Path) -> dict[int, list[str]]:
    """Extract tables per page, returns Markdown-formatted strings keyed by page."""
    tables_by_page: dict[int, list[str]] = {}
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            tables = page.extract_tables()
            if not tables:
                continue
            md_tables = []
            for table in tables:
                if not table:
                    continue
                rows = [[cell or "" for cell in row] for row in table if row]
                if len(rows) < 2:
                    continue
                header = "| " + " | ".join(rows[0]) + " |"
                separator = "| " + " | ".join(["---"] * len(rows[0])) + " |"
                body = "\n".join("| " + " | ".join(row) + " |" for row in rows[1:])
                md_tables.append("\n".join([header, separator, body]))
            if md_tables:
                tables_by_page[page_num] = md_tables
    return tables_by_page


def _table_rects(pdf_path: Path) -> dict[int, list[fitz.Rect]]:
    """Return bounding boxes of table regions per page (to skip in text extraction)."""
    rects_by_page: dict[int, list[fitz.Rect]] = {}
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            rects = []
            for table in page.find_tables():
                b = table.bbox  # (x0, top, x1, bottom)
                rects.append(fitz.Rect(b[0], b[1], b[2], b[3]))
            rects_by_page[page_num] = rects
    return rects_by_page


# ── Image extraction ──────────────────────────────────────────────────────────

def _extract_images(doc: fitz.Document, image_dir: Path) -> None:
    """Save embedded images as PNG files."""
    image_dir.mkdir(parents=True, exist_ok=True)
    for page_num, page in enumerate(doc, start=1):
        for img_index, img in enumerate(page.get_images(full=True), start=1):
            xref = img[0]
            pix = fitz.Pixmap(doc, xref)
            if pix.n > 4:
                pix = fitz.Pixmap(fitz.csRGB, pix)
            pix.save(str(image_dir / f"page{page_num}_img{img_index}.png"))


# ── Section grouping ──────────────────────────────────────────────────────────

def _group_into_sections(
    doc: fitz.Document,
    tables_by_page: dict[int, list[str]],
    table_rects_by_page: dict[int, list[fitz.Rect]],
) -> list[ParsedChunk]:
    """
    Walk every page block-by-block, detect headings by font size, and group
    consecutive body blocks under the same heading into one ParsedChunk.
    Tables are inserted as separate ParsedChunk(table) entries.
    """
    body_size = _collect_body_font_size(doc)

    # Flat sequence of raw items before grouping:
    #   ("heading", level, text, page) | ("body", text, page) | ("table", md, page)
    raw: list[tuple] = []

    for page_num, page in enumerate(doc, start=1):
        table_rects = table_rects_by_page.get(page_num, [])

        # Insert tables for this page first (they appear above any text extracted
        # from the same page since pdfplumber ordering already reflects layout)
        for md_table in tables_by_page.get(page_num, []):
            raw.append(("table", md_table, page_num))

        for block in page.get_text("dict")["blocks"]:
            if block.get("type") != 0:  # skip image xobjects
                continue

            block_rect = fitz.Rect(block["bbox"])
            if any(block_rect.intersects(tr) for tr in table_rects):
                continue  # already captured by pdfplumber

            # Collect block text and dominant font size
            lines_text: list[str] = []
            max_font = 0.0
            for line in block.get("lines", []):
                parts = []
                for span in line.get("spans", []):
                    t = span["text"]
                    if t.strip():
                        max_font = max(max_font, span["size"])
                    parts.append(t)  # keep whitespace spans for proper word spacing
                line_str = "".join(parts).strip()
                if line_str:
                    lines_text.append(line_str)

            block_text = " ".join(lines_text).strip()
            if not block_text:
                continue

            level = _heading_level(max_font, body_size)
            if level > 0:
                raw.append(("heading", level, block_text, page_num))
            else:
                raw.append(("body", block_text, page_num))

    # ── Group raw items into sections ─────────────────────────────────────────
    chunks: list[ParsedChunk] = []
    cur_heading = ""
    cur_level = 1
    cur_body: list[str] = []
    cur_page = 1

    def flush() -> None:
        nonlocal cur_heading, cur_body, cur_page
        body = "\n\n".join(cur_body).strip()
        if not body and not cur_heading:
            return
        if cur_heading:
            prefix = "#" * cur_level + " " + cur_heading
            text = f"{prefix}\n\n{body}" if body else prefix
        else:
            text = body
        if text.strip():
            chunks.append(ParsedChunk(text=text.strip(), page=cur_page, chunk_type=ChunkType.text))
        cur_heading = ""
        cur_body = []

    for item in raw:
        kind = item[0]
        if kind == "table":
            flush()
            _, md_table, page_num = item
            chunks.append(ParsedChunk(text=md_table, page=page_num, chunk_type=ChunkType.table))
        elif kind == "heading":
            flush()
            _, level, text, page_num = item
            cur_heading = text
            cur_level = level
            cur_page = page_num
        else:  # body
            _, text, page_num = item
            if not cur_body and not cur_heading:
                cur_page = page_num
            cur_body.append(text)

    flush()
    return chunks


# ── Public API ────────────────────────────────────────────────────────────────

def parse_pdf(pdf_path: Path, file_id: str, data_dir: Path) -> ParseResult:
    image_dir = data_dir / file_id / "images"
    log.info("pdf.parse.start", file_id=file_id, path=str(pdf_path))

    tables_by_page = _extract_tables(pdf_path)
    rect_by_page = _table_rects(pdf_path)

    with fitz.open(str(pdf_path)) as doc:
        page_count = len(doc)
        _extract_images(doc, image_dir)
        chunks = _group_into_sections(doc, tables_by_page, rect_by_page)

    log.info("pdf.parse.done", file_id=file_id, chunks=len(chunks), pages=page_count)
    return ParseResult(chunks=chunks, page_count=page_count, image_dir=image_dir)
