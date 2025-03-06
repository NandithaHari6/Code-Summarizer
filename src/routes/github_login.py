from fastapi import  HTTPException, Request, APIRouter
from fastapi.responses import RedirectResponse
import requests
import os
from dotenv import load_dotenv
from github_controller.login import save_user,get_user
load_dotenv()



GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
REDIRECT_URI = "https://code-summarizer.onrender.com/github-login"

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

    github_id=save_user(access_token)
    FRONTEND_URL="http://localhost:3000/"
    return RedirectResponse(url=f"{FRONTEND_URL}?access_token={access_token}")

@git_router.get("/protected-route")
def protected_route(request: Request):
    """Example of a protected route"""
    access_token = request.headers.get("Authorization")
    
    github_id=get_user(access_token)
    return {"message": "You have access!", "github_id": github_id}
