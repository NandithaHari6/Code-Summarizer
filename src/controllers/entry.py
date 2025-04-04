from controllers.redis_cache import  load_docs_from_redis
import os
from controllers.folder_summary import map_phase, reduce_phase_folder_sum
from controllers.file_summary import reduce_phase_file_sum, reduce_phase_file_sum_from_res
from controllers.gen_sum2 import instantiate_llm, load_single_file, load_docs,delete_folder, get_directory_structure
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
    


    #Map reduce
    if level=="folder":
        # file_structure=get_directory_structure(repo_link)

        folder_structure=get_directory_structure(repo_link)
        final_sum=reduce_phase_folder_sum(llm,res,folder_structure)
        print(final_sum)
    elif level=="file":
        if cached_docs and cached_docs["completed"]:
            final_sum=reduce_phase_file_sum_from_res(llm,res,file_path)
            print(final_sum)
            
        else:             
            extracted_path = file_path.replace("\\tmp\\clonedfile\\", "" , 1)
            print("Extracted path",extracted_path)
            documents=load_single_file(repo_link,extracted_path)

            
            final_sum=reduce_phase_file_sum(llm,documents,file_path)
            print(final_sum)
    if os.path.exists(repo_path):
        delete_folder(repo_path)
    return final_sum
if __name__=="__main__":
    generate_summary("https://github.com/wasimtikki120/WeatherVista-Interactive-Weather-App","file","\\tmp\\clonedfile\\script.js")
    