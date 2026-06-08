import re
from backend.models.schemas import TextChunk


def chunk_for_extraction(
    text: str,
    source_document: str,
    chunk_size: int = 2000,
    overlap: int = 200,
) -> list[TextChunk]:
    if len(text) <= chunk_size:
        return [
            TextChunk(
                chunk_index=0,
                text=text,
                start_char=0,
                end_char=len(text),
                source_document=source_document,
            )
        ]

    paragraphs = _split_paragraphs(text)
    chunks = []
    current_text = ""
    current_start = 0
    char_offset = 0

    for para in paragraphs:
        if len(current_text) + len(para) + 1 > chunk_size and current_text:
            chunks.append(
                TextChunk(
                    chunk_index=len(chunks),
                    text=current_text.strip(),
                    start_char=current_start,
                    end_char=current_start + len(current_text),
                    source_document=source_document,
                )
            )
            overlap_text = current_text[-overlap:] if overlap > 0 else ""
            current_start = current_start + len(current_text) - len(overlap_text)
            current_text = overlap_text

        if len(para) > chunk_size:
            if current_text:
                chunks.append(
                    TextChunk(
                        chunk_index=len(chunks),
                        text=current_text.strip(),
                        start_char=current_start,
                        end_char=current_start + len(current_text),
                        source_document=source_document,
                    )
                )
                current_start = current_start + len(current_text)
                current_text = ""

            sentence_chunks = _split_by_sentences(para, chunk_size, overlap)
            for sc in sentence_chunks:
                chunks.append(
                    TextChunk(
                        chunk_index=len(chunks),
                        text=sc,
                        start_char=current_start,
                        end_char=current_start + len(sc),
                        source_document=source_document,
                    )
                )
                current_start += len(sc) - overlap
        else:
            if current_text:
                current_text += "\n\n" + para
            else:
                current_text = para

        char_offset += len(para)

    if current_text.strip():
        chunks.append(
            TextChunk(
                chunk_index=len(chunks),
                text=current_text.strip(),
                start_char=current_start,
                end_char=current_start + len(current_text),
                source_document=source_document,
            )
        )

    return chunks


def _split_paragraphs(text: str) -> list[str]:
    paragraphs = re.split(r"\n\s*\n", text)
    return [p.strip() for p in paragraphs if p.strip()]


def _split_by_sentences(
    text: str, chunk_size: int, overlap: int
) -> list[str]:
    sentences = re.split(r"(?<=[.!?])\s+", text)
    chunks = []
    current = ""

    for sent in sentences:
        if len(current) + len(sent) + 1 > chunk_size and current:
            chunks.append(current.strip())
            overlap_text = current[-overlap:] if overlap > 0 else ""
            current = overlap_text + " " + sent
        else:
            current = (current + " " + sent).strip() if current else sent

    if current.strip():
        chunks.append(current.strip())

    return chunks
