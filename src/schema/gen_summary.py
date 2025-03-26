
from pydantic import BaseModel,Field
class SummaryRequest(BaseModel):
    repo_link: str
    level: str
    file_path: str=''
class CodeSnippet(BaseModel):
    code:str
class CloseRepoRequest(BaseModel):
    repo_link:str
class SummaryResponse(BaseModel):
    title: str = Field(description="title for the summary generated")
    summary: str = Field(description="summary explaining the functionality of the code")    


