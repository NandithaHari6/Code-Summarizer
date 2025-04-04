from pydantic import BaseModel

class AddSummary(BaseModel):
    repo_link: str
    summary: str
    level: str 
 