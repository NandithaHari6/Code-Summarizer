import tiktoken
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from transformers import AutoTokenizer

# # Load LLaMA 3 tokenizer (adjust model name if needed)
# llama_tokenizer = AutoTokenizer.from_pretrained("meta-llama/Meta-Llama-3-8B")

# # Token limit for LLaMA 3.3 70B (ChatGroq)
# TOKEN_LIMIT = 6000  

# def count_tokens(text):
#     """Returns the number of tokens in a given text."""
#     return len(llama_tokenizer.encode(text, add_special_tokens=False))

# def split_text_list(text_list, max_tokens=TOKEN_LIMIT):
#     """Splits a list of text summaries while maintaining context within token limits."""
    
#     text_splitter = RecursiveCharacterTextSplitter(chunk_size=max_tokens, chunk_overlap=200)  
#     split_chunks = []
#     curr_chunk=""
#     curr_token=0
#     i=0
#     while i<len(text_list):
#         text=text_list[i]
#         if count_tokens(text) > max_tokens:  # Only split if needed
#             split_chunks.extend(text_splitter.split_text(text))
#         else:
#             tokens=count_tokens(text)
#             if curr_token+tokens>max_tokens:
#                 curr_chunk+=text
#                 curr_token+=tokens
#             else:
#                 split_chunks.append(curr_chunk)
#                 curr_chunk=text
#                 curr_token=tokens
#         i+=1


#     return split_chunks  # Returns list of token-limited chunks

# def recursive_reduce(llm, summaries):
#     """Recursively reduces summaries while keeping token size within limits."""
    
#     # Step 1: Ensure each chunk is under TOKEN_LIMIT
#     reduced_summaries = split_text_list(summaries)
    
#     # Step 2: Apply reduce phase iteratively until we get a single summary
#     while len(reduced_summaries) > 1:
#         new_summaries = []
        
#         for i in range(0, len(reduced_summaries)):  # Process in pairs
#             chunk_group = reduced_summaries[i]
            
#             reduce_prompt = f"""Summarize the following code summaries into a concise, well-structured summary:  
#             {chunk_group}  
            
#             Return the summary in **valid JSON format** as follows:  

#             {{
#               "title": "Project title",
#               "techStack": {{
#                 "ProgrammingLanguages": ["List of languages"],
#                 "FrameworksLibraries": ["List of frameworks/libraries"],
#                 "Tools": ["List of tools"]
#               }},
#               "overview": "Brief explanation of the project.",
#               "fileStructure": [
#                 {{
#                   "title": "Folder or File Name",
#                   "description": "Purpose and functionality."
#                 }}
#               ]
#             }}
#             """
            
#             # Invoke LLM on reduced chunk
#             reduced_summary = llm.invoke(reduce_prompt).content  
#             new_summaries.append(reduced_summary)
        
#         reduced_summaries = new_summaries  # Update summaries for next iteration

#     return reduced_summaries[0]  # Final summarized output


# def split_text_list(summaries, token_limit=1000):
#     """
#     Splits a list of large summaries into smaller, contextually meaningful chunks
#     within the given token limit.
#     """
#     text_splitter = RecursiveCharacterTextSplitter(
#         chunk_size=token_limit,  # Max tokens per chunk
#         chunk_overlap=500,       # Ensures some context is carried over
#         length_function=count_tokens  # Uses actual token count
#     )
    
#     # Combine summaries into one large text block (if necessary)
#     full_text = "\n".join(summaries)
    
#     # Split into chunks
#     split_chunks = text_splitter.split_text(full_text)

#     return split_chunks
def count_tokens(text):
    """Returns the approximate number of tokens in a text."""
   
    encoding = tiktoken.get_encoding("cl100k_base")  # OpenAI GPT-4 tokenizer
    return len(encoding.encode(text))
   # Fallback: word count approximation

# def split_text_list(res, max_tokens=2000):
#     """
#     Splits a list of summary strings into groups, each within the token limit.
#     Ensures that combined chunks do not exceed `max_tokens`.
#     """
#     chunks = []
#     current_chunk = []
#     current_tokens = 0

#     for summary in res:
#         tokens = count_tokens(summary)

#         # If adding this summary exceeds max tokens, start a new chunk
#         if current_tokens + tokens > max_tokens:
#             chunks.append("\n\n".join(current_chunk))  # Store the current chunk
#             current_chunk = [summary]  # Start a new chunk
#             current_tokens = tokens
#         else:
#             current_chunk.append(summary)
#             current_tokens += tokens

#     # Add the last chunk if not empty
#     if current_chunk:
#         chunks.append("\n\n".join(current_chunk))

#     return chunks

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
# if __name__=="__main__":
#     print(count_tokens("HEllo world"))
 