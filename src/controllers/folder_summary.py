from controllers.gen_sum2 import instantiate_llm
from langchain_core.prompts import PromptTemplate
from controllers.redis_cache import save_docs_to_redis, load_docs_from_redis
from controllers.splitters import split_document,count_tokens
import json
def map_phase(llm, documents, repo_link):
    """Processes documents, stores summaries in Redis, and resumes if interrupted."""
    map_template = """You are a senior software engineer working on this project, with experience handling various code bases in different programming languages. Explain the functionality of the code to a junior developer viewing this code base for the first time.
    {docs}. This code snippet is a part of a large project.
    Explain in just 2 to 3 sentences,not exceeding 150 words, only describing the code functionality,any important tech stacks, tools or frameworks used.
     -Do not add your own logic, metadata, or code snippets."""
    
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
            doc.__class__(page_content=response, metadata=doc.metadata)
            # Store only metadata and summary
            cached_res.append(doc)

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
def reduce_large_folder(res):
    map_reduce_template=''' Fit in this summary generated into consice , accurate paragraph or sentence withiin 100 words, strictly.{res} '''
 
   
    new_res=[doc.page_content for doc in res]

    reduce_template=''' The following is a collection of summaries from various small code snippets that together form a single project:  
{docs}  .

Analyze these snippets, extract the core themes, and distill them into a final summary within strictly 100 words'''
    reduce_template_last_doc="""The following is a collection of summaries from various small code snippets that together form a single project:  
{docs}  .

Analyze these snippets, extract the core themes, and distill them into a final, well-structured summary.  
The final summary should follow this format:  
- Project Title: A concise and descriptive title reflecting the project's purpose.  
- Tech Stack Used: List the programming languages, frameworks, libraries, and tools utilized.  
- Project Overview: An explanation of the project's goal, functionality, and intended audience.Overview Should contain upto 300 words.  
- File & Folder Breakdown: A structured summary of the project's key directories and files, along with their roles.

No need of any other sentences in the response.Return the results in JSON format with the following keys only: projectTitle, techStack, projectOverview, fileOverview.
The values of each field must be strictly strings and not list or dictionary.fileOverview must contain filename-description format. 
- Never add ```json on the beginning and do not add ``` at the end

 """
    prev=0
    token=0
    i=0
    llm=instantiate_llm()
    reduce_prompt = PromptTemplate.from_template(reduce_template)
    last_reduce_prompt=PromptTemplate.from_template(reduce_template_last_doc)
    reduce_chain=reduce_prompt |llm
    
    while len(new_res)>1:
        prev=0
        token=0
        i=0
   
        while i<len(new_res):
            
            if len(new_res)==1:
                return new_res[0]
            token_count=count_tokens(new_res[i])
            print(token_count)


            if((token_count+token >4000) or i==(len(new_res)-1)):
                

                while True:
                    try:
                        if i==(len(new_res)-1):
                            text = " ".join(new_res[prev:])  
                            last_reduce_chain=last_reduce_prompt |llm
                            sum=last_reduce_chain.invoke({"docs":text}).content
                            new_res[prev:]=[sum]
                        else:
                            text = " ".join(new_res[prev:i])  
                            sum=reduce_chain.invoke({"docs":text}).content
                            new_res[prev:i]=[sum]
                        print("Summary is ",sum)
                        
                            
                        break
                    except Exception as e:
                        print(" Reduce prompt",e)
                        llm = instantiate_llm()
                        reduce_chain = reduce_prompt | llm
                
                token=token_count
                i=prev+2
                prev=prev+1
            else:
                token+=token_count
                i+=1
    return new_res[0]  

def reduce_phase_folder_sum(llm,res):
    print(res[0])
    reduce_template  = """The following is a collection of summaries from various small code snippets that together form a single project:  
{docs}  .

Analyze these snippets, extract the core themes, and distill them into a final, well-structured summary.  
The final summary should follow this format:  
- Project Title: A concise and descriptive title reflecting the project's purpose.  
- Tech Stack Used: List the programming languages, frameworks, libraries, and tools utilized.  
- Project Overview: An explanation of the project's goal, functionality, and intended audience. Overview Should contain upto 300 words. 
- File & Folder Breakdown: A structured summary of the project's key directories and files, along with their roles.

No need of any other sentences in the response.Return the results in JSON format with the following keys only: projectTitle, techStack, projectOverview, fileOverview.
The values of each field must be strictly strings and not list or dictionary.fileOverview must contain filename-description format. 
- Never add ```json on the beginning and do not add ``` at the end

 """
   
    llm=instantiate_llm()
    reduce_prompt = PromptTemplate.from_template(reduce_template)
    reduce_chain=reduce_prompt |llm
    while True:
        try:
            
            doc_texts = [doc.page_content for doc in res]  # Fix indexing issue
            final_sum = reduce_chain.invoke({"docs": doc_texts})
            
            final_sum=json.loads(final_sum.content)
          
            break
        except Exception as e:
            print(e)
            if "413" in str(e):
                final_res=reduce_large_folder(res)
                return final_res   
            else:
                llm=instantiate_llm()
                reduce_chain=reduce_prompt |llm
            

    return final_sum