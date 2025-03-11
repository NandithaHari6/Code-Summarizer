from git import Repo
import stat
from langchain_community.document_loaders.generic import GenericLoader
from langchain_community.document_loaders.parsers import LanguageParser

from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
from controllers.splitters import  split_document,count_tokens
from controllers.redis_cache import save_file_structure_to_redis, load_file_structure_from_redis,save_docs_to_redis, load_docs_from_redis, delete_docs_from_redis
import shutil
import requests
from queue import Queue
load_dotenv()
import time
from collections import deque
import os

import tiktoken 
import time
API_KEYS=[os.getenv("groq_api_key"),os.getenv("groq_api_key_2"),os.getenv("groq_api_key_3")]
queue = deque([(i, time.time()) for i in range(len(API_KEYS))])

def load_docs(repo_link:str,repo_path:str):    
    repo = Repo.clone_from(repo_link, to_path=repo_path)
    loader = GenericLoader.from_filesystem(
        repo_path ,

        glob="**/*",
        suffixes=[".py",".js",".jsx",".cpp",".java",".c",".cs",".rs",".rb"],
        # exclude=["**/non-utf8-encoding.py"],
        parser=LanguageParser(),
    )
    documents = loader.load()
    return documents
def instantiate_llm():
    global queue
    while queue:
        index, available_time = queue.popleft()
        if available_time <= time.time():
            llm = ChatGroq(
                temperature=0,
                groq_api_key=API_KEYS[index],
                model_name="llama-3.3-70b-versatile"
            )
            print("Index used", index)
            queue.append((index, time.time() + 120))  # Re-add with 2s delay
            return llm
        else:
            time.sleep(available_time - time.time())
            llm = ChatGroq(
                temperature=0,
                groq_api_key=API_KEYS[index],
                model_name="llama-3.3-70b-versatile"
            )
            print("Index used", index)
            queue.append((index, time.time() + 120))  # Re-add with 2s delay
            return llm
    return llm
# def map_phase(llm,documents):
#     map_template = """You are a senior software engineer working on this project, with experience of handling various code bases, in different programming languages. Explain the functionality of the code to a junior software developer, who recently joined your team and is viewing this code base for the first time 
#     {docs}
#     Explain in just 2 to 3 sentences,just the thing in the code alone. Do not add your own logic  .Do not include meta data information and code snippet . Just the sentence explaination is enough"""
#     map_prompt = PromptTemplate.from_template(map_template)
#     map_chain = map_prompt |llm
#     i=0
#     res=[0]*len(documents)

#     while i<len(documents):
#     #    print(map_chain.invoke({"docs":documents[i]}).content)

#         print(documents[i].metadata)
#         try:
#             res[i]=map_chain.invoke({"docs":documents[i]}).content
#             i+=1
#         except Exception as e:
#             print(e)
#             print("Calling new llm")
#             llm=instantiate_llm()
#             map_chain = map_prompt |llm
#     return res
    # Reduce
# Uncomment if using OpenAI models

def map_phase(llm, documents, repo_link):
    """Processes documents, stores summaries in Redis, and resumes if interrupted."""
    map_template = """You are a senior software engineer working on this project, with experience handling various code bases in different programming languages. Explain the functionality of the code to a junior developer viewing this code base for the first time.
    {docs}
    Explain in just 2 to 3 sentences,not exceeding 150 words, only describing the code functionality,any important tech stacks, tools or frameworks used. Do not add your own logic, metadata, or code snippets."""
    
    map_prompt = PromptTemplate.from_template(map_template)
    map_chain = map_prompt | llm

    # Load cached results
    cached_data = load_docs_from_redis(repo_link)
    cached_res = cached_data.get("res") if cached_data else []
    completed = cached_data.get("completed") if cached_data else False

    # If already completed, return cached results
    if completed:
        return cached_res

    i = len(cached_res)   # Start from where it left off

    while i < len(documents):
        doc = documents[i]
        print(doc.metadata)

        try:
            response = map_chain.invoke({"docs": doc}).content

            # Store only metadata and summary
            cached_res.append({"metadata": doc.metadata, "summary": response})

            # Save progress in Redis
            save_docs_to_redis(repo_link, cached_res, completed=False)
            i += 1
        except Exception as e:
            print(e)
            if "413" in str(e):  # Check if error is 413 (Payload Too Large)
                print(f"Splitting document: {doc.metadata}")
                split_docs = split_document(doc)
                documents[i:i+1] = split_docs
            else:
                print("Calling new LLM instance")
                llm = instantiate_llm()
                map_chain = map_prompt | llm

    # Mark as completed
    save_docs_to_redis(repo_link, cached_res, completed=True)
    return cached_res
