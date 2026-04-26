from __future__ import annotations

SYSTEM_PROMPT = """You are a precise research assistant. Answer the user's question using ONLY the provided context from scientific documents.

Rules:
- Base your answer strictly on the context provided.
- If the context does not contain enough information, say so explicitly.
- Cite the source by referencing [Page X] inline when using information from a specific page.
- Be concise and accurate. Do not speculate beyond the context.
- When the user asks about a figure, chart, diagram, or image, include the page image in your response using Markdown syntax: ![Figure](url). Only include images that are directly relevant to the question."""


def build_messages(
    query: str,
    context_chunks: list[dict],
    history: list[dict] | None = None,
) -> list[dict]:
    context_parts = []
    for chunk in context_chunks:
        page = chunk.get("page", "?")
        text = chunk.get("text", "").strip()
        chunk_type = chunk.get("chunk_type", "text")
        file_id = chunk.get("file_id")

        label = "[Table]" if chunk_type == "table" else ""
        preview = ""
        if file_id and page != "?":
            url = f"/api/v1/documents/{file_id}/page?page={page}"
            preview = f"\n[Page image: ![Page {page}]({url})]"

        context_parts.append(f"[Page {page}]{label}\n{text}{preview}")

    context_str = "\n\n---\n\n".join(context_parts)

    messages: list[dict] = [{"role": "system", "content": SYSTEM_PROMPT}]

    if history:
        messages.extend(history)

    user_content = f"Context:\n{context_str}\n\nQuestion: {query}"
    messages.append({"role": "user", "content": user_content})

    return messages
