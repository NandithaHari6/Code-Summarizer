
from pydantic import BaseModel
class SummaryRequest(BaseModel):
    repo_link: str
    level: str



