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
    repo = Repo.clone_from(repo_link, to_path=repo_path)
    loader = GenericLoader.from_filesystem(
        repo_path ,
        glob="**/*",
        suffixes=[".py"],
        exclude=["**/non-utf8-encoding.py"],
        parser=LanguageParser(language=Language.PYTHON),
    )
    documents = loader.load()
    print("Len of documents")
    print(len(documents))

    res=[0]*len(documents)
    llm=ChatGroq(temperature=0,
                groq_api_key=os.getenv("groq_api_key"),
                model_name="llama-3.1-70b-versatile")

    # Map
    map_template = """The following is the code that is a part of a price comparison website.
    {docs}
    The docs contain python code for building a proce comparison website. Please summarize each doc in 2 to 3 lines, include all necessary and important information.Do not include meta data information and code snippet . Just the sentence explaination is enough"""
    map_prompt = PromptTemplate.from_template(map_template)
    map_chain = map_prompt |llm
    i=0
    for i in range(0,len(documents)):
    #    print(map_chain.invoke({"docs":documents[i]}).content)
        res[i]=map_chain.invoke({"docs":documents[i]}).content
    # Reduce
    reduce_template = """The following is set of summaries of small code snippets of a price comparison website code
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
    generate_summary("https://github.com/NandithaHari6/portfolio","folder")
    
    