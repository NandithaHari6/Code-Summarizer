import uuid

from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from database.connection import Base, engine

    
class Summary(Base):
    __tablename__ = 'summary'
    
    githubid = Column(Integer, nullable=False)
    sumid = Column(UUID(as_uuid=True),primary_key=True, default=uuid.uuid4)
    repo_link=Column(String)
    level=Column(String)
    summary=Column(String,nullable=False)



Base.metadata.create_all(engine)
