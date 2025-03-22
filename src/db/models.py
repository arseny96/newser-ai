from sqlalchemy import create_engine, Column, String, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class ProcessedArticle(Base):
    __tablename__ = "processed_articles"
    
    id = Column(String, primary_key=True)
    source_url = Column(String)
    is_processed = Column(Boolean, default=False)
