

from sqlalchemy.orm import Session
from database.model import  Summary
from reqmodel.model import AddSummary
import uuid
from fastapi import HTTPException
def add_summary(db: Session, summary_data: AddSummary, githubid: int):
    """Function to add a summary to the database."""
    new_summary = Summary(
        githubid=githubid,
        repo_link=summary_data.repo_link,
        summary=summary_data.summary,
        level=summary_data.level,
    )

    db.add(new_summary)
    db.commit()
    db.refresh(new_summary)
    return new_summary
def delete_summary(sumid: uuid.UUID,db:Session):
    summary = db.query(Summary).filter(Summary.sumid == sumid).first()

    if not summary:
        raise HTTPException(status_code=404, detail="Summary not found")

    db.delete(summary)
    db.commit()
    return summary