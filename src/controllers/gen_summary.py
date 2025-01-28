from git import Repo
from langchain_community.document_loaders.generic import GenericLoader
from langchain_community.document_loaders.parsers import LanguageParser
from langchain_text_splitters import Language
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
import shutil
load_dotenv()
import os
def generate_summary(repo_link: str, level: str) -> str:
    print(level)
    
    repo_path ="/tmp/clonedfile"
    
    # repo = Repo.clone_from(repo_link, to_path=repo_path)
    loader = GenericLoader.from_filesystem(
        repo_path ,
        glob="**/*",
        suffixes=[".py", ".js"],
        
        
        parser=LanguageParser(),
    )
    documents = loader.load()
    print("Len of documents")
    print(len(documents))

    res=[0]*len(documents)
    llm=ChatGroq(temperature=0,
                groq_api_key=os.getenv("groq_api_key"),
                model_name="llama-3.3-70b-versatile")

    # Map
    map_template = """You are a senior software engineer working on this project, with experience of handling various code bases, in different programming languages. Explain the functionality of the code to a junior software developer, who recently joined your team and is viewing this code base for the first time 
    {docs}
    Explain in just 2 to 3 sentences,just the thing in the code alone. Do not add your own logic  .Do not include meta data information and code snippet . Just the sentence explaination is enough"""
    map_prompt = PromptTemplate.from_template(map_template)
    map_chain = map_prompt |llm
    i=0
    for i in range(0,len(documents)):
    #    print(map_chain.invoke({"docs":documents[i]}).content)
        print(documents[i].metadata)
        res[i]=map_chain.invoke({"docs":documents[i]}).content
    # Reduce
    reduce_template = """The following is set of summaries of small code snippets of that are part of a single project
    {docs}
    Take these and distill it into a final, consolidated summary of the main themes. 
    """
    reduce_prompt = PromptTemplate.from_template(reduce_template)
    reduce_chain=reduce_prompt |llm
    final_sum=reduce_chain.invoke({"docs":res})
   
    print(final_sum.content)

    
    try:
        if os.path.exists(repo_path):
            print(f"Directory exists: {repo_path}. Deleting...")
            shutil.rmtree(repo_path)
            print(f"Deleted {repo_path}")
        else:
            print(f"Directory does not exist: {repo_path}")
    except OSError as e:
    # If it fails, inform the user.
        print("Error: %s - %s." % (e.filename, e.strerror))
    return final_sum.content



if __name__=="__main__":
    generate_summary("https://github.com/NandithaHari6/dbms-project","folder")
    
    