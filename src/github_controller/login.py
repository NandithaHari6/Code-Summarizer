
from fastapi import  HTTPException, Depends
import requests
from fastapi.security import OAuth2PasswordBearer
user_sessions={}
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
def get_github_user(token: str = Depends(oauth2_scheme)):
    """Extracts and validates GitHub token using OAuth2PasswordBearer."""
    if not token or token not in user_sessions:
        raise HTTPException(status_code=403, detail="Unauthorized")
    return user_sessions[token]  
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
