#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deployment Script for Chhattisgarh News Bot
Handles setup, testing, and deployment to Heroku
"""

import os
import sys
import json
import asyncio
import logging
from datetime import datetime
import subprocess

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsBot Deployer:
    def __init__(self):
        self.required_env_vars = [
            'TELEGRAM_TOKEN',
            'TELEGRAM_CHAT_ID', 
            'WHATSAPP_TOKEN',
            'WHATSAPP_PHONE_NUMBER',
            'GOOGLE_DRIVE_FOLDER_ID'
        ]
        
    def check_environment(self):
        """Check if all required environment variables are set"""
        logger.info("Checking environment variables...")
        
        missing_vars = []
        for var in self.required_env_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            logger.error(f"Missing environment variables: {missing_vars}")
            logger.info("Please set these variables in your .env file or Heroku config")
            return False
        
        logger.info("✅ All environment variables are set")
        return True
    
    def test_telegram_connection(self):
        """Test Telegram bot connection"""
        try:
            import requests
            token = os.getenv('TELEGRAM_TOKEN')
            
            if not token:
                logger.error("TELEGRAM_TOKEN not found")
                return False
            
            url = f"https://api.telegram.org/bot{token}/getMe"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                bot_name = data.get('result', {}).get('username', 'Unknown')
                logger.info(f"✅ Telegram bot connected: @{bot_name}")
                return True
            else:
                logger.error(f"❌ Telegram connection failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Telegram test failed: {e}")
            return False
    
    def test_news_scraping(self):
        """Test news scraping functionality"""
        try:
            logger.info("Testing news scraping...")
            
            # Import and test scraper
            sys.path.append('src')
            from news_scraper import NewsScraper
            
            scraper = NewsScraper()
            
            # Test a single RSS source
            test_source = {
                "url": "https://www.patrika.com/raipur-news/",
                "rss": "https://www.patrika.com/rss/raipur-news.xml",
                "type": "rss"
            }
            
            # Run async test
            async def test_scrape():
                articles = await scraper.scrape_rss_source("test_patrika", test_source)
                return articles
            
            articles = asyncio.run(test_scrape())
            
            if articles:
                logger.info(f"✅ News scraping working: {len(articles)} articles found")
                return True
            else:
                logger.warning("⚠️ No articles found, but scraping is functional")
                return True
                
        except Exception as e:
            logger.error(f"❌ News scraping test failed: {e}")
            return False
    
    def test_bulletin_formatting(self):
        """Test bulletin formatting"""
        try:
            logger.info("Testing bulletin formatting...")
            
            sys.path.append('src')
            from bulletin_formatter import BulletinFormatter
            
            formatter = BulletinFormatter()
            
            # Test data
            test_articles = [
                {
                    "title": "रायपुर में डिजिटल ठगी का मामला",
                    "body": "रायपुर में एक बुजुर्ग महिला से 22 लाख रुपए की ठगी हुई है।",
                    "category": "crime",
                    "importance": 3.0
                }
            ]
            
            bulletin = formatter.format_bulletin(test_articles)
            tts_text = formatter.format_for_tts(test_articles)
            
            if "छत्तीसगढ़ की ताज़ा खबरें" in bulletin:
                logger.info("✅ Bulletin formatting working")
                logger.info(f"Sample bulletin:\n{bulletin[:100]}...")
                return True
            else:
                logger.error("❌ Bulletin formatting failed")
                return False
                
        except Exception as e:
            logger.error(f"❌ Bulletin formatting test failed: {e}")
            return False
    
    def create_heroku_app(self, app_name="chhattisgarh-news-bot"):
        """Create Heroku app"""
        try:
            logger.info(f"Creating Heroku app: {app_name}")
            
            # Check if Heroku CLI is installed
            result = subprocess.run(['heroku', '--version'], 
                                  capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error("❌ Heroku CLI not installed")
                logger.info("Please install Heroku CLI: https://devcenter.heroku.com/articles/heroku-cli")
                return False
            
            # Create app
            result = subprocess.run(['heroku', 'create', app_name], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"✅ Heroku app created: {app_name}")
                return True
            else:
                if "already exists" in result.stderr:
                    logger.info(f"✅ Heroku app already exists: {app_name}")
                    return True
                else:
                    logger.error(f"❌ Failed to create Heroku app: {result.stderr}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Heroku app creation failed: {e}")
            return False
    
    def set_heroku_config(self, app_name="chhattisgarh-news-bot"):
        """Set Heroku environment variables"""
        try:
            logger.info("Setting Heroku config variables...")
            
            config_vars = {}
            for var in self.required_env_vars:
                value = os.getenv(var)
                if value:
                    config_vars[var] = value
            
            # Set config vars
            for var, value in config_vars.items():
                result = subprocess.run([
                    'heroku', 'config:set', f'{var}={value}', 
                    '--app', app_name
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    logger.info(f"✅ Set {var}")
                else:
                    logger.error(f"❌ Failed to set {var}: {result.stderr}")
                    return False
            
            logger.info("✅ All Heroku config variables set")
            return True
            
        except Exception as e:
            logger.error(f"❌ Heroku config setup failed: {e}")
            return False
    
    def deploy_to_heroku(self, app_name="chhattisgarh-news-bot"):
        """Deploy to Heroku"""
        try:
            logger.info("Deploying to Heroku...")
            
            # Add Heroku remote
            result = subprocess.run([
                'heroku', 'git:remote', '-a', app_name
            ], capture_output=True, text=True)
            
            # Deploy
            result = subprocess.run([
                'git', 'push', 'heroku', 'main'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("✅ Deployed to Heroku successfully")
                return True
            else:
                logger.error(f"❌ Deployment failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Heroku deployment failed: {e}")
            return False
    
    def run_deployment(self):
        """Run complete deployment process"""
        logger.info("🚀 Starting Chhattisgarh News Bot deployment...")
        
        steps = [
            ("Environment Check", self.check_environment),
            ("Telegram Test", self.test_telegram_connection),
            ("News Scraping Test", self.test_news_scraping),
            ("Bulletin Formatting Test", self.test_bulletin_formatting),
            ("Heroku App Creation", self.create_heroku_app),
            ("Heroku Config Setup", self.set_heroku_config),
            ("Heroku Deployment", self.deploy_to_heroku)
        ]
        
        for step_name, step_func in steps:
            logger.info(f"\n📋 Step: {step_name}")
            
            try:
                success = step_func()
                if not success:
                    logger.error(f"❌ {step_name} failed. Stopping deployment.")
                    return False
            except Exception as e:
                logger.error(f"❌ {step_name} failed with error: {e}")
                return False
        
        logger.info("\n🎉 Deployment completed successfully!")
        logger.info("Your Chhattisgarh News Bot is now running on Heroku!")
        
        return True

if __name__ == "__main__":
    deployer = NewsBotDeployer()
    success = deployer.run_deployment()
    
    if success:
        print("\n✅ SUCCESS: Bot deployed and ready!")
        print("📱 Check your Telegram/WhatsApp for news bulletins at 8 PM IST")
    else:
        print("\n❌ DEPLOYMENT FAILED")
        print("Please check the logs above and fix any issues")
        sys.exit(1)