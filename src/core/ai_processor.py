import requests
import logging
from typing import List

data_logger = logging.getLogger('data')

class AIProcessor:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def generate_summary(self, text: str, categories: List[str]) -> str:
        try:
            prompt = f"Переведи и напиши тезисный пересказ для науч-поп телеграм канала на 600 символов в нейтрально-позитивном настроении, как бы немного лично. В начале должна быть тема новости, она должна быть привлекающей, интригующей и явно намекать на смысл новости. Можно добавить немного эмодзи, но нельзя, чтобы два эмодзи стояли рядом. Не надо хэштегов и продающий лозунгов. Все это необходимо на основе следующей статьи({', '.join(categories)}):\n{text[:5000]}"
            
            data_logger.debug(f"Sending request to DeepSeek: {prompt[:200]}...")
            
            response = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "messages": [{"role": "user", "content": prompt}],
                    "model": "deepseek-chat",
                    "temperature": 0.7
                },
                timeout=30
            )
            
            data_logger.debug(f"API response: {response.status_code}")
            return response.json()["choices"][0]["message"]["content"]
            
        except Exception as e:
            data_logger.error(f"API error: {str(e)}")
            return ""
