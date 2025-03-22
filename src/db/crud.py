from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import ProcessedArticle

class DBCrud:
    def __init__(self, db_url: str):
        engine = create_engine(db_url)
        ProcessedArticle.metadata.create_all(engine)
        self.Session = sessionmaker(bind=engine)
    
    def is_processed(self, article_id: str) -> bool:
        with self.Session() as session:
            return session.query(ProcessedArticle).filter_by(id=article_id).first() is not None
    
    def save_article(self, article_data: dict):
        with self.Session() as session:
            article = ProcessedArticle(
                id=article_data["id"],
                source_url=article_data["source_url"]
            )
            session.add(article)
            session.commit()
