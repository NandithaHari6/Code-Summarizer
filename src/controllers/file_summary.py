from controllers.gen_sum2 import instantiate_llm
from langchain_core.prompts import PromptTemplate
from controllers.splitters import split_document
def reduce_phase_file_sum_from_res(llm,res,file_path):
    j=0
    code_snippet_sum=[0]*len(res)
    
    for i in range(len(res)):
        curr_res=res[i].metadata
        
        if file_path == curr_res['source']:
            code_snippet_sum[j]=res[i].page_content
            
            j=j+1
    print("Summraries reduced are :", code_snippet_sum)
    reduce_template = """The following is set of summaries of small code snippets of the file , {file_path} that is a part of a big project .
    {docs}
    Take these and come up with a summmary of the functionality of the code in this file alone. Don't use more than 200 words.
    -Never use bullet points, bold lettetrs.
    -return as plain text.
    """
    file_path=file_path.replace("\\tmp\\clonedfile","")
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
    final_sum=file_path + "\n" + final_sum.content
    return final_sum        
def reduce_phase_file_sum(llm,code_snippet_doc,file_path):
    j=0
    
    code_snippet_sum=[]

    map_template = """
    {docs}
    Explain the code . 
    -Do not include meta data information and code snippet . 
    -Just the sentence explaination is enough"""
    map_prompt = PromptTemplate.from_template(map_template)
    map_chain = map_prompt |llm  
    i=0

    while i<(len(code_snippet_doc)):
        try:
            code_snippet_sum.append(map_chain.invoke(code_snippet_doc[i]).content)
           
            i+=1
        except Exception as e:
            print(e)
            if "413" in str(e): 
                doc=code_snippet_doc[i] # Check if error is 413 (Payload Too Large)
                print(f"Splitting document: {doc.metadata}")
                split_docs = split_document(doc)
                code_snippet_doc[i:i+1] = split_docs
            else:
                llm=instantiate_llm()
                map_chain = map_prompt |llm  
    print(len(code_snippet_doc))
    if len(code_snippet_sum)==1:
        return code_snippet_sum[0]
    reduce_template = """The following is set of summaries of small code snippets of the file , {file_path} that is a part of a big project. 
    {docs}
    Take these and come up with a summmary of the functionality of the code. Explain each function in detail.
    -Never use bullet points, bold lettetrs.
    -return as plain text.
    """
    reduce_prompt = PromptTemplate.from_template(reduce_template)
    reduce_chain=reduce_prompt |llm
    while True:
        try:
            
            final_sum=reduce_chain.invoke({"docs":code_snippet_sum,"file_path":file_path})
            break
        except Exception as e:
            print("Reduce file error", e)
            llm=instantiate_llm()
            reduce_chain=reduce_prompt |llm
    final_sum=file_path+ "\n"+final_sum.content
    return final_sum     