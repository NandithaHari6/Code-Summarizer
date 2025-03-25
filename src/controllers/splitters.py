import tiktoken
def count_token_as_len(text):
    return len(text)
def count_tokens(text):
    """Returns the approximate number of tokens in a text."""
   
    encoding = tiktoken.get_encoding("cl100k_base")  # OpenAI GPT-4 tokenizer
    return len(encoding.encode(text))
def split_document(doc, max_tokens=5000):
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
def split_res(doc, max_tokens=3000):
    """
    Splits a document into smaller parts, each with fewer than `max_tokens`.
    Uses token-based splitting if tiktoken is available, otherwise word-based.
    """
    res=" "
    print(doc)
    for ele in doc:
        res+=ele["summary"]

    
    tokens = count_tokens(res)

    if tokens <= max_tokens:
        return res  # No need to split if within limit

    parts = []
    num_parts = (tokens // max_tokens) + 1  # Calculate number of splits
    chunk_size = len(res) // num_parts  # Approximate text split by length

    for i in range(num_parts):
        start = i * chunk_size
        end = (i + 1) * chunk_size if i < num_parts - 1 else len(doc)
        part_content =res[start:end]

        # Create a new Document object while preserving metadata
        
        parts.append(part_content)
    print(parts[0])
    print(type(parts[0]))
    return parts
# if __name__=="__main__":
#     print(count_tokens("HEllo world"))
 