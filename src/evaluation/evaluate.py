import os
from controllers.gen_summary import generate_summary, instantiate_llm, close_repo
from langchain_core.prompts import PromptTemplate
github_link=["https://github.com/adityasurya4103/Clinic-Hospital-Management-System-"]

mydir = os.getcwd()  # Get the current directory 


llm=instantiate_llm("Chatgroq")
extract_details_template = """You are a summary generation assisstent. Given the summary of a large project, extract Project overview, its main funcions and technology stack used in developing the project.The summary is {summary}  . No need of any other sentences in the response.Return the results in JSON format with the following keys only: Overview, Functional Overview, Technology Stack. 
- Exclude the Mermaid diagrams, such as sequence diagrams, flowcharts from extractions
- Never add ```json on the beginning and do not add ``` at the end
    """
extract_prompt = PromptTemplate.from_template(extract_details_template)
extract_chain=extract_prompt |llm
    
for i in range(len(github_link)):
    myfile = f"evaluation/eval_files/eval_file{i}.txt"
    file_path = os.path.join(mydir, myfile)
    with open(file_path, "r") as f:
        ref_summary = f.read()  # Read file content
    print(ref_summary)
    ref_json=extract_chain.invoke({"summary":ref_summary})
    print(ref_json)
    generated_summary=generate_summary(repo_link=github_link[0], level="folder")
    gen_json=extract_chain.invoke({"summary":generated_summary})
    print(gen_json)

    close_repo(repo_link=github_link[i])