# def reduce_phase_folder_sum(llm, res_list:list,file_structure):
#     """
#     Iteratively reduces a list of summaries to a final summary using token-limited chunking.
#     """
#     reduce_template  = """The following is a collection of summaries from various small code snippets that together form a single project:  
# {docs}  . The folder structure of the project rep is {file_structure}.

# Analyze these snippets, extract the core themes, and distill them into a final, well-structured summary.  

# The final summary should follow this format:  
# - *Project Title:* A concise and descriptive title reflecting the project's purpose.  
# - *Tech Stack Used:* List the programming languages, frameworks, libraries, and tools utilized.  
# - *Project Overview:* A brief explanation of the project's goal, functionality, and intended audience.  
# - *File & Folder Breakdown:* A structured summary of the project's key directories and files, along with their roles.
#  """
#     res=[]
#     for ele in res_list:
#         res.append(ele["summary"])
#     # print(f"res is {res}")
#     llm = instantiate_llm()
#     reduce_prompt = PromptTemplate.from_template(reduce_template)
#     reduce_chain = reduce_prompt | llm

#     # Step 1: Split `res` into token-limited chunks
#     res_chunks = split_text_list(res)
#     print(f" len of res_chunks is {len(res_chunks)}")
#     i=0
#     summary_store = " "
#     while i<len(res_chunks) :  # Keep summarizing until we get a single summary
        
        
#         chunk=res_chunks[i]
#         print(count_tokens(chunk))
#         try:
#             summary = reduce_chain.invoke({"docs": chunk,"file_structure":file_structure}).content
#             print(f"Summary is {summary}")
#             summary_store+=(summary)
#             print(summary)
#             i+=1
            
#         except Exception as e:
#             print(e)
#             if "413" in str(e):  # If payload is too large, split again
#                 print("Splitting text due to token limit exceeded.")
#                 split_chunks = split_text_list([chunk])  # Split the large chunk
#                 res_chunks[i:i+1]=(split_chunks)
                
#             else:
#                 print(e)
#                 llm = instantiate_llm()
#                 reduce_chain = reduce_prompt | llm
        
    
        

#     return summary_store

