import os
from controllers.gen_sum2 import generate_summary, instantiate_llm
from langchain_core.prompts import PromptTemplate
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
github_link = [
    "https://github.com/adityasurya4103/Clinic-Hospital-Management-System-",
"https://github.com/Viveckh/Veniqa",
"https://github.com/Tanq16/ExpenseOwl",
"https://github.com/AR10X/data-analysis",
"https://github.com/PATMESH/Learning-Management-System",
"https://github.com/deepankarvarma/To-Do-List-Using-Python",
"https://github.com/otahina/PowerPoint-Generator-Python-Project",
"https://github.com/MaxRohowsky/chrome-dinosaur",
"https://github.com/wasimtikki120/WeatherVista-Interactive-Weather-App",

"https://github.com/Rohit-Nandagawali/HTML-Chat-Application-using-java",
]

mydir = os.getcwd()  # Get the current directory 


llm=instantiate_llm()
extract_details_template = """You are a summary generation assisstent. Given the summary of a large project, extract Project overview, its main funcions and technology stack used in developing the project.The summary is {summary}  . No need of any other sentences in the response.Return the results in JSON format with the following keys only: Overview, Functional Overview, Technology Stack. 
- Exclude the Mermaid diagrams, such as sequence diagrams, flowcharts from extractions
- Never add ```json on the beginning and do not add ``` at the end
    """
extract_prompt = PromptTemplate.from_template(extract_details_template)
extract_chain=extract_prompt|llm
def compute_similarity(ref_json, gen_json):
    fields = ["Overview", "Functional Overview", "Technology Stack"]
    vectorizer = TfidfVectorizer()
    scores = []
    
    for field in fields:
        ref_text = ref_json.get(field, "")
        gen_text = gen_json.get(field, "")
        
        if ref_text and gen_text:
            tfidf_matrix = vectorizer.fit_transform([ref_text, gen_text])
            similarity = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1])[0][0]
            scores.append(similarity)
        else:
            scores.append(0)
    print(scores)
    return sum(scores) / len(scores)  # Average similarity score    
for i in range(len(github_link)):
    myfile = f"evaluation/eval_files/eval_files{i}.txt"
    file_path = os.path.join(mydir, myfile)
    with open(file_path, "r") as f:
        ref_summary = f.read()  # Read file content
    
    ref_json=extract_chain.invoke({"summary":ref_summary})
    
    generated_summary=generate_summary(repo_link=github_link[i], level="folder")
    gen_json=extract_chain.invoke({"summary":generated_summary})
    # print(f"Ref summary :{ref_json.content}")
    # print(f"Generated Summary:{gen_json.content}")
    # print(json.loads(ref_json.content))
    score = compute_similarity(json.loads(ref_json.content), json.loads(gen_json.content))
    print(f"Similarity Score for repo {github_link[i]}: {score:.4f}")
    

