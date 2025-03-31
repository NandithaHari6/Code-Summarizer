from git import Repo
import stat
from langchain_community.document_loaders.generic import GenericLoader
from langchain_community.document_loaders.parsers import LanguageParser
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
from controllers.redis_cache import save_file_structure_to_redis, load_file_structure_from_redis, delete_docs_from_redis
import shutil
import requests

load_dotenv()
import time
from collections import deque
import os

import time
from fpdf import FPDF

import io

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
    return 


def get_default_branch(repo_owner: str, repo_name: str) -> str:
    """Fetch the default branch of a GitHub repository."""
    api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}"
    response = requests.get(api_url)
   
    if response.status_code == 200:
        return response.json().get("default_branch")  # Fallback to 'main'
    else:
        raise ValueError(f"Failed to fetch default branch: {api_url}")

def load_single_file(repo_link: str, file_path: str):
    """Load a single file from a GitHub repository using its default branch."""
    repo_owner, repo_name = repo_link.rstrip('/').split('/')[-2:]

    # Get the actual default branch
    default_branch = get_default_branch(repo_owner, repo_name)
    
    # Construct the raw file URL dynamically
    raw_url = f"https://raw.githubusercontent.com/{repo_owner}/{repo_name}/{default_branch}/{file_path}"

    # Download file content
    response = requests.get(raw_url)
    if response.status_code != 200:
        raise ValueError(f"Failed to fetch file: {raw_url}")

    # Save temporarily
    temp_file_path = f"/tmp/{(file_path)}"
    with open(temp_file_path, "w", encoding="utf-8") as f:
        f.write(response.text)

    # Load using LanguageParser
    loader = GenericLoader.from_filesystem(
        "/tmp",
        glob=os.path.basename(file_path),
        parser=LanguageParser()
    )
    
    documents = loader.load()
    # print(len(documents))
    # Cleanup: remove temp file
    os.remove(temp_file_path)

    return documents
def remove_readonly(func, path, _):
    """Change the file permission to writable and retry deletion"""
    os.chmod(path, stat.S_IWRITE)
    func(path)


def delete_folder(repo_path):
    try:
        if os.path.exists(repo_path):
            print(f"Directory exists: {repo_path}. Deleting...")
            shutil.rmtree(repo_path,onerror=remove_readonly)
            # shutil.rmtree(repo_path)
            print(f"Deleted {repo_path}")
        else:
            print(f"Directory does not exist: {repo_path}")
    except OSError as e:
        print("Error: %s - %s." % (e.filename, e.strerror))
def get_directory_structure(repo_link, root_dir="/tmp/clonedfile", suffixes=[".py", ".js", ".jsx", ".cpp", ".java", ".c", ".cs", ".rs", ".rb"]):
    """Recursively generates a directory structure dictionary, including only files with specified suffixes."""
    
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
                sub_structure = build_structure(item_path)
                if sub_structure:  # Only add non-empty folders
                    structure[item] = sub_structure
            else:
                if any(item.endswith(suffix) for suffix in suffixes):
                    structure[item] = None  # Mark files as None
        return structure

    directory_structure = build_structure(root_dir)

    # Cache the structure in Redis
    save_file_structure_to_redis(repo_link, directory_structure)

    # Cleanup after processing
    if os.path.exists(root_dir):
        delete_folder(root_dir)

    return directory_structure
def create_pdf(summary_data: dict, repo_link: str, level: str) -> bytes:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Title
    pdf.set_font("Arial", style="B", size=16)
    pdf.cell(200, 10, "Project Summary", ln=True, align="C")
    pdf.ln(10)

    # Repo Link as Hyperlink
    pdf.set_font("Arial", size=12)
    pdf.cell(10, 10, f"Repository Link:   ", ln=True)
    pdf.set_text_color(0, 0, 255)  # Blue color for hyperlink
    pdf.cell(0, 10, repo_link, ln=True, link=repo_link)
    pdf.set_text_color(0, 0, 0)  # Reset color
    pdf.ln(5)

    # Summary Level
    pdf.cell(0, 10, f"Summary Level: {level}", ln=True)
    pdf.ln(5)

    # Add content from JSON
    for key, value in summary_data.items():
        pdf.set_font("Arial", style="B", size=12)
        if key == "projectTitle":
            pdf.cell(0, 10, "Project Title", ln=True)
        elif key == "techStack":
            pdf.cell(0, 10, "Tech Stack Used", ln=True)
        elif key == "fileOverview":
            pdf.cell(0, 10, "Important Modules", ln=True)
        elif key == "projectOverview":
            pdf.cell(0, 10, "Summary", ln=True)
        
        pdf.set_font("Arial", size=11)

        if isinstance(value, str) and "\n" in value:
            for line in value.split("\n"):
                pdf.multi_cell(0, 8, line)
        else:
            pdf.multi_cell(0, 8, str(value))
        
        pdf.ln(5)

    print("Created PDF")
    
    # ✅ Get PDF as bytes directly
    return pdf.output(dest="S").encode("latin1")
# def get_directory_structure(repo_link, root_dir="/tmp/clonedfile"):
#     """Recursively generates a directory structure dictionary, ignoring hidden files."""
    
#     # Check Redis cache first
#     cached_docs = load_file_structure_from_redis(repo_link)
    
#     if cached_docs:
#         return cached_docs["file_structure"]
    
#     # Clone repository only if not already cloned
#     elif not os.path.exists(root_dir):
#         Repo.clone_from(repo_link, to_path=root_dir)

#     def build_structure(directory):
#         structure = {}
#         for item in os.listdir(directory):
#             if item.startswith("."):  # Ignore hidden files and folders
#                 continue
            
#             item_path = os.path.join(directory, item)
#             if os.path.isdir(item_path):
#                 structure[item] = build_structure(item_path)  # Recurse correctly
#             else:
#                 structure[item] = None  # Mark files as None
#         return structure

#     directory_structure = build_structure(root_dir)

#     # Cache the structure in Redis
#     save_file_structure_to_redis(repo_link, directory_structure)

#     # Cleanup after processing
#     if os.path.exists(root_dir):
#         delete_folder(root_dir)

#     return directory_structure


def code_snippet_summary(code_snippet):
    llm=instantiate_llm()
   
    reduce_template = """The following in a small code snippet {code}. Explain the working and  functionality accurately, in detail. Don't use more than 200 words. Return as plain text , no need of any formatting. 
    """
    reduce_prompt = PromptTemplate.from_template(reduce_template)
    reduce_chain=reduce_prompt |llm
    final_sum=reduce_chain.invoke({"code":code_snippet})
    print(final_sum.content)
    while True:
        try:
            final_sum=reduce_chain.invoke({"code":code_snippet}) 
            break
        except Exception as e:
            print(e)
            llm= instantiate_llm()
            reduce_chain=reduce_prompt|llm
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