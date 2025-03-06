
from fastapi import  HTTPException
import requests

user_sessions={}

def save_user(access_token):
        # Get user data from GitHub API
    user_data_response = requests.get(
        "https://api.github.com/user",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    user_data = user_data_response.json()

    if "id" not in user_data:
        raise HTTPException(status_code=400, detail="Failed to fetch user data")

    github_id = str(user_data["id"])
    
    # Store session
    user_sessions[access_token] = github_id
    return github_id

def get_userid(access_token):
    if not access_token or access_token not in user_sessions:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    github_id = user_sessions[access_token]
    return github_id