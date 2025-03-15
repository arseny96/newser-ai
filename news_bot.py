import feedparser
import sqlite3
import asyncio
import time
import requests
import traceback
from bs4 import BeautifulSoup
from telegram import Bot
from telegram.error import TelegramError
from config import CONFIG, get_feed_list, app_logger, data_logger

class NewsBot:
    def __init__(self):
        self.app_logger = app_logger.getChild('NewsBot')
        self.data_logger = data_logger.getChild('Network')
        self.db_conn = sqlite3.connect(CONFIG['database'])
        self._init_db()
        self.bot = Bot(token=CONFIG['telegram']['bot_token'])

    def _init_db(self):
        cursor = self.db_conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS processed_articles (
                source_url TEXT,
                article_id TEXT,
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (source_url, article_id)
                )
        ''')
        self.db_conn.commit()

    async def _clean_html(self, text):
        try:
            soup = BeautifulSoup(text, 'html.parser')
            return soup.get_text(separator=' ', strip=True)
        except Exception as e:
            self.app_logger.error(f"HTML cleaning failed: {str(e)}")
            return text

    async def _get_full_text(self, url):
        try:
            self.app_logger.info(f"Fetching content from: {url}")
            response = requests.get(
                url,
                headers={'User-Agent': CONFIG['user_agent']},
                timeout=CONFIG['timeouts']['http']
            )
            
            self.data_logger.debug(
                "HTTP Request:\nURL: %s\nStatus: %d\nHeaders: %s\nBody: %.200s...",
                url,
                response.status_code,
                dict(response.headers),
                response.text
            )
            
            soup = BeautifulSoup(response.text, 'html.parser')
            return ' '.join([p.text for p in soup.find_all('p')])
            
        except Exception as e:
            self.data_logger.error(
                "Request Failed:\nURL: %s\nError: %s\nTraceback: %s",
                url,
                str(e),
                traceback.format_exc()
            )
            return ""

    async def _process_article(self, text):
        try:
            self.app_logger.info("Processing article with AI")
            headers = {
                "Authorization": f"Bearer {CONFIG['deepseek']['api_key']}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "messages": [{
                    "role": "user",
                    "content": f"Не пиши ничего кроме того, что я тебя попорошу в следующем задании\nПереведи на русский язык и создай на основе текста новость для телеграм канала на 800 символов. Этот текст не должен ссылаться на какие-то ресурсы, он должен писаться как будто от лица редакции этого канала. Настроение должно быть легкое и ненавязчивое. При этом, нужно обязательно писать привлекающий внимание заголовок и чтобы он был выделен жирным шрифтом через markdown (**example**). Текст следуюший:\n\n{text[:6000]}"
                }],
                "model": CONFIG['deepseek']['model'],
                "temperature": 0.7
            }
            
            self.data_logger.debug(
                "DeepSeek Request:\nHeaders: %s\nPayload: %.500s...",
                {k: "***" if k == "Authorization" else v for k, v in headers.items()},
                str(payload)
                )

            response = requests.post(
                CONFIG['deepseek']['api_url'],
                json=payload,
                headers=headers,
                timeout=CONFIG['timeouts']['ai_api']
            )
            
            self.data_logger.debug(
                "DeepSeek Response:\nStatus: %d\nBody: %.1000s...",
                response.status_code,
                response.text
            )
            
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
            
        except Exception as e:
            self.data_logger.error(
                "AI Processing Failed:\nError: %s\nTraceback: %s",
                str(e),
                traceback.format_exc()
            )
            return None

    async def _send_to_telegram(self, message, article_url):
        max_retries = 3
        retry_delay = 5
        max_length = CONFIG['max_message_length']
        
        for attempt in range(max_retries):
            try:
                self.app_logger.info(f"Sending message (attempt {attempt+1}/{max_retries})")
                
                # Обрезаем сообщение по лимиту Telegram
                formatted_msg = f"{message}\n\n🔗 [Читать полностью]({article_url})"
                if len(formatted_msg) > max_length:
                    formatted_msg = formatted_msg[:max_length-100] + "... [truncated]"

                await self.bot.send_message(
                    chat_id=CONFIG['telegram']['channel_id'],
                    text=formatted_msg,
                    parse_mode='Markdown',
                    disable_web_page_preview=True,
                    read_timeout=CONFIG['timeouts']['telegram'],
                    write_timeout=CONFIG['timeouts']['telegram'],
                    connect_timeout=CONFIG['timeouts']['telegram']
                )
                return True
                
            except TelegramError as e:
                error_msg = f"Telegram error: {str(e)}"
                if attempt < max_retries - 1:
                    self.data_logger.warning(f"Attempt {attempt+1} failed: {error_msg}")
                    await asyncio.sleep(retry_delay)
                else:
                    self.data_logger.error(f"{error_msg}\nTraceback: {traceback.format_exc()}")
                    return False
            except Exception as e:
                self.data_logger.error(
                    "Unexpected error: %s\nTraceback: %s",
                    str(e),
                    traceback.format_exc()
                )
                return False

    async def _process_feed(self, rss_url):
        try:
            self.app_logger.info(f"Processing feed: {rss_url}")
            cursor = self.db_conn.cursor()
            feed = feedparser.parse(rss_url)
            
            self.data_logger.debug(
                "RSS Feed Data:\nURL: %s\nEntries: %d\nSample: %s",
                rss_url,
                len(feed.entries),
                [{"title": e.title, "link": e.link} for e in feed.entries[:3]]
            )
            
            entries = feed.entries[:1]
            self.app_logger.info(f"Found {len(entries)} articles to process")
            
            for entry in entries:
                self.data_logger.debug(
                    "Processing RSS Entry:\nTitle: %s\nLink: %s\nID: %s",
                    entry.get('title', 'No title'),
                    entry.get('link', 'No link'),
                    entry.get('id', 'No ID')
                )

                cursor.execute('''
                    SELECT 1 FROM processed_articles 
                    WHERE source_url = ? AND article_id = ?
                ''', (rss_url, entry.id))
                
                if cursor.fetchone():
                    self.app_logger.debug("Skipping processed article")
                    continue

                try:
                    content = await self._clean_html(entry.get('description', ''))
                    if not content:
                        content = await self._get_full_text(entry.link)

                    summary = await self._process_article(content)
                    if not summary:
                        continue

                    if await self._send_to_telegram(summary, entry.link):
                        cursor.execute('''
                            INSERT INTO processed_articles (source_url, article_id)
                            VALUES (?, ?)
                        ''', (rss_url, entry.id))
                        self.db_conn.commit()
                        self.app_logger.info(f"Processed article: {entry.id[:20]}...")

                except Exception as e:
                    self.app_logger.error(f"Article processing failed: {str(e)}")
                    self.db_conn.rollback()
                    
        except Exception as e:
            self.app_logger.error(f"Feed processing error: {str(e)}")

    async def run(self):
        self.app_logger.info("Starting NewsBot service")
        while True:
            try:
                start_time = time.time()
                
                for feed_url in get_feed_list():
                    await self._process_feed(feed_url)
                
                elapsed = time.time() - start_time
                sleep_time = max(CONFIG['check_interval'] - elapsed, 0)
                self.app_logger.debug(f"Cycle completed. Sleeping {sleep_time:.1f}s")
                await asyncio.sleep(sleep_time)
                
            except KeyboardInterrupt:
                self.app_logger.info("Shutting down by user request")
                break
            except Exception as e:
                self.app_logger.critical(f"Critical error: {str(e)}")
                await asyncio.sleep(60)

if __name__ == "__main__":
    bot = NewsBot()
    asyncio.run(bot.run())
