from fastapi import APIRouter
from fastapi import FastAPI, HTTPException
from controllers.gen_summary import generate_summary
from models.gen_summary import SummaryRequest

from pydantic import BaseModel
class SummaryRequest(BaseModel):
    repo_link: str
    level: str
router = APIRouter()
@router.post("/generate_summary")
async def generate_summary_endpoint(request: SummaryRequest):
    try:
        # Call the generate_summary function with the parameters from the request
        summary = generate_summary(request.repo_link, request.level)
        return {"summary": summary}
    except Exception as e:
        # Handle exceptions and return an error response
        raise HTTPException(status_code=500, detail=str(e))
@router.get("/")
async def hello():
    print()