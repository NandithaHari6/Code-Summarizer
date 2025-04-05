
from fastapi.responses import RedirectResponse
import requests
import os
from database.model import Summary
from dotenv import load_dotenv
from github_controller.login import save_user
from reqmodel.model import AddSummary
from database.connection import get_db
from fastapi import APIRouter, HTTPException, Depends, Request,Query
from sqlalchemy.orm import Session
from utils.save_sum import add_summary,delete_summary
from github_controller.login import get_github_user, get_user_info,logout_user
import httpx
import uuid

load_dotenv()



GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
REDIRECT_URI = "http://127.0.0.1:8000/github-code"

git_router = APIRouter()
@git_router.get("/github-login")
def github_login_endpoint():
    """Redirect user to GitHub for authentication."""
  
    github_auth_url =f"https://github.com/login/oauth/authorize?client_id={GITHUB_CLIENT_ID}&redirect_uri={REDIRECT_URI}"
    headers = {'Content': 'application/json'}
    return RedirectResponse(url=github_auth_url,headers=headers)

@git_router.get("/github-code")
async def github_callback(code: str):
    params ={
        'client_id': GITHUB_CLIENT_ID,
        'client_secret': GITHUB_CLIENT_SECRET,
        'code': code
    }
    headers = {'Accept': 'application/json'}
    async with httpx.AsyncClient() as client:
        response = await client.post(url='https://github.com/login/oauth/access_token', params=params, headers=headers)
    if response.status_code==200:
        response_json = response.json()

        access_token = response_json['access_token']
        if  not access_token:
            raise HTTPException(status_code=400, detail="Failed to get access token")
        github_id=save_user(access_token)
    FRONTEND_URL="http://localhost:3000/login"
    return RedirectResponse(url=f"{FRONTEND_URL}?access_token={access_token}")


@git_router.post("/save_summary")
async def save_summary(
    summary: AddSummary, 
    githubid: int = Depends(get_github_user),  # Now uses OAuth2 Bearer Token
    db: Session = Depends(get_db)
):
    """Protected route that stores a summary in the database."""
    new_summary = add_summary(db, summary, githubid)
    return {
        "message": "Summary added successfully",
        "githubid": new_summary.githubid,
        "repo_link": new_summary.repo_link,
        "summary": new_summary.summary,
        "level": new_summary.level,
    }
@git_router.get("/view_saved_sum")
def display_summary(githubid: int = Depends(get_github_user),  # Now uses OAuth2 Bearer Token
    db: Session = Depends(get_db)):
   
    summaries = db.query(Summary).filter(Summary.githubid == githubid).all()
    if not summaries:
        raise HTTPException(status_code=404, detail="No summaries found for this GitHub ID")
    
    return [
        {
            "sumid": str(summary.sumid),
            "repo_link": summary.repo_link,
            "level": summary.level,
            "summary": summary.summary
        }
        for summary in summaries
    ]

@git_router.get("/user_info")
def get_user_info_endpoint(res:dict= Depends(get_user_info) ):

    return res
# @git_router.delete("/delete_summary/{sumid}")
# def delete_summary(sumid: uuid.UUID, db: Session = Depends(get_db)):
#     delete_summary(sumid,db)
#     return {"msg":"Successfully deleted summary "}

@git_router.delete("/delete_summary/{sumid}")
def delete_summary(sumid: uuid.UUID, db: Session = Depends(get_db)):
    # Find the summary by sumid
    summary = db.query(Summary).filter(Summary.sumid == sumid).first()

    if not summary:
        raise HTTPException(status_code=404, detail="Summary not found")

    db.delete(summary)
    db.commit()

    return {"message": "Summary deleted successfully"}
@git_router.get("/logout")
def git_logout_endpoint(msg: dict= Depends(logout_user)):
    return msg