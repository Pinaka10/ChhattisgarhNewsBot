#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Chhattisgarh News Bot - Automated Hindi News Scraping and Distribution
Created for Bhindi AI Platform
'''

import asyncio
import logging
import schedule
import time
from datetime import datetime, timezone
import pytz

from src.news_scraper import NewsScraper
from src.news_verifier import NewsVerifier
from src.bulletin_formatter import BulletinFormatter
from src.tts_generator import TTSGenerator
from src.delivery_manager import DeliveryManager
from src.storage_manager import StorageManager
from src.health_monitor import HealthMonitor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('chhattisgarh_news_bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class ChhattisgarhNewsBot:
    def __init__(self):
        self.scraper = NewsScraper()
        self.verifier = NewsVerifier()
        self.formatter = BulletinFormatter()
        self.tts_generator = TTSGenerator()
        self.delivery_manager = DeliveryManager()
        self.storage_manager = StorageManager()
        self.health_monitor = HealthMonitor()
        
        # IST timezone
        self.ist = pytz.timezone('Asia/Kolkata')
        
    async def daily_workflow(self):
        '''Main daily workflow for news processing'''
        try:
            logger.info("Starting daily news workflow...")
            
            # Step 1: Scrape news
            raw_news = await self.scraper.scrape_all_sources()
            logger.info(f"Scraped {len(raw_news)} articles")
            
            # Step 2: Verify news
            verified_news = await self.verifier.verify_news(raw_news)
            logger.info(f"Verified {len(verified_news)} articles")
            
            # Step 3: Store in Google Drive
            await self.storage_manager.store_to_drive(verified_news)
            
            # Step 4: Format bulletin
            bulletin_text = self.formatter.format_bulletin(verified_news)
            
            # Step 5: Generate MP4
            mp4_path = await self.tts_generator.create_bulletin_video(bulletin_text)
            
            # Step 6: Deliver to WhatsApp/Telegram
            await self.delivery_manager.deliver_bulletin(bulletin_text, mp4_path)
            
            logger.info("Daily workflow completed successfully")
            
        except Exception as e:
            logger.error(f"Error in daily workflow: {e}")
            await self.health_monitor.send_error_alert(str(e))

    def schedule_tasks(self):
        '''Schedule all daily tasks'''
        # Scraping times: 4 AM, 12 PM, 4 PM IST
        schedule.every().day.at("04:00").do(lambda: asyncio.run(self.scraper.scrape_all_sources()))
        schedule.every().day.at("12:00").do(lambda: asyncio.run(self.scraper.scrape_all_sources()))
        schedule.every().day.at("16:00").do(lambda: asyncio.run(self.scraper.scrape_all_sources()))
        
        # Main workflow: 5 PM verification, 6 PM summary, 7 PM generation, 8 PM delivery
        schedule.every().day.at("17:00").do(lambda: asyncio.run(self.daily_workflow()))
        
        # Health checks every hour
        schedule.every().hour.do(lambda: asyncio.run(self.health_monitor.health_check()))

    def run(self):
        '''Run the bot'''
        logger.info("Starting Chhattisgarh News Bot...")
        self.schedule_tasks()
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

if __name__ == "__main__":
    bot = ChhattisgarhNewsBot()
    bot.run()