import json
import os
import glob
import hashlib
import logging
from typing import List, Dict, Optional

logger = logging.getLogger('app')

class JsonReader:
    def __init__(self, articles_dir: str):
        self.articles_dir = articles_dir
        logger.info("Initialized JSON reader")

    def _generate_article_id(self, article: Dict) -> str:
        if article.get('post_id'):
            return article['post_id']
        return hashlib.sha256(article['link'].encode()).hexdigest()[:8]

    def get_entries(self) -> List[Dict]:
        entries = []
        json_files = glob.glob(os.path.join(self.articles_dir, 'articles_*.json'))
        
        for file_path in sorted(json_files, reverse=True):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    articles = json.load(f)
                    for article in articles:
                        entry = self._process_article(article)
                        if entry: 
                            entries.append(entry)
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON in {file_path}: {str(e)}")
            except Exception as e:
                logger.error(f"Error processing {file_path}: {str(e)}")
        
        logger.info(f"Found {len(entries)} valid articles")
        return entries

    def _process_article(self, article: Dict) -> Optional[Dict]:
        if not article.get('full_content'):
            logger.warning(f"Skipping article without content: {article.get('title')}")
            return None

        return {
            'id': self._generate_article_id(article),
            'title': article.get('title', 'No Title'),
            'content': article.get('full_content', ''),
            'url': article.get('link', '')
        }
