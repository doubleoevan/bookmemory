from __future__ import annotations

import re


PARAGRAPH_SEPARATOR = "\n\n"
DEFAULT_MAX_CHARACTERS = 1200
DEFAULT_MIN_CHARACTERS = 200


def chunk_text(
    *,
    text: str,
    max_chars: int = DEFAULT_MAX_CHARACTERS,
    min_chars: int = DEFAULT_MIN_CHARACTERS,
) -> list[str]:
    """
    Chunks text deterministically by paragraph:
    - split on blank lines
    - pack paragraphs until max_chars
    - hard-split any giant paragraph
    """
    # trim whitespace and collapse 3+ newlines into a single blank line
    normalized_text = text.strip()
    normalized_text = re.sub(r"\n{3,}", PARAGRAPH_SEPARATOR, normalized_text)

    # break normalized text into paragraphs
    paragraphs = [
        paragraph.strip()
        for paragraph in normalized_text.split(PARAGRAPH_SEPARATOR)
        if paragraph.strip()
    ]

    # append paragraphs to a buffer and emit a chunk when adding the next paragraph would exceed the limit
    chunks: list[str] = []
    buffer: list[str] = []
    buffer_length = 0

    def add_chunk() -> None:
        nonlocal buffer, buffer_length
        if not buffer:
            return

        # normalize the buffer contents and merge adjacent blank lines
        buffer_chunk = PARAGRAPH_SEPARATOR.join(buffer).strip()
        buffer_chunk = re.sub(
            r"\n[ \t]*\n(?:[ \t]*\n)+",
            PARAGRAPH_SEPARATOR,
            buffer_chunk,
        )

        # add the buffer chunk if it isn't empty
        if buffer_chunk:
            chunks.append(buffer_chunk)
        buffer = []
        buffer_length = 0

    for paragraph in paragraphs:
        # add any buffered chunk first so an oversized paragraph gets split into its own chunk(s)
        if len(paragraph) > max_chars:
            add_chunk()

            # split an oversized paragraph into max_chars sized chunks
            start = 0
            while start < len(paragraph):
                end = min(start + max_chars, len(paragraph))
                paragraph_chunk = paragraph[start:end].strip()
                if paragraph_chunk:
                    chunks.append(paragraph_chunk)
                start = end
            continue

        # append to the current buffer or write to the next chunk if it is full
        separator_length = len(PARAGRAPH_SEPARATOR) if buffer else 0
        if buffer_length + separator_length + len(paragraph) <= max_chars:
            buffer.append(paragraph)
            buffer_length += separator_length + len(paragraph)
        else:
            add_chunk()
            buffer.append(paragraph)
            buffer_length = len(paragraph)

    # add any remaining chunks
    add_chunk()

    # merge small chunks into the previous chunk when possible
    merged_chunks: list[str] = []
    for chunk in chunks:
        if (
            merged_chunks
            and len(chunk) < min_chars
            and len(merged_chunks[-1]) + len(PARAGRAPH_SEPARATOR) + len(chunk)
            <= max_chars
        ):
            merged_chunks[-1] = merged_chunks[-1] + PARAGRAPH_SEPARATOR + chunk
        else:
            merged_chunks.append(chunk)

    return merged_chunks
