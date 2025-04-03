from telegram import Bot
from telegram.error import TelegramError
import logging
import asyncio

logger = logging.getLogger('app')

class TelegramPoster:
    def __init__(self, token: str, channel_id: str):
        self.bot = Bot(token=token)
        self.channel_id = channel_id

    async def send_message(self, text: str, url: str) -> bool:  # Добавили async
        try:
            message = f"{text}\n\n {url}"
            await self.bot.send_message(  # Добавили await
                chat_id=self.channel_id,
                text=message,
                disable_web_page_preview=True
            )
            logger.info(f"Sent message: {url}")
            return True
        except TelegramError as e:
            logger.error(f"Failed to send message: {str(e)}")
            return False
