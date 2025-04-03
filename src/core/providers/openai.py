from openai import OpenAI
from ..ai_processor import BaseAIProcessor
from src.config.logger import data_logger
from src.config.settings import get_settings

config = get_settings()

class OpenAIProcessor(BaseAIProcessor):
    def __init__(self, api_key: str, model_name: str, timeout: int = config.AI_API_TIMEOUT):
        self.client = OpenAI(api_key=api_key)
        self.model_name = model_name
        self.timeout = timeout

    def generate_summary(self, text: str) -> str:  # Убрали categories
        try:
            prompt = f"Сделай на основе этого текста заметку для новостного телеграм канала на тему ИИ. До 1000 символов. В нейтрально-положительном стиле. Перевести с английского на русский. Сделать визуально привлекательным. Сделать просто читаемым как для научно-популярной аудитории. Не вставляй хэштеги. Все эмодзи можно ставить в начало абзаца. Эмодзи не может быть два рядом друг с другом. Необходимо, чтобы текст заметки был отформатирован и динамичен, разбит на пункты, где это предполагается. В ответе не пиши ничего кроме того, что я тебя попросил. Текст: {text[:config.AI_MAX_TEXT_LENGTH]}"

            data_logger.debug(f"*** ПОЛНЫЙ ЗАПРОС К OPENAI ***\n{prompt}\n*** КОНЕЦ ЗАПРОСА ***")

            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                timeout=self.timeout
            )
            return response.choices[0].message.content
        except Exception as e:
            data_logger.error(f"OpenAI API error: {str(e)}", exc_info=True)
            return ""
