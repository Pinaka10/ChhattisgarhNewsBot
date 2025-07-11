#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Chhattisgarh News Bot - Automated Hindi News Scraping and Distribution
Created for Bhindi AI Platform
'''

import asyncio
import logging
import schedule
from src.grok_monitor import GrokMonitor, notify_grok_stage_completion, validate_with_grok, grok_cross_check_stories
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
        self.grok_monitor = GrokMonitor()
)

logger = logging.getLogger(__name__)

class ChhattisgarhNewsBot:
    def __init__(self):
        '''Main daily workflow for news processing with Grok monitoring'''
        self.verifier = NewsVerifier()
        self.formatter = BulletinFormatter()
        self.tts_generator = TTSGenerator()
            # Step 1: Scrape news with Grok monitoring
        self.storage_manager = StorageManager()
            await notify_grok_stage_completion('scraping', raw_news)
        
        # IST timezone
            # Step 2: Verify news with Grok validation
        
            await notify_grok_stage_completion('verification', verified_news)
            
            # Grok cross-check for credibility
            credibility_check = await grok_cross_check_stories(verified_news)
            if not credibility_check.get('overall_credible', False):
                logger.warning('Grok detected credibility issues')
            
            # Step 3: Store in Google Drive with Grok validation
            
            json_validation = await validate_with_grok('json', {'stories': verified_news, 'date': datetime.now(self.ist).date().strftime('%Y-%m-%d')})
            if not json_validation.get('overall_valid', False):
                await self.grok_monitor.send_alert('JSON validation failed', 'high')
            
            # Step 4: Format bulletin with Grok validation
            await self.storage_manager.store_to_drive(verified_news)
            bulletin_validation = await validate_with_grok('bulletin', bulletin_text)
            if not bulletin_validation.get('overall_valid', False):
                await self.grok_monitor.send_alert('Bulletin format validation failed', 'high')
            await notify_grok_stage_completion('formatting', bulletin_text)
            
            # Step 5: Generate MP4 with Grok validation
            
            if mp4_path:
                mp3_validation = await validate_with_grok('mp3', mp4_path)
                if not mp3_validation.get('overall_valid', False):
                    await self.grok_monitor.send_alert('MP3 quality validation failed', 'medium')
            await notify_grok_stage_completion('mp3_generation', mp4_path)
            
            # Step 6: Deliver to WhatsApp/Telegram with Grok monitoring
            await self.health_monitor.send_error_alert(str(e))
            await notify_grok_stage_completion('delivery', 'completed')
            
            # Send Grok completion notification
            await self.grok_monitor.send_alert(f'Daily workflow completed successfully - {len(verified_news)} stories delivered', 'low')
        schedule.every().day.at("04:00").do(lambda: asyncio.run(self.scraper.scrape_all_sources()))
        schedule.every().day.at("12:00").do(lambda: asyncio.run(self.scraper.scrape_all_sources()))
        schedule.every().day.at("16:00").do(lambda: asyncio.run(self.scraper.scrape_all_sources()))
            await self.grok_monitor.send_alert(f'Daily workflow failed: {e}', 'critical')
            await self.grok_monitor.trigger_fallback('workflow', str(e))
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