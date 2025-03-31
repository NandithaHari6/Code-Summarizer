
from fastapi import  HTTPException, Depends
import requests
from fastapi.security import OAuth2PasswordBearer
user_sessions={}
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
def get_github_user(token: str = Depends(oauth2_scheme)):
    
    """Extracts and validates GitHub token using OAuth2PasswordBearer."""
    if  token  in user_sessions:
        return user_sessions[token] 
    else:
        github_id=save_user(token)
        if not github_id:
             raise HTTPException(status_code=400, detail="Invalid access token.")
        
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
def get_user_info(access_token: str = Depends(oauth2_scheme)):
    if not access_token:
        raise HTTPException(status_code=400, detail="No access token passed")

    user_data_response = requests.get(
        "https://api.github.com/user",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    user_data = user_data_response.json()
    if not user_data:
        raise HTTPException(status_code=400, detail="Failed to fetch user data")
    return {"name":user_data["name"],"username": user_data["login"],"no_of_repos":user_data["public_repos"],"url":user_data["html_url"], "followers":user_data["followers"],"following":user_data["following"] }
def logout_user(access_token: str = Depends(oauth2_scheme)):
    if access_token not in user_sessions or not access_token:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    del user_sessions[access_token]  # Remove token from session
    return {"message": "Logged out successfully"}