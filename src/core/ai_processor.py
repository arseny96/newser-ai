from typing import List
from abc import ABC, abstractmethod
import logging

data_logger = logging.getLogger('data')

class BaseAIProcessor(ABC):
    @abstractmethod
    def generate_summary(self, text: str, categories: List[str]) -> str:
        pass
