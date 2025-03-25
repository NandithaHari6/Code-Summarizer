from controllers.gen_sum2 import instantiate_llm
from langchain_core.prompts import PromptTemplate
from controllers.redis_cache import save_docs_to_redis, load_docs_from_redis
from controllers.splitters import split_document,count_token_as_len
def map_phase(llm, documents, repo_link):
    """Processes documents, stores summaries in Redis, and resumes if interrupted."""
    map_template = """You are a senior software engineer working on this project, with experience handling various code bases in different programming languages. Explain the functionality of the code to a junior developer viewing this code base for the first time.
    {docs}. This code snippet is a part of a large project.
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
 
    print("Reduce large folder exec")
  
    # new_res=[]
    # i=0
    # print("Type of res in large", type(res))
    # print("Type of res in large", type(res[0]))

    # documents=split_document(res[0])
    # print("Type of res in large", type(res[0]))
    # print("Type of res in large", type(res[0]))
    # print(documents[0])
    # llm=instantiate_llm()
    # map_reduce_prompt = PromptTemplate.from_template(map_reduce_template)
    # map_reduce_chain=map_reduce_prompt |llm
    # while i<len(documents):
    #     doc=documents[i]
    #     print(doc)
    #     try:
    #         new_res[i]=map_reduce_chain.invoke({"res":doc.page_content}).content
    #         i+=1
    #     except Exception as e:
    #         if "413" in str(e):
    #             print(f"Splitting document: {doc.metadata}")
    #             split_docs = split_document(doc)
    #             documents[i:i+1] = split_docs
    #         else:
                
    #             llm = instantiate_llm()
    #             map_reduce_chain = map_reduce_prompt | llm
        

    new_res=[doc.page_content for doc in res]

    reduce_template=''' The following is a collection of summaries from various small code snippets that together form a single project:  
{docs}  .

Analyze these snippets, extract the core themes, and distill them into a final summary within strictly 100 words'''
    print(new_res[0])
    prev=0
    token=0
    i=0
    llm=instantiate_llm()
    reduce_prompt = PromptTemplate.from_template(reduce_template)
    reduce_chain=reduce_prompt |llm
    while len(new_res)>1:
        prev=0
        token=0
        i=0
        print("Len of array",len(new_res))
        while i<len(new_res):
            
            if len(new_res)==1:
                return new_res[0]
            token_count=count_token_as_len(new_res[i])
            print(token_count)


            if((token_count+token >4000) or i==(len(new_res)-1)):
                

                while True:
                    try:
                        if i==(len(new_res)-1):
                            text = " ".join(new_res[prev:])  
                        else:
                            text = " ".join(new_res[prev:i])  
                        
                        sum=reduce_chain.invoke({"docs":text}).content
                        print("Summary is ",sum)
                        if i==(len(new_res)-1):
                            new_res[prev:]=[sum]
                        else:
                            new_res[prev:i]=[sum]
                        break
                    except Exception as e:
                        print(" Reduce prompt",e)
                        llm = instantiate_llm()
                        reduce_chain = reduce_prompt | llm
                print("Updating")
                token=token_count
                i=prev+2
                prev=prev+1
            else:
                token+=token_count
                i+=1
                



    return new_res[0]  
# def reduce_helper(new_res):
#     reduce_template=''' The following is a collection of summaries from various small code snippets that together form a single project:  
# {docs}  .

# Analyze these snippets, extract the core themes, and distill them into a final summary within strictly 100 words'''
#     llm=instantiate_llm()
#     reduce_prompt = PromptTemplate.from_template(reduce_template)
#     reduce_chain=reduce_prompt |llm
#     prev=0
#     token=0
#     i=0
#     while i<len(new_res):
#             if
#             token_count=count_token_as_len(new_res[i])
#             print(token_count)
#             if token_count+token <4000:
#                 token+=token_count
#                 i+=1
#             else:
                

#                 while True:
#                     try:
                      

#                         sum=reduce_chain.invoke({"docs":new_res[prev:i]}).content

#                         print(sum)
#                         new_res[prev:i]=[sum]
#                         break
#                     except Exception as e:
#                         print(" Reduce prompt",e)
#                         llm = instantiate_llm()
#                         reduce_chain = reduce_prompt | llm
#                 print("Updating")
#                 token=token_count
#                 i=prev+1
#                 prev=prev+1
#     return new_res
def reduce_phase_folder_sum(llm,res):
    print(res[0])
    reduce_template  = """The following is a collection of summaries from various small code snippets that together form a single project:  
{docs}  .

Analyze these snippets, extract the core themes, and distill them into a final, well-structured summary.  
The final summary should follow this format:  
- Project Title: A concise and descriptive title reflecting the project's purpose.  
- Tech Stack Used: List the programming languages, frameworks, libraries, and tools utilized.  
- Project Overview: A brief explanation of the project's goal, functionality, and intended audience.  
- File & Folder Breakdown: A structured summary of the project's key directories and files, along with their roles.
Ensure readability with proper indentation and bullet points.
 """
    llm=instantiate_llm()
    reduce_prompt = PromptTemplate.from_template(reduce_template)
    reduce_chain=reduce_prompt |llm
    while True:
        try:
            doc_texts = [doc.page_content for doc in res]  # Fix indexing issue
            final_sum = reduce_chain.invoke({"docs": doc_texts})
        
          
            break
        except Exception as e:
            print(e)
            if "413" in str(e):
                final_res=reduce_large_folder(res)
                return final_res
                
            else:
                llm=instantiate_llm()
                reduce_chain=reduce_prompt |llm
            

    return final_sum.content