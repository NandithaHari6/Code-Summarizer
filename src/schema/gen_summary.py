
from pydantic import BaseModel
class SummaryRequest(BaseModel):
    repo_link: str
    level: str
    file_path: str
class CloseRepoRequest(BaseModel):
    repo_link:str



