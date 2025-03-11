import os
from controllers.gen_sum2 import generate_summary, instantiate_llm
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
from nltk.translate.bleu_score import sentence_bleu
from rouge_score import rouge_scorer as Rouge
from bert_score import score as bert_score
from nltk.translate.meteor_score import meteor_score
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
def compute_cosine_similarity(ref_text, gen_text):
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([ref_text, gen_text])
    return cosine_similarity(tfidf_matrix[0], tfidf_matrix[1])[0][0]

def compute_bleu_score(ref_text, gen_text):
    return sentence_bleu([ref_text.split()], gen_text.split())

def compute_rouge_score(ref_text, gen_text):
    rouge = Rouge()
    return rouge.get_scores(gen_text, ref_text)[0]['rouge-l']['f']

def compute_bert_score(ref_text, gen_text):
    P, R, F1 = bert_score([gen_text], [ref_text], lang="en")
    return F1.mean().item()

def compute_meteor_score(ref_text, gen_text):
    return meteor_score([ref_text.split()], gen_text.split())

def compute_similarity(ref_json, gen_json):
    fields = ["Overview", "Functional Overview", "Technology Stack"]
    scores = {"Cosine": [], "BLEU": [], "ROUGE": [], "BERT": [], "METEOR": []}
    
    for field in fields:
        ref_text = ref_json.get(field, "")
        gen_text = gen_json.get(field, "")
        
        if ref_text and gen_text:
            scores["Cosine"].append(compute_cosine_similarity(ref_text, gen_text))
            scores["BLEU"].append(compute_bleu_score(ref_text, gen_text))
            scores["ROUGE"].append(compute_rouge_score(ref_text, gen_text))
            scores["BERT"].append(compute_bert_score(ref_text, gen_text))
            scores["METEOR"].append(compute_meteor_score(ref_text, gen_text))
        else:
            for key in scores:
                scores[key].append(0)
    
    avg_scores = {key: sum(values) / len(values) for key, values in scores.items()}
    return avg_scores

for i, repo in enumerate(github_link):
    cache_data = load_from_cache(repo)
    
    if cache_data:
        ref_summary = cache_data["ref_summary"]
        gen_summary = cache_data["gen_summary"]
        print(f"Loaded cached summaries for {repo}")
    else:
        myfile = f"evaluation/eval_files/eval_files{i}.txt"
        file_path = os.path.join(mydir, myfile)

        with open(file_path, "r") as f:
            ref_summary = f.read()
        
        gen_summary = generate_summary(repo_link=repo, level="folder")
        store_to_cache(repo, ref_summary, gen_summary)
    
    ref_json = extract_chain.invoke({"summary": ref_summary})
    gen_json = extract_chain.invoke({"summary": gen_summary})
    print(f"Github repo {repo}\nGenerated summary: {gen_summary}\nReference Summary: {ref_summary}\nGenerated JSON: {gen_json}\nReference JSON: {ref_json}")
    
    similarity_scores = compute_similarity(json.loads(ref_json.content), json.loads(gen_json.content))
    
    print(f"Similarity Scores for repo {repo}:")
    print(f"  Cosine Similarity: {similarity_scores['Cosine']:.4f}")
    print(f"  BLEU Score: {similarity_scores['BLEU']:.4f}")
    print(f"  ROUGE Score: {similarity_scores['ROUGE']:.4f}")
    print(f"  BERT Score: {similarity_scores['BERT']:.4f}")
    print(f"  METEOR Score: {similarity_scores['METEOR']:.4f}")



# def compute_similarity(ref_json, gen_json):
#     fields = ["Overview", "Functional Overview", "Technology Stack"]
#     vectorizer = TfidfVectorizer()
#     scores = []
    
#     for field in fields:
#         ref_text = ref_json.get(field, "")
#         gen_text = gen_json.get(field, "")
        
#         if ref_text and gen_text:
#             tfidf_matrix = vectorizer.fit_transform([ref_text, gen_text])
#             similarity = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1])[0][0]
#             scores.append(similarity)
#         else:
#             scores.append(0)
#     print(scores)
#     return sum(scores) / len(scores)  # Average similarity score    
# for i in range(len(github_link)):
#     repo = github_link[i]
#     cache_data = load_from_cache(repo)

#     if cache_data:
#         ref_summary = cache_data["ref_summary"]
#         gen_summary = cache_data["gen_summary"]
#         print(f"Loaded cached summaries for {repo}")
#     else:
#         myfile = f"evaluation/eval_files/eval_files{i}.txt"
#         file_path = os.path.join(mydir, myfile)

#         with open(file_path, "r") as f:
#             ref_summary = f.read()

        
#         generated_summary = generate_summary(repo_link=repo, level="folder")
        

#         store_to_cache(repo, ref_summary, gen_summary)

#     ref_json = extract_chain.invoke({"summary": ref_summary})
#     gen_json = extract_chain.invoke({"summary": generated_summary})
#     print(f"Github repo {repo}\n Generated summary : {gen_summary} \n Reference Summary {ref_summary}  Generated json:{gen_json} Reference json {ref_json}")
#     score = compute_similarity(json.loads(ref_json.content), json.loads(gen_json.content))
#     print(f"Similarity Score for repo {repo}: {score:.4f}")
