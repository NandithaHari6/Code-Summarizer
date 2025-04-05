import os
from controllers.entry import generate_summary, instantiate_llm
from langchain_core.prompts import PromptTemplate
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from evaluation.redis_cache import load_from_cache, store_to_cache
import os
import json
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from rouge import Rouge
github_link = [
"https://github.com/deepankarvarma/To-Do-List-Using-Python",

"https://github.com/MaxRohowsky/chrome-dinosaur",
"https://github.com/wasimtikki120/WeatherVista-Interactive-Weather-App",

"https://github.com/Rohit-Nandagawali/HTML-Chat-Application-using-java",

"https://github.com/bqubique/Text-Editor",
"https://github.com/Malavikkarajmohan/Movie-Ticket-Booking-System",
"https://github.com/rba1aji/Job-Portal-System"]

mydir = os.getcwd()  # Get the current directory 

llm=instantiate_llm()
extract_details_template = """You are a summary generation assisstent. Given the summary of a large project, extract Project overview, its main funcions and technology stack used in developing the project.The summary is {summary}  . No need of any other sentences in the response.Return the results in JSON format with the following keys only: Overview, Functional Overview, Technology Stack. 
- Exclude the diagrams, such as sequence diagrams, flowcharts from extractions
- Never add ```json on the beginning and do not add ``` at the end
    """
extract_prompt = PromptTemplate.from_template(extract_details_template)
extract_chain=extract_prompt|llm
def llm_evaluation(llm, ref, gen):
    evaluate_prompt_template="""Rate the reference summary {ref} and generated summary {gen} for quality on a scale of 0 to 5 , highest value indicating that they are very similar. Judge generated summary for how Accurately it summarize thes functionality of the project 
    -return just the rating
    -never add any text"""
    evaluate_prompt = PromptTemplate.from_template(evaluate_prompt_template)
    evaluate_chain=evaluate_prompt|llm
    res= evaluate_chain.invoke({"ref":ref,"gen":gen}).content
    # print(res)
    return res
def compute_rouge(ref_json, gen_json):
    fields = ["Overview", "Functional Overview", "Technology Stack"]
    rouge_eval=Rouge()
    scores = []
    
    for field in fields:
        ref_text = ref_json.get(field, "")
        gen_text = gen_json.get(field, "")
        
        if ref_text and gen_text:
            
            similarity = rouge_eval.get_scores(ref_text,gen_text)
            f1=similarity[0]["rouge-l"]
            scores.append(f1["f"])
        else:
            scores.append(0)
    # print(scores)
    return sum(scores) / len(scores) 
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
    # print(scores)
    return sum(scores) / len(scores)  # Average similarity score    
for i in range(len(github_link)):
    repo = github_link[i]
    cache_data = load_from_cache(repo)

    if cache_data:
        ref_summary = cache_data["ref_summary"]
        gen_summary = cache_data["gen_summary"]
        # print(f"Loaded cached summaries for {repo}")
    else:
        myfile = f"evaluation\\eval_files\\eval_files{i}.txt"
        file_path = os.path.join(mydir, myfile)

        with open(file_path, "r",encoding="utf8") as f:
            ref_summary = f.read()

        
        gen_summary = generate_summary(repo_link=repo, level="folder")
        

        store_to_cache(repo, ref_summary, gen_summary)
    llm_score=llm_evaluation(llm,ref_summary, gen_summary)
    ref_json = extract_chain.invoke({"summary": ref_summary}).content
    gen_json = extract_chain.invoke({"summary": gen_summary}).content
    # print(f"Github repo {repo}\n Generated summary : {gen_summary} \n Reference Summary {ref_summary}  Generated json:{gen_json} Reference json {ref_json}")
    score = compute_similarity(json.loads(ref_json), json.loads(gen_json))
    rouge_score=compute_rouge(json.loads(ref_json), json.loads(gen_json))
    print(f"Similarity Score for repo {repo}: Cosine similarity {score:.4f} \n Rouge score :{rouge_score} \n LLM score : {llm_score}")
    
 