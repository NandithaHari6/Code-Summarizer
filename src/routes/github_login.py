from fastapi import  HTTPException, Request, APIRouter
from fastapi.responses import RedirectResponse
import requests
import os
from dotenv import load_dotenv

load_dotenv()



GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
REDIRECT_URI = "http://localhost:8000/github-login"

# Store active sessions (Temporary)
user_sessions = {}  # {token: github_id}
git_router = APIRouter()
@git_router.get("/github/login")
def github_login():
    """Redirect user to GitHub for authentication."""
    github_auth_url = f"https://github.com/login/oauth/authorize?client_id={GITHUB_CLIENT_ID}&redirect_uri={REDIRECT_URI}"
    return RedirectResponse(url=github_auth_url)

@git_router.get("/github-login")
def github_callback(code: str):
    """GitHub OAuth callback to exchange code for an access token."""
    token_url = "https://github.com/login/oauth/access_token"
    headers = {"Accept": "application/json"}
    payload = {
        "client_id": GITHUB_CLIENT_ID,
        "client_secret": GITHUB_CLIENT_SECRET,
        "code": code,
        "redirect_uri": REDIRECT_URI
    }
    
    response = requests.post(token_url, headers=headers, data=payload)
    token_data = response.json()
    
    if "access_token" not in token_data:
        raise HTTPException(status_code=400, detail="Failed to get access token")

    access_token = token_data["access_token"]

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
    FRONTEND_URL="http://localhost:5173/"
    return RedirectResponse(url=f"{FRONTEND_URL}?access_token={access_token}")

@git_router.get("/protected-route")
def protected_route(request: Request):
    """Example of a protected route"""
    token = request.headers.get("Authorization")
    
    if not token or token not in user_sessions:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    github_id = user_sessions[token]
    return {"message": "You have access!", "github_id": github_id}
