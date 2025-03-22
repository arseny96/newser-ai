import yaml
import feedparser
from typing import List, Dict
import logging

logger = logging.getLogger('app')

class RssReader:
    def __init__(self, config_path: str):
        self.sources = self._load_sources(config_path)
        logger.info(f"Loaded {len(self.sources)} RSS sources")

    def _load_sources(self, path: str) -> List[Dict]:
        try:
            with open(path) as f:
                return yaml.safe_load(f)["sources"]
        except Exception as e:
            logger.error(f"Error loading sources: {str(e)}")
            return []

    def get_entries(self) -> List[Dict]:
        entries = []
        for source in self.sources:
            entries.extend(self._process_source(source))
        return entries

    def _process_source(self, source: Dict) -> List[Dict]:
        try:
            feed = feedparser.parse(source["url"])
            return [
                self._parse_entry(entry, source) 
                for entry in feed.entries 
                if self._pass_filters(entry, source.get("filters", {}))
            ]
        except Exception as e:
            logger.error(f"Error processing {source['url']}: {str(e)}", exc_info=True)
            return []

    def _parse_entry(self, entry, source: Dict) -> Dict:
        return {
            "id": entry.id,
            "title": entry.title,
            "content": entry.description,
            "url": entry.link,
            "categories": source["categories"]
        }

    def _pass_filters(self, entry, filters: Dict) -> bool:
        # Получаем данные
        description = entry.get("description", "") or ""
        content = entry.get("content", "")

        # Обрабатываем content, если это список
        if isinstance(content, list):
            content = " ".join([str(item) for item in content])
        else:
            content = str(content)

        # Объединяем содержимое
        full_content = description + content

        # Применяем фильтры
        if "min_length" in filters and len(full_content) < filters["min_length"]:
            return False
        if "max_length" in filters and len(full_content) > filters["max_length"]:
            return False
        if "exclude_keywords" in filters:
            return not any(kw in full_content.lower() for kw in filters["exclude_keywords"])
        return True
