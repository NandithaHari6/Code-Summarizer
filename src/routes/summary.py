from fastapi import APIRouter
from fastapi import FastAPI, HTTPException
from controllers.gen_sum2 import generate_summary,close_repo,get_directory_structure,code_snippet_summary
from controllers.prompts import code_snippet_summary
from schema.gen_summary import SummaryRequest,CloseRepoRequest, CodeSnippet

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
async def generate_file_summary_endpoint(request: SummaryRequest):
    try:
        # Call the generate_summary function with the parameters from the request
        summary = generate_summary(request.repo_link, request.level, request.file_path)
        return {"summary": summary}
    except Exception as e:
        # Handle exceptions and return an error response
        raise HTTPException(status_code=500, detail=str(e))
@router.post("/get_file_structure")
async def generate_file_structure(request: CloseRepoRequest):
    try:
        # Call the generate_summary function with the parameters from the request
        structure = get_directory_structure(request.repo_link)
        return {"structure":structure}
    except Exception as e:
        # Handle exceptions and return an error response
        raise HTTPException(status_code=500, detail=str(e))
@router.post("/generate_code_summary")
async def code_snippet(request: CodeSnippet):
    try:
        # Call the generate_summary function with the parameters from the request
        summary=code_snippet_summary(request.code)
        print(f"Summary is {summary}")
        return {"summary": summary}
    except Exception as e:
        # Handle exceptions and return an error response
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/close_repo")
async def close_repo_request(request: CloseRepoRequest):
    try:
        close_repo(request.repo_link)
        return {"message": f"Successfully closed the repo {request.repo_link}"}
    except Exception as e:
        # Handle exceptions and return an error response
        raise HTTPException(status_code=500, detail=str(e))
@router.get("/")
async def hello():
    print()