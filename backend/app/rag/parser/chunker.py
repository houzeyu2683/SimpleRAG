from __future__ import annotations
from dataclasses import dataclass

from app.core.config import get_settings
from app.rag.parser.pdf_parser import ChunkType, ParsedChunk

settings = get_settings()


def _split_text(text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
    """Split long text by paragraphs first, then sentences, with overlap."""
    if len(text) <= chunk_size:
        return [text]

    separators = ["\n\n", "\n", ". ", " "]
    for sep in separators:
        if sep not in text:
            continue
        parts = text.split(sep)
        chunks: list[str] = []
        current = ""
        for part in parts:
            candidate = (current + sep + part) if current else part
            if len(candidate) <= chunk_size:
                current = candidate
            else:
                if current:
                    chunks.append(current)
                current = part
        if current:
            chunks.append(current)

        if len(chunks) <= 1:
            continue

        # Apply overlap
        if chunk_overlap > 0 and len(chunks) > 1:
            overlapped = [chunks[0]]
            for i in range(1, len(chunks)):
                tail = overlapped[-1][-chunk_overlap:]
                overlapped.append(tail + chunks[i])
            return [c.strip() for c in overlapped if c.strip()]
        return [c.strip() for c in chunks if c.strip()]

    # Fallback: hard split
    return [text[i: i + chunk_size] for i in range(0, len(text), chunk_size - chunk_overlap)]


@dataclass
class TextChunk:
    text: str
    file_id: str
    page: int
    chunk_type: ChunkType
    chunk_index: int
    metadata: dict


def chunk_parsed_document(
    parsed_chunks: list[ParsedChunk],
    file_id: str,
    collection_name: str,
) -> list[TextChunk]:
    result: list[TextChunk] = []
    chunk_index = 0
    max_size = settings.rag_chunk_size
    overlap = settings.rag_chunk_overlap

    for parsed in parsed_chunks:
        base_meta = {**parsed.metadata, "collection": collection_name}

        if parsed.chunk_type == ChunkType.table:
            # Tables are never split
            result.append(TextChunk(
                text=parsed.text,
                file_id=file_id,
                page=parsed.page,
                chunk_type=parsed.chunk_type,
                chunk_index=chunk_index,
                metadata=base_meta,
            ))
            chunk_index += 1
            continue

        text = parsed.text.strip()
        if not text:
            continue

        if len(text) <= max_size:
            result.append(TextChunk(
                text=text,
                file_id=file_id,
                page=parsed.page,
                chunk_type=parsed.chunk_type,
                chunk_index=chunk_index,
                metadata=base_meta,
            ))
            chunk_index += 1
        else:
            # Extract heading prefix so each sub-chunk retains context
            heading_prefix = ""
            body = text
            first_newline = text.find("\n\n")
            if text.startswith("#") and first_newline != -1:
                heading_prefix = text[:first_newline + 2]  # "## Title\n\n"
                body = text[first_newline + 2:]

            sub_texts = _split_text(body, max_size - len(heading_prefix), overlap)
            for sub in sub_texts:
                if not sub.strip():
                    continue
                result.append(TextChunk(
                    text=heading_prefix + sub,
                    file_id=file_id,
                    page=parsed.page,
                    chunk_type=parsed.chunk_type,
                    chunk_index=chunk_index,
                    metadata=base_meta,
                ))
                chunk_index += 1

    return result