def split_res(doc, max_tokens=5000):
    """
    Splits a document into smaller parts, each with fewer than `max_tokens`.
    Uses token-based splitting if tiktoken is available, otherwise word-based.
    """
    res=("\n").join(doc)
    
    tokens = count_tokens(doc)

    if tokens <= max_tokens:
        return doc  # No need to split if within limit

    parts = []
    num_parts = (tokens // max_tokens) + 1  # Calculate number of splits
    chunk_size = len(doc) // num_parts  # Approximate text split by length

    for i in range(num_parts):
        start = i * chunk_size
        end = (i + 1) * chunk_size if i < num_parts - 1 else len(doc)
        part_content =doc[start:end]

        # Create a new Document object while preserving metadata
        
        parts.append(part_content)

    return parts
def reduce_large_folder(res):
    
    map_reduce_template=''' The following is a collection of summaries from various small code snippets that together form a single project:  
{res}  .

Analyze these snippets, extract the core themes, and distill them into a final summary within strictly 100 words'''
    llm=instantiate_llm()
    reduce_prompt = PromptTemplate.from_template(map_reduce_template)
    reduce_chain=reduce_prompt |llm
    
    flag=0
    new_res=[]
    i=0
    split_res_array=split_res(res)
    llm=instantiate_llm()
    map_reduce_prompt = PromptTemplate.from_template(map_reduce_template)
    map_reduce_chain=map_reduce_prompt |llm
    while i<len(split_res_array):
        try:
            new_res=map_reduce_chain.invoke({"res":split_res_array[i]}).content
            i+=1
        except:
            llm = instantiate_llm()
            map_reduce_chain = map_reduce_prompt | llm
        flag=0
    while True:
        try:
            final_sum=reduce_chain.invoke({"docs":new_res})
            break
        except Exception as e:
            llm = instantiate_llm()
            reduce_chain = reduce_prompt | llm


    return final_sum.content   
def reduce_phase_folder_sum(llm,res):
    reduce_template  = """The following is a collection of summaries from various small code snippets that together form a single project:  
{docs}  .

Analyze these snippets, extract the core themes, and distill them into a final, well-structured summary.  

The final summary should follow this format:  
- *Project Title:* A concise and descriptive title reflecting the project's purpose.  
- *Tech Stack Used:* List the programming languages, frameworks, libraries, and tools utilized.  
- *Project Overview:* A brief explanation of the project's goal, functionality, and intended audience.  
- *File & Folder Breakdown:* A structured summary of the project's key directories and files, along with their roles.
 """
    llm=instantiate_llm()
    reduce_prompt = PromptTemplate.from_template(reduce_template)
    reduce_chain=reduce_prompt |llm
    while True:
        try:
            final_sum=reduce_chain.invoke({"docs":res})
            break
        except Exception as e:
        
            if "413" in e:
                new_res=reduce_large_folder(res)
                res=new_res
            else:
                llm=instantiate_llm()
                reduce_chain=reduce_prompt |llm
            

    return final_sum.content
def reduce_phase_file_sum(llm,documents,file_path):
    j=0
    code_snippet_doc=[0]
    code_snippet_sum=[0]
    for i in range(len(documents)):
            if file_path == documents[i].metadata['source']:
                code_snippet_doc[j]=documents[i]
                j=j+1 
    map_template = """You are a senior software engineer working on this project, with experience of handling various code bases, in different programming languages. Explain the functionality of the code to a junior software developer, who recently joined your team and is viewing this code base for the first time 
    {docs}
    Explain in just 2 to 3 sentences,just the thing in the code alone. Do not add your own logic  .Do not include meta data information and code snippet . Just the sentence explaination is enough"""
    map_prompt = PromptTemplate.from_template(map_template)
    map_chain = map_prompt |llm  
    i=0 
    while i<(len(code_snippet_doc)):
        try:
            code_snippet_sum[i]=map_chain.invoke(code_snippet_doc[i])
            i+=1
        except Exception as e:
            if "413" in str(e): 
                doc=code_snippet_doc[i] # Check if error is 413 (Payload Too Large)
                print(f"Splitting document: {doc.metadata}")
                split_docs = split_document(doc)
                code_snippet_doc[i:i+1] = split_docs
            else:
                llm=instantiate_llm()
                map_chain = map_prompt |llm  
    reduce_template = """The following is set of summaries of small code snippets of the file , {file_path} that is a part of a big project .
    {docs}
    Take thses and come up with a summmary of the functionality of the code in this file alone. Explain each function in detail. Don't use more than 200 words.
    """
    reduce_prompt = PromptTemplate.from_template(reduce_template)
    reduce_chain=reduce_prompt |llm
    while True:
        try:
            final_sum=reduce_chain.invoke({"docs":code_snippet_sum,"file_path":file_path})
            break
        except:
            llm=instantiate_llm()
            reduce_chain=reduce_prompt |llm
    return final_sum     
def load_single_file(repo_link: str, file_path: str):
    # Convert GitHub repo link to raw file URL
    repo_owner, repo_name = repo_link.rstrip('/').split('/')[-2:]
    raw_url = f"https://raw.githubusercontent.com/{repo_owner}/{repo_name}/main/{file_path}"  # Assumes 'main' branch
    # raw_url='https://raw.githubusercontent.com/NandithaHari6/Price-comparison-website/refs/heads/main/deleteDb.py'
    # Download file content
    response = requests.get(raw_url)
    if response.status_code != 200:
        raise ValueError(f"Failed to fetch file: {raw_url}")

    # Save temporarily
    temp_file_path = f"/tmp/{os.path.basename(file_path)}"
    with open(temp_file_path, "w", encoding="utf-8") as f:
        f.write(response.text)

    # Load using LanguageParser
    loader = GenericLoader.from_filesystem(
        "/tmp",
        glob=os.path.basename(file_path),
        parser=LanguageParser(),
    )
    
    documents = loader.load()

    # Cleanup: remove temp file
    os.remove(temp_file_path)

    return documents   
def reduce_phase_file_sum_from_res(llm,res, documents,file_path):
    j=0
    code_snippet_sum=[0]*len(documents)
  
    for i in range(len(res)):
        if file_path == res[i].metadata['source']:
            code_snippet_sum[j]=res[i]
            j=j+1
        
    reduce_template = """The following is set of summaries of small code snippets of the file , {file_path} that is a part of a big project .
    {docs}
    Take thses and come up with a summmary of the functionality of the code in this file alone. Explain each function in detail. Don't use more than 200 words.
    """
    llm=instantiate_llm()
    reduce_prompt = PromptTemplate.from_template(reduce_template)
    reduce_chain=reduce_prompt |llm
    while True:
        try:
            final_sum=reduce_chain.invoke({"docs":code_snippet_sum,"file_path":file_path})
            break
        except:
            llm=instantiate_llm()
            reduce_chain=reduce_prompt |llm

    return final_sum        



def remove_readonly(func, path, _):
    """Change the file permission to writable and retry deletion"""
    os.chmod(path, stat.S_IWRITE)
    func(path)


def delete_folder(repo_path):
    try:
        if os.path.exists(repo_path):
            print(f"Directory exists: {repo_path}. Deleting...")
            shutil.rmtree(repo_path, onerror=remove_readonly)
            print(f"Deleted {repo_path}")
        else:
            print(f"Directory does not exist: {repo_path}")
    except OSError as e:
        print("Error: %s - %s." % (e.filename, e.strerror))
def get_directory_structure(repo_link, root_dir="/tmp/clonedfile"):
    """Recursively generates a directory structure dictionary, ignoring hidden files."""
    
    # Check Redis cache first
    cached_docs = load_file_structure_from_redis(repo_link)
    
    if cached_docs:
        return cached_docs["file_structure"]
    
    # Clone repository only if not already cloned
    elif not os.path.exists(root_dir):
        Repo.clone_from(repo_link, to_path=root_dir)

    def build_structure(directory):
        structure = {}
        for item in os.listdir(directory):
            if item.startswith("."):  # Ignore hidden files and folders
                continue
            item_path = os.path.join(directory, item)
            if os.path.isdir(item_path):
                structure[item] = build_structure(item_path)  # Recurse correctly
            else:
                structure[item] = None  # Mark files as None
        return structure

    directory_structure = build_structure(root_dir)

    # Cache the structure in Redis
    save_file_structure_to_redis(repo_link, directory_structure)

    # Cleanup after processing
    if os.path.exists(root_dir):
        delete_folder(root_dir)

    return directory_structure


def generate_summary(repo_link: str,level,file_path=None) -> str:
    #Load documents
    repo_path = "/tmp/clonedfile"
    cached_docs = load_docs_from_redis(repo_link)
    documents={}
    print("Started running")
    llm=instantiate_llm()
    # print(cached_docs)
    if cached_docs:
        print("Loading data from Redis cache...")
        if cached_docs["completed"]:

            res = cached_docs["res"]
        else:
            docs = load_docs(repo_link, repo_path)
            res=map_phase(llm,docs,repo_link)
    elif level=="folder": 
        docs = load_docs(repo_link, repo_path)
        res=map_phase(llm,docs,repo_link)
        
    print("Len of documents")
    print(len(documents))
    #Map reduce
    if level=="folder":
        # file_structure=get_directory_structure(repo_link)
        print(f"res is {res[0]}")
        final_sum=reduce_phase_folder_sum(llm,res)
        print(final_sum)
    elif level=="file":
        if cached_docs:
            final_sum=reduce_phase_file_sum_from_res(llm,res,file_path)
            print(final_sum.content)
            final_sum=final_sum.content
        else:             
            extracted_path = file_path.replace("/tmp/clonedfile/", "", 1)
            documents=load_single_file(repo_link,extracted_path)
            print(len(documents))
            final_sum=reduce_phase_file_sum(llm,documents,file_path)
            print(final_sum.content) 
            final_sum=final_sum.content
    if os.path.exists(repo_path):
        delete_folder(repo_path)
    return final_sum
def code_snippet_summary(code_snippet):
    llm=instantiate_llm()
    reduce_template = """The following in a small code snippet {code}. Explain the working and  functionality accurately, in detail. Don't use more than 200 words.
    """
    reduce_prompt = PromptTemplate.from_template(reduce_template)
    reduce_chain=reduce_prompt |llm
    while True:
        try:
            final_sum=reduce_chain.invoke({"code":code_snippet}) 
            break
        except:
            llm= instantiate_llm()
            reduce_chain=reduce_prompt |llm   
    return final_sum.content
    
def close_repo(repo_link,repo_path=r"\tmp\clonedrepo"):
    delete_folder(repo_path)
    delete_docs_from_redis(repo_link)
    return 
     

if __name__=="__main__":
#     print(code_snippet_summary(""" {
#   "code": "s = 'malayalam'  # string\n\ni,j = 0, len(s) - 1  # two pointers\n\nis_palindrome = True  # assume palindrome\nwhile i < j:\n    if s[i] != s[j]:  # mismatch found\n        is_palindrome = False\n        break\n    i += 1\n    j -= 1\n\nif is_palindrome:\n    print(\"Yes\") \nelse:\n    print(\"No\")"
# }
# """))
    print(get_directory_structure("https://github.com/deepankarvarma/To-Do-List-Using-Python"))