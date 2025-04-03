import requests
from ..ai_processor import BaseAIProcessor

class DeepSeekProcessor(BaseAIProcessor):
    def __init__(self, api_key: str, model_name: str, timeout: int = 30):
        self.api_key = api_key
        self.model_name = model_name
        self.timeout = timeout

    def generate_summary(self, text: str) -> str:  # Убрали categories
        try:
            prompt = f"Напиши краткий пересказ статьи в нейтрально-позитивном стиле с эмодзи. Текст: {text[:5000]}"
            
            response = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "messages": [{"role": "user", "content": prompt}],
                    "model": self.model_name,
                    "temperature": 0.7
                },
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            data_logger.error(f"DeepSeek API error: {str(e)}", exc_info=True)
            return ""
