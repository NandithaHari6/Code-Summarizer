from fastapi import APIRouter
from fastapi import FastAPI, HTTPException
from controllers.gen_summary import generate_summary,close_repo
from schema.gen_summary import SummaryRequest,CloseRepoRequest

router = APIRouter()
@router.post("/generate_folder_summary")
async def generate_summary_endpoint(request: SummaryRequest):
    try:
        # Call the generate_summary function with the parameters from the request
        summary = generate_summary(request.repo_link, request.level)
        return {"summary": summary}
    except Exception as e:
        # Handle exceptions and return an error response
        raise HTTPException(status_code=500, detail=str(e))
@router.post("/generate_file_summary")
async def generate_summary_endpoint(request: SummaryRequest):
    try:
        # Call the generate_summary function with the parameters from the request
        summary = generate_summary(request.repo_link, request.level, request.file_path)
        return {"summary": summary}
    except Exception as e:
        # Handle exceptions and return an error response
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/close_repo")
async def close_repo_request(request: CloseRepoRequest):
    try:
        close_repo(request.repo_link)
        return {"message": f"Successfully clsed the repo {request.repo_link}"}
    except Exception as e:
        # Handle exceptions and return an error response
        raise HTTPException(status_code=500, detail=str(e))
@router.get("/")
async def hello():
    print()