#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
News Scraper for Chhattisgarh News Sources
Scrapes news from multiple Hindi news sources
"""

import asyncio
import aiohttp
import requests
from bs4 import BeautifulSoup
import feedparser
import logging
from datetime import datetime, timedelta
import pytz
import json
import time
import random

logger = logging.getLogger(__name__)

class NewsScraper:
    def __init__(self):
        self.ist = pytz.timezone('Asia/Kolkata')
        self.today = datetime.now(self.ist).date()
        
        # Chhattisgarh news sources
        self.sources = {
            # Print Media
            "haribhoomi": {
                "url": "https://www.haribhoomi.com/state/chhattisgarh",
                "rss": "https://www.haribhoomi.com/state/chhattisgarh/feed",
                "type": "rss"
            },
            "navbharat": {
                "url": "https://navbharattimes.indiatimes.com/state/chhattisgarh",
                "type": "web"
            },
            "deshbandhu": {
                "url": "https://deshbandhu.co.in/category/chhattisgarh",
                "type": "web"
            },
            "patrika": {
                "url": "https://www.patrika.com/raipur-news/",
                "rss": "https://www.patrika.com/rss/raipur-news.xml",
                "type": "rss"
            },
            "dainik_bhaskar": {
                "url": "https://www.bhaskar.com/local/chhattisgarh/",
                "rss": "https://www.bhaskar.com/rss-feed/1127/",
                "type": "rss"
            },
            
            # TV Web Portals
            "ibc24": {
                "url": "https://www.ibc24.in/",
                "type": "web"
            },
            "zee_mp_cg": {
                "url": "https://zeenews.india.com/hindi/india/chhattisgarh",
                "type": "web"
            },
            "news18_chhattisgarh": {
                "url": "https://hindi.news18.com/state/chhattisgarh/",
                "rss": "https://hindi.news18.com/rss/state/chhattisgarh.xml",
                "type": "rss"
            },
            
            # Web Channels
            "chhattisgarh_today": {
                "url": "https://chhattisgarh.today/",
                "type": "web"
            },
            "cg_wall": {
                "url": "https://cgwall.com/",
                "type": "web"
            }
        }
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'hi-IN,hi;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }

    async def scrape_rss_source(self, source_name, source_info):
        """Scrape news from RSS feed"""
        try:
            logger.info(f"Scraping RSS: {source_name}")
            
            if "rss" not in source_info:
                return []
                
            feed = feedparser.parse(source_info["rss"])
            articles = []
            
            for entry in feed.entries[:10]:  # Limit to 10 recent articles
                # Check if article is from today
                pub_date = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    pub_date = datetime(*entry.published_parsed[:6])
                    pub_date = pub_date.replace(tzinfo=pytz.UTC).astimezone(self.ist)
                    
                    # Only include today's news
                    if pub_date.date() != self.today:
                        continue
                
                article = {
                    "source": source_name,
                    "title": entry.title if hasattr(entry, 'title') else "",
                    "body": self.clean_text(entry.summary if hasattr(entry, 'summary') else ""),
                    "url": entry.link if hasattr(entry, 'link') else "",
                    "timestamp": pub_date.isoformat() if pub_date else datetime.now(self.ist).isoformat()
                }
                
                # Verify URL is working
                if await self.verify_url(article["url"]):
                    articles.append(article)
                    
            logger.info(f"Found {len(articles)} articles from {source_name}")
            return articles
            
        except Exception as e:
            logger.error(f"Error scraping RSS {source_name}: {e}")
            return []

    async def scrape_web_source(self, source_name, source_info):
        """Scrape news from web page"""
        try:
            logger.info(f"Scraping web: {source_name}")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(source_info["url"], headers=self.headers) as response:
                    if response.status != 200:
                        logger.warning(f"Failed to fetch {source_name}: {response.status}")
                        return []
                    
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    articles = []
                    
                    # Generic article extraction (customize per source)
                    article_selectors = [
                        'article', '.news-item', '.story', '.post',
                        '.news-card', '.article-item', '.content-item'
                    ]
                    
                    for selector in article_selectors:
                        elements = soup.select(selector)
                        if elements:
                            break
                    
                    for element in elements[:10]:  # Limit to 10 articles
                        title_elem = element.find(['h1', 'h2', 'h3', 'h4', '.title', '.headline'])
                        link_elem = element.find('a')
                        
                        if title_elem and link_elem:
                            title = self.clean_text(title_elem.get_text())
                            url = link_elem.get('href', '')
                            
                            # Make URL absolute
                            if url.startswith('/'):
                                base_url = f"https://{source_info['url'].split('/')[2]}"
                                url = base_url + url
                            
                            # Extract body text
                            body_elem = element.find(['p', '.summary', '.excerpt', '.description'])
                            body = self.clean_text(body_elem.get_text()) if body_elem else ""
                            
                            article = {
                                "source": source_name,
                                "title": title,
                                "body": body,
                                "url": url,
                                "timestamp": datetime.now(self.ist).isoformat()
                            }
                            
                            # Verify URL and check if it's Chhattisgarh related
                            if (await self.verify_url(url) and 
                                self.is_chhattisgarh_related(title + " " + body)):
                                articles.append(article)
                    
                    logger.info(f"Found {len(articles)} articles from {source_name}")
                    return articles
                    
        except Exception as e:
            logger.error(f"Error scraping web {source_name}: {e}")
            return []

    async def verify_url(self, url):
        """Verify if URL is accessible (returns 200 status)"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.head(url, headers=self.headers, timeout=10) as response:
                    return response.status == 200
        except:
            return False

    def is_chhattisgarh_related(self, text):
        """Check if text is related to Chhattisgarh"""
        cg_keywords = [
            'छत्तीसगढ़', 'रायपुर', 'बिलासपुर', 'दुर्ग', 'भिलाई', 'कोरबा', 'राजनांदगांव',
            'जगदलपुर', 'अंबिकापुर', 'चांपा', 'धमतरी', 'महासमुंद', 'कांकेर', 'बस्तर',
            'सरगुजा', 'दंतेवाड़ा', 'नारायणपुर', 'बीजापुर', 'सुकमा', 'कोंडागांव',
            'गरियाबंद', 'जांजगीर', 'चांपा', 'सक्ती', 'मुंगेली', 'बलौदाबाजार',
            'बेमेतरा', 'बलरामपुर', 'सूरजपुर', 'chhattisgarh', 'raipur', 'bilaspur'
        ]
        
        text_lower = text.lower()
        return any(keyword.lower() in text_lower for keyword in cg_keywords)

    def clean_text(self, text):
        """Clean and normalize text"""
        if not text:
            return ""
        
        # Remove extra whitespace and newlines
        text = ' '.join(text.split())
        
        # Remove HTML entities
        text = text.replace('&nbsp;', ' ').replace('&amp;', '&')
        text = text.replace('&lt;', '<').replace('&gt;', '>')
        
        return text.strip()

    async def scrape_all_sources(self):
        """Scrape all news sources"""
        logger.info("Starting news scraping from all sources...")
        
        all_articles = []
        tasks = []
        
        for source_name, source_info in self.sources.items():
            if source_info["type"] == "rss":
                task = self.scrape_rss_source(source_name, source_info)
            else:
                task = self.scrape_web_source(source_name, source_info)
            
            tasks.append(task)
            
            # Add delay to avoid overwhelming servers
            await asyncio.sleep(random.uniform(1, 3))
        
        # Execute all scraping tasks
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, list):
                all_articles.extend(result)
            else:
                logger.error(f"Scraping task failed: {result}")
        
        logger.info(f"Total articles scraped: {len(all_articles)}")
        
        # Save raw data for backup
        with open(f'raw_news_{self.today}.json', 'w', encoding='utf-8') as f:
            json.dump(all_articles, f, ensure_ascii=False, indent=2)
        
        return all_articles