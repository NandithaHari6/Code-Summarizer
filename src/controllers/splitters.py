import tiktoken

def count_tokens(text):
    """Returns the approximate number of tokens in a text."""
    try:
        encoding = tiktoken.get_encoding("cl100k_base")  # OpenAI GPT-4 tokenizer
        return len(encoding.encode(text))
    except ImportError:
        return len(text.split())  # Fallback: word count approximation

def split_text_list(res, max_tokens=3000):
    """
    Splits a list of summary strings into groups, each within the token limit.
    Ensures that combined chunks do not exceed `max_tokens`.
    """
    chunks = []
    current_chunk = []
    current_tokens = 0

    for summary in res:
        tokens = count_tokens(summary)

        # If adding this summary exceeds max tokens, start a new chunk
        if current_tokens + tokens > max_tokens:
            chunks.append("\n\n".join(current_chunk))  # Store the current chunk
            current_chunk = [summary]  # Start a new chunk
            current_tokens = tokens
        else:
            current_chunk.append(summary)
            current_tokens += tokens

    # Add the last chunk if not empty
    if current_chunk:
        chunks.append("\n\n".join(current_chunk))

    return chunks

def split_document(doc, max_tokens=6000):
    """
    Splits a document into smaller parts, each with fewer than `max_tokens`.
    Uses token-based splitting if tiktoken is available, otherwise word-based.
    """
    content = doc.page_content
    tokens = count_tokens(content)

    if tokens <= max_tokens:
        return [doc]  # No need to split if within limit

    parts = []
    num_parts = (tokens // max_tokens) + 1  # Calculate number of splits
    chunk_size = len(content) // num_parts  # Approximate text split by length

    for i in range(num_parts):
        start = i * chunk_size
        end = (i + 1) * chunk_size if i < num_parts - 1 else len(content)
        part_content = content[start:end]

        # Create a new Document object while preserving metadata
        part_doc = doc.__class__(page_content=part_content, metadata=doc.metadata)
        parts.append(part_doc)

    return parts