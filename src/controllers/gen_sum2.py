from git import Repo
import stat
from langchain_community.document_loaders.generic import GenericLoader
from langchain_community.document_loaders.parsers import LanguageParser
from langchain_text_splitters import Language
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
from controllers.redis_cache import save_file_structure_to_redis, load_file_structure_from_redis,save_docs_to_redis, load_docs_from_redis, delete_docs_from_redis
import shutil
import requests
from queue import Queue
load_dotenv()
import time
from collections import deque
import os
import time
from code-summarizer.API import API_KEYS
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
def map_phase(llm,documents):
    map_template = """You are a senior software engineer working on this project, with experience of handling various code bases, in different programming languages. Explain the functionality of the code to a junior software developer, who recently joined your team and is viewing this code base for the first time 
    {docs}
    Explain in just 2 to 3 sentences,just the thing in the code alone. Do not add your own logic  .Do not include meta data information and code snippet . Just the sentence explaination is enough"""
    map_prompt = PromptTemplate.from_template(map_template)
    map_chain = map_prompt |llm
    i=0
    res=[0]*len(documents)

    while i<len(documents):
    #    print(map_chain.invoke({"docs":documents[i]}).content)

        print(documents[i].metadata)
        try:
            res[i]=map_chain.invoke({"docs":documents[i]}).content
            i+=1
        except:
            print("Calling new llm")
            llm=instantiate_llm()
            map_chain = map_prompt |llm
    return res
    # Reduce
def reduce_phase_folder_sum(llm,res):
    reduce_template = """The following is set of summaries of small code snippets of that are part of a single project
    {docs}
    Take these and distill it into a final, consolidated summary of the main themes. 
    """
    llm=instantiate_llm()
    reduce_prompt = PromptTemplate.from_template(reduce_template)
    reduce_chain=reduce_prompt |llm

    final_sum=reduce_chain.invoke({"docs":res})
        
            

    return final_sum
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
        except:
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
        if file_path == documents[i].metadata['source']:
            code_snippet_sum[j]=res[i]
            j=j+1
        
    reduce_template = """The following is set of summaries of small code snippets of the file , {file_path} that is a part of a big project .
    {docs}
    Take thses and come up with a summmary of the functionality of the code in this file alone. Explain each function in detail. Don't use more than 200 words.
    """
    llm=instantiate_llm()
    reduce_prompt = PromptTemplate.from_template(reduce_template)
    reduce_chain=reduce_prompt |llm
    try:
        final_sum=reduce_chain.invoke({"docs":code_snippet_sum,"file_path":file_path})
    except:
        print("Error processing")
    return final_sum        



def remove_readonly(func, path, _):
    """Change the file permission to writable and retry deletion"""
    os.chmod(path, stat.S_IWRITE)
    func(path)


def delete_folder(repo_path):
    try:
        if os.path.exists(repo_path):
            print(f"Directory exists: {repo_path}. Deleting...")
            shutil.rmtree(repo_path,onerror=remove_readonly)
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
    else:
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
    
    llm=instantiate_llm()
    if cached_docs:
        print("Loading data from Redis cache...")
        documents = cached_docs["documents"]
        res = cached_docs["res"]
    elif not cached_docs and level=="folder": 
        docs = load_docs(repo_link, repo_path)
        res=map_phase(llm,docs)
       
        save_docs_to_redis(repo_link, docs,res)  # Store in Redis
        
    print("Len of documents")
    print(len(documents))
    #Map reduce
    if level=="folder":
        final_sum=reduce_phase_folder_sum(llm,res)
        print(final_sum.content)
    elif level=="file":
        if cached_docs:
            final_sum=reduce_phase_file_sum_from_res(llm,res,documents,file_path)
            print(final_sum.content)
        else:             
            extracted_path = file_path.replace("/tmp/cloned/", "", 1)
            documents=load_single_file(repo_link,extracted_path)
            final_sum=reduce_phase_file_sum(llm,documents,file_path)
            print(final_sum.content) 
    if os.path.exists(repo_path):
        delete_folder(repo_path)
    return final_sum.content
def code_snippet_summary(code_snippet):
    llm=instantiate_llm("Chatgroq")
    reduce_template = """The following in a small code snippet {code}. Explain the working and  functionality accurately, in detail. Don't use more than 200 words.
    """
    reduce_prompt = PromptTemplate.from_template(reduce_template)
    reduce_chain=reduce_prompt |llm
    final_sum=reduce_chain.invoke({"code":code_snippet})    
    return final_sum.content
    
def close_repo(repo_link,repo_path=r"\tmp\clonedrepo"):
    delete_folder(repo_path)
    delete_docs_from_redis(repo_link)
    return 
     

if __name__=="__main__":
    print(code_snippet_summary(""" {
  "code": "s = 'malayalam'  # string\n\ni,j = 0, len(s) - 1  # two pointers\n\nis_palindrome = True  # assume palindrome\nwhile i < j:\n    if s[i] != s[j]:  # mismatch found\n        is_palindrome = False\n        break\n    i += 1\n    j -= 1\n\nif is_palindrome:\n    print(\"Yes\") \nelse:\n    print(\"No\")"
}
"""))