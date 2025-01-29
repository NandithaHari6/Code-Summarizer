import requests

# The API endpoint
# url = "https://code-summarizer.onrender.com/generate_summary"
url="http://127.0.0.1:8000/generate_summary"
# Data to be sent
data = {
    "repo_link":"https://github.com/NandithaHari6/dbms-project-backend",
    "level":"file",
    "file_path":"\\tmp\\clonedfile\\cibil.js"
}

# A POST request to the API
response = requests.post(url, json=data)
# print(response.json())
# data2={
#     "username":"Nanditha",
#     "email":"nanditha@gmail.com",
#     "summary":response.summary
# }
# save_url="http://127.0.0.1:8000/save_summary"
# res=requests.post(save_url, json=data2)
# # Print the response
print(response.json())