from git import Repo
import stat
from langchain_community.document_loaders.generic import GenericLoader
from langchain_community.document_loaders.parsers import LanguageParser
from langchain_text_splitters import Language
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
from controllers.redis_cache import save_docs_to_redis, load_docs_from_redis, delete_docs_from_redis
import shutil
load_dotenv()
import os

def load_docs(repo_link:str,repo_path:str):    
    repo = Repo.clone_from(repo_link, to_path=repo_path)
    loader = GenericLoader.from_filesystem(
        repo_path ,

        glob="**/*",
        suffixes=[".py",".js"],
        # exclude=["**/non-utf8-encoding.py"],
        parser=LanguageParser(),
    )
    documents = loader.load()
    return documents
def instantiate_llm(llm_name:str):
    if llm_name =="Chatgroq":
        llm=ChatGroq(temperature=0,
                    groq_api_key=os.getenv("groq_api_key"),
                    model_name="llama-3.3-70b-versatile")
    return llm
def map_phase(llm,documents):
    map_template = """You are a senior software engineer working on this project, with experience of handling various code bases, in different programming languages. Explain the functionality of the code to a junior software developer, who recently joined your team and is viewing this code base for the first time 
    {docs}
    Explain in just 2 to 3 sentences,just the thing in the code alone. Do not add your own logic  .Do not include meta data information and code snippet . Just the sentence explaination is enough"""
    map_prompt = PromptTemplate.from_template(map_template)
    map_chain = map_prompt |llm
    i=0
    res=[0]*len(documents)
    for i in range(0,len(documents)):
    #    print(map_chain.invoke({"docs":documents[i]}).content)
        print(documents[i].metadata)
        res[i]=map_chain.invoke({"docs":documents[i]}).content
        # print(res[i])
    return res
    # Reduce
def reduce_phase_folder_sum(llm,res):
    reduce_template = """The following is set of summaries of small code snippets of that are part of a single project
    {docs}
    Take these and distill it into a final, consolidated summary of the main themes. 
    """
    reduce_prompt = PromptTemplate.from_template(reduce_template)
    reduce_chain=reduce_prompt |llm
    final_sum=reduce_chain.invoke({"docs":res})
   
    return final_sum
# def reduce_phase_file_sum(llm,documents,file_path):
#     j=0
#     code_snippet_doc=[0]
#     code_snippet_sum=[0]
#     for i in range(len(documents)):
#             if file_path == documents[i].metadata['source']:
#                 code_snippet_doc[j]=documents[i]
#                 j=j+1 
#     map_template = """You are a senior software engineer working on this project, with experience of handling various code bases, in different programming languages. Explain the functionality of the code to a junior software developer, who recently joined your team and is viewing this code base for the first time 
#     {docs}
#     Explain in just 2 to 3 sentences,just the thing in the code alone. Do not add your own logic  .Do not include meta data information and code snippet . Just the sentence explaination is enough"""
#     map_prompt = PromptTemplate.from_template(map_template)
#     map_chain = map_prompt |llm   
#     for i in range(len(code_snippet_doc)):
#          code_snippet_sum[i]=map_chain.invoke(code_snippet_doc[i])
#     reduce_template = """The following is set of summaries of small code snippets of the file , {file_path} that is a part of a big project .
#     {docs}
#     Take thses and come up with a summmary of the functionality of the code in this file alone. Explain each function in detail. Don't use more than 200 words.
#     """
#     reduce_prompt = PromptTemplate.from_template(reduce_template)
#     reduce_chain=reduce_prompt |llm
#     final_sum=reduce_chain.invoke({"docs":code_snippet_sum,"file_path":file_path})
   
#     return final_sum        
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
    reduce_prompt = PromptTemplate.from_template(reduce_template)
    reduce_chain=reduce_prompt |llm
    final_sum=reduce_chain.invoke({"docs":code_snippet_sum,"file_path":file_path})
   
    return final_sum        
def get_repo_directory_structure(repo_path):
    """Returns the directory structure of the cloned repository."""
    repo_structure = {}
    for root, dirs, files in os.walk(repo_path):
        relative_path = os.path.relpath(root, repo_path)
        repo_structure[relative_path] = {
            "folders": dirs,
            "files": files
        }
    return repo_structure    


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
def generate_summary(repo_link: str,level,file_path=None) -> str:
    #Load documents
    repo_path = "/tmp/clonedfile"
    cached_docs = load_docs_from_redis(repo_link)
    documents={}
    llm=instantiate_llm("Chatgroq")
    if cached_docs:
        print("Loading data from Redis cache...")
        documents = cached_docs["documents"]
        res = cached_docs["res"]
    else: 
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
        final_sum=reduce_phase_file_sum_from_res(llm,res,documents,file_path)
        print(final_sum.content) 
    delete_folder(repo_path)
    return final_sum.content

def close_repo(repo_link,repo_path=r"\tmp\clonedrepo"):
    delete_folder(repo_path)
    delete_docs_from_redis(repo_link)
    return 
     

if __name__=="__main__":
    # generate_summary("https://github.com/NandithaHari6/dbms-project-backend","file","\\tmp\\clonedfile\\controller\\customerController.js")
    print(get_repo_directory_structure("/tmp/clonedfile"))
    # delete_folder("/tmp/clonedfile")
    # delete_docs_from_redis("https://github.com/NandithaHari6/dbms-project-backend")