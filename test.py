import requests

# The API endpoint
# url = "https://code-summarizer.onrender.com/generate_folder_summary"
# url="http://127.0.0.1:8000/generate_folder_summary"
# # Data to be sent
# data = {
#     "repo_link":"https://github.com/NandithaHari6/dbms-project-backend",
#     "level":"folder"
# }
url="http://127.0.0.1:8000/generate_code_summary"
# Data to be sent
code="""s = "malayalam"  # string

i,j = 0, len(s) - 1  # two pointers

is_palindrome = True  # assume palindrome
while i < j:
    if s[i] != s[j]:  # mismatch found
        is_palindrome = False
        break
    i += 1
    j -= 1

if is_palindrome:
    print("Yes") 
else:
    print("No")   
"""
data = {
    "code":code
    
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