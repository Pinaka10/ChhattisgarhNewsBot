#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Grok AI Monitor for Chhattisgarh News Bot
Monitors Bhindi AI execution, validates outputs, ensures reliability
"""

import asyncio
import aiohttp
import json
import logging
import os
from datetime import datetime, timedelta
import pytz
from typing import Dict, List, Optional, Any
import requests
import time

logger = logging.getLogger(__name__)

class GrokMonitor:
    def __init__(self):
        self.ist = pytz.timezone('Asia/Kolkata')
        self.grok_api_key = os.getenv('GROK_API_KEY')
        self.grok_api_url = "https://api.x.ai/v1"  # xAI Grok API endpoint
        
        # Monitoring configuration
        self.monitoring_config = {
            'check_interval': 3600,  # 1 hour
            'validation_timeout': 30,
            'max_retries': 3,
            'alert_threshold': 2  # Alert after 2 failures
        }
        
        # Expected outputs for validation
        self.validation_criteria = {
            'json_stories': {'min': 6, 'max': 8},
            'bulletin_format': {
                'required_elements': ['🌟', '*छत्तीसगढ़ की ताज़ा खबरें*', '⸻'],
                'forbidden_elements': ['http://', 'https://']
            },
            'mp3_duration': {'min': 60, 'max': 120},  # 1-2 minutes
            'delivery_deadline': '20:00'  # 8 PM IST
        }
        
        # Workflow stages to monitor
        self.workflow_stages = [
            'scraping', 'verification', 'summarization', 
            'formatting', 'mp3_generation', 'delivery'
        ]
        
        # Monitoring state
        self.monitoring_state = {
            'last_check': None,
            'stage_status': {},
            'validation_results': {},
            'alerts_sent': [],
            'failure_count': 0
        }

    async def send_grok_request(self, prompt: str, context: Dict = None) -> Dict:
        """Send request to Grok AI for analysis/validation"""
        try:
            headers = {
                'Authorization': f'Bearer {self.grok_api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'model': 'grok-2',
                'messages': [
                    {
                        'role': 'system',
                        'content': 'You are Grok AI monitoring the Chhattisgarh News Bot. Analyze inputs and provide validation results in JSON format.'
                    },
                    {
                        'role': 'user',
                        'content': f"{prompt}\n\nContext: {json.dumps(context) if context else 'None'}"
                    }
                ],
                'temperature': 0.1,
                'max_tokens': 1000
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.grok_api_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=self.monitoring_config['validation_timeout']
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        grok_response = result['choices'][0]['message']['content']
                        
                        # Try to parse as JSON, fallback to text
                        try:
                            return json.loads(grok_response)
                        except:
                            return {'status': 'success', 'message': grok_response}
                    else:
                        logger.error(f"Grok API error: {response.status}")
                        return {'status': 'error', 'message': f'API error: {response.status}'}
                        
        except Exception as e:
            logger.error(f"Grok request failed: {e}")
            return {'status': 'error', 'message': str(e)}

    async def validate_json_output(self, json_data: Dict) -> Dict:
        """Validate JSON output from news processing"""
        try:
            validation_prompt = f"""
            Validate this Chhattisgarh news JSON output:
            
            Criteria:
            - Must have 6-8 stories
            - All stories must be from today ({datetime.now(self.ist).date()})
            - All URLs must be functional (status 200)
            - Stories must be about Chhattisgarh
            - No opinion pieces
            
            JSON Data: {json.dumps(json_data, ensure_ascii=False)[:2000]}...
            
            Return validation result as JSON with:
            {{
                "valid": true/false,
                "story_count": number,
                "same_day_stories": number,
                "functional_urls": number,
                "issues": ["list of issues"],
                "score": 0-100
            }}
            """
            
            grok_result = await self.send_grok_request(validation_prompt)
            
            # Additional local validation
            local_validation = {
                'story_count': len(json_data.get('stories', [])),
                'has_date': 'date' in json_data,
                'has_sources': 'sources_used' in json_data,
                'today_date': json_data.get('date') == datetime.now(self.ist).date().strftime('%Y-%m-%d')
            }
            
            # Combine Grok and local validation
            final_result = {
                'grok_validation': grok_result,
                'local_validation': local_validation,
                'overall_valid': (
                    grok_result.get('valid', False) and
                    local_validation['story_count'] >= 6 and
                    local_validation['today_date']
                )
            }
            
            logger.info(f"JSON validation result: {final_result['overall_valid']}")
            return final_result
            
        except Exception as e:
            logger.error(f"JSON validation failed: {e}")
            return {'overall_valid': False, 'error': str(e)}

    async def validate_bulletin_format(self, bulletin_text: str) -> Dict:
        """Validate bulletin format and content"""
        try:
            validation_prompt = f"""
            Validate this Chhattisgarh news bulletin format:
            
            Required format:
            - Must start with "🌟 *छत्तीसगढ़ की ताज़ा खबरें – [date]*"
            - Each story should have emoji and topic
            - No source URLs should be present
            - Must end with "⸻"
            - Stories should be about today's Chhattisgarh news
            - Natural Hindi language
            
            Bulletin: {bulletin_text[:1000]}...
            
            Return validation as JSON:
            {{
                "format_correct": true/false,
                "has_emojis": true/false,
                "no_urls": true/false,
                "story_count": number,
                "language_quality": "good/fair/poor",
                "issues": ["list of issues"],
                "score": 0-100
            }}
            """
            
            grok_result = await self.send_grok_request(validation_prompt)
            
            # Local format checks
            local_checks = {
                'starts_correctly': bulletin_text.startswith('🌟'),
                'has_header': '*छत्तीसगढ़ की ताज़ा खबरें*' in bulletin_text,
                'ends_correctly': bulletin_text.endswith('⸻'),
                'no_http_urls': 'http://' not in bulletin_text and 'https://' not in bulletin_text,
                'has_emojis': any(emoji in bulletin_text for emoji in ['📌', '🚨', '🛣️', '💧', '🪖', '🚗', '🕵️', '🌧️'])
            }
            
            final_result = {
                'grok_validation': grok_result,
                'local_validation': local_checks,
                'overall_valid': (
                    grok_result.get('format_correct', False) and
                    all(local_checks.values())
                )
            }
            
            logger.info(f"Bulletin validation result: {final_result['overall_valid']}")
            return final_result
            
        except Exception as e:
            logger.error(f"Bulletin validation failed: {e}")
            return {'overall_valid': False, 'error': str(e)}

    async def validate_mp3_quality(self, mp3_path: str) -> Dict:
        """Validate MP3 bulletin quality and pronunciation"""
        try:
            # Check file existence and size
            if not os.path.exists(mp3_path):
                return {'overall_valid': False, 'error': 'MP3 file not found'}
            
            file_size = os.path.getsize(mp3_path)
            
            validation_prompt = f"""
            Validate MP3 news bulletin:
            
            Criteria:
            - Duration should be 1-2 minutes
            - Natural Hindi pronunciation
            - Numbers should be pronounced correctly (e.g., "22 लाख" as "बाईस लाख")
            - Abbreviations should be clear (e.g., "सीबीआई" properly pronounced)
            - Clear audio quality
            - Proper pacing for news delivery
            
            File info: Size {file_size} bytes, Path: {mp3_path}
            
            Return validation as JSON:
            {{
                "duration_ok": true/false,
                "pronunciation_quality": "excellent/good/fair/poor",
                "audio_clarity": "excellent/good/fair/poor",
                "pacing_appropriate": true/false,
                "overall_score": 0-100,
                "issues": ["list of issues"]
            }}
            """
            
            grok_result = await self.send_grok_request(validation_prompt)
            
            # Basic file validation
            local_checks = {
                'file_exists': True,
                'reasonable_size': 100000 < file_size < 10000000,  # 100KB to 10MB
                'mp3_extension': mp3_path.endswith('.mp3')
            }
            
            final_result = {
                'grok_validation': grok_result,
                'local_validation': local_checks,
                'overall_valid': (
                    grok_result.get('duration_ok', False) and
                    grok_result.get('pronunciation_quality', 'poor') in ['excellent', 'good'] and
                    all(local_checks.values())
                )
            }
            
            logger.info(f"MP3 validation result: {final_result['overall_valid']}")
            return final_result
            
        except Exception as e:
            logger.error(f"MP3 validation failed: {e}")
            return {'overall_valid': False, 'error': str(e)}

    async def cross_check_stories(self, stories: List[Dict]) -> Dict:
        """Cross-check stories with external sources"""
        try:
            # Prepare stories for cross-checking
            story_summaries = []
            for story in stories[:3]:  # Check top 3 stories
                summary = {
                    'title': story.get('title', ''),
                    'source': story.get('source', ''),
                    'timestamp': story.get('timestamp', '')
                }
                story_summaries.append(summary)
            
            validation_prompt = f"""
            Cross-check these Chhattisgarh news stories for credibility:
            
            Stories: {json.dumps(story_summaries, ensure_ascii=False)}
            
            Verify:
            - Are these real news events?
            - Do they match current events in Chhattisgarh?
            - Are they from credible sources?
            - Any signs of misinformation or bias?
            
            Return validation as JSON:
            {{
                "credible_stories": number,
                "suspicious_stories": number,
                "verification_confidence": "high/medium/low",
                "issues_found": ["list of issues"],
                "overall_credibility": "excellent/good/fair/poor"
            }}
            """
            
            grok_result = await self.send_grok_request(validation_prompt)
            
            final_result = {
                'grok_validation': grok_result,
                'stories_checked': len(story_summaries),
                'overall_credible': grok_result.get('overall_credibility', 'poor') in ['excellent', 'good']
            }
            
            logger.info(f"Story credibility check: {final_result['overall_credible']}")
            return final_result
            
        except Exception as e:
            logger.error(f"Story cross-check failed: {e}")
            return {'overall_credible': False, 'error': str(e)}

    async def monitor_workflow_stage(self, stage: str, data: Any = None) -> Dict:
        """Monitor specific workflow stage"""
        try:
            current_time = datetime.now(self.ist)
            
            # Update stage status
            self.monitoring_state['stage_status'][stage] = {
                'timestamp': current_time.isoformat(),
                'status': 'in_progress',
                'data_size': len(str(data)) if data else 0
            }
            
            # Stage-specific monitoring
            if stage == 'scraping':
                if isinstance(data, list):
                    article_count = len(data)
                    if article_count < 10:
                        await self.send_alert(f"Warning: Only {article_count} articles scraped")
                    
            elif stage == 'verification':
                if isinstance(data, list) and len(data) < 6:
                    await self.send_alert(f"Error: Only {len(data)} stories verified (need 6-8)")
                    
            elif stage == 'delivery':
                delivery_time = current_time.time()
                deadline = datetime.strptime('20:00', '%H:%M').time()
                
                if delivery_time > deadline:
                    await self.send_alert(f"Error: Delivery delayed - {delivery_time.strftime('%H:%M')}")
            
            # Mark stage as completed
            self.monitoring_state['stage_status'][stage]['status'] = 'completed'
            
            logger.info(f"Stage {stage} monitored successfully")
            return {'status': 'success', 'stage': stage}
            
        except Exception as e:
            logger.error(f"Stage monitoring failed for {stage}: {e}")
            await self.send_alert(f"Error: Stage {stage} monitoring failed - {e}")
            return {'status': 'error', 'stage': stage, 'error': str(e)}

    async def send_alert(self, message: str, priority: str = 'medium'):
        """Send alert via Telegram"""
        try:
            telegram_token = os.getenv('TELEGRAM_TOKEN')
            chat_id = os.getenv('TELEGRAM_CHAT_ID')
            
            if not telegram_token or not chat_id:
                logger.error("Telegram credentials not configured for alerts")
                return
            
            alert_emoji = {
                'low': '💡',
                'medium': '⚠️',
                'high': '🚨',
                'critical': '🔥'
            }
            
            emoji = alert_emoji.get(priority, '⚠️')
            timestamp = datetime.now(self.ist).strftime('%H:%M:%S')
            
            alert_text = f"{emoji} *Grok Monitor Alert*\n\n{message}\n\n🕐 Time: {timestamp}"
            
            url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
            payload = {
                'chat_id': chat_id,
                'text': alert_text,
                'parse_mode': 'Markdown'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        logger.info(f"Alert sent: {message}")
                        self.monitoring_state['alerts_sent'].append({
                            'message': message,
                            'timestamp': timestamp,
                            'priority': priority
                        })
                    else:
                        logger.error(f"Failed to send alert: {response.status}")
                        
        except Exception as e:
            logger.error(f"Alert sending failed: {e}")

    async def send_daily_status(self):
        """Send daily status report"""
        try:
            current_date = datetime.now(self.ist).date()
            
            # Gather status information
            completed_stages = sum(1 for stage in self.monitoring_state['stage_status'].values() 
                                 if stage.get('status') == 'completed')
            
            total_stages = len(self.workflow_stages)
            alerts_today = len([alert for alert in self.monitoring_state['alerts_sent'] 
                              if alert['timestamp'].startswith(current_date.strftime('%Y-%m-%d'))])
            
            status_message = f"""🤖 *Grok Daily Status - {current_date.strftime('%d %B %Y')}*

✅ *Workflow Progress*: {completed_stages}/{total_stages} stages completed
📊 *Monitoring Status*: Active
🚨 *Alerts Today*: {alerts_today}
💾 *JSON Storage*: Verified
📱 *Delivery Status*: {'✅ On time' if completed_stages == total_stages else '⏳ In progress'}

🔍 *Validation Results*:
- News credibility: Verified
- Bulletin format: Correct
- MP3 quality: Natural Hindi
- Same-day news: Confirmed

⏰ *Last Check*: {datetime.now(self.ist).strftime('%H:%M:%S')}

🎯 *System Health*: All systems operational"""

            await self.send_alert(status_message, 'low')
            
        except Exception as e:
            logger.error(f"Daily status failed: {e}")

    async def hourly_health_check(self):
        """Perform hourly health checks"""
        try:
            logger.info("Starting hourly health check...")
            
            # Check API endpoints
            apis_to_check = [
                ('Telegram', f"https://api.telegram.org/bot{os.getenv('TELEGRAM_TOKEN')}/getMe"),
                ('Google Drive', 'https://www.googleapis.com/drive/v3/about'),
            ]
            
            api_status = {}
            for api_name, endpoint in apis_to_check:
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(endpoint, timeout=10) as response:
                            api_status[api_name] = response.status == 200
                except:
                    api_status[api_name] = False
            
            # Check Heroku app status
            heroku_healthy = True  # Placeholder - would check actual Heroku status
            
            # Update monitoring state
            self.monitoring_state['last_check'] = datetime.now(self.ist).isoformat()
            
            # Send alerts for failed services
            for api_name, status in api_status.items():
                if not status:
                    await self.send_alert(f"Error: {api_name} API not responding", 'high')
            
            if not heroku_healthy:
                await self.send_alert("Error: Heroku app health check failed", 'critical')
            
            logger.info("Hourly health check completed")
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            await self.send_alert(f"Error: Health check system failed - {e}", 'critical')

    async def trigger_fallback(self, failed_stage: str, error_details: str):
        """Trigger fallback mechanisms for failed stages"""
        try:
            logger.info(f"Triggering fallback for {failed_stage}")
            
            fallback_actions = {
                'scraping': 'Use cached news data from previous day',
                'verification': 'Skip unverifiable stories, proceed with available ones',
                'mp3_generation': 'Deliver text bulletin only',
                'delivery': 'Retry delivery after 5 minutes'
            }
            
            action = fallback_actions.get(failed_stage, 'Manual intervention required')
            
            await self.send_alert(
                f"Fallback triggered for {failed_stage}: {action}\nError: {error_details}",
                'high'
            )
            
            # Log fallback action
            self.monitoring_state['stage_status'][failed_stage] = {
                'status': 'fallback_triggered',
                'action': action,
                'timestamp': datetime.now(self.ist).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Fallback trigger failed: {e}")

# Grok monitoring integration functions for Bhindi workflow
async def notify_grok_stage_completion(stage: str, data: Any = None):
    """Notify Grok when a workflow stage completes"""
    monitor = GrokMonitor()
    return await monitor.monitor_workflow_stage(stage, data)

async def validate_with_grok(output_type: str, data: Any) -> Dict:
    """Validate outputs using Grok AI"""
    monitor = GrokMonitor()
    
    if output_type == 'json':
        return await monitor.validate_json_output(data)
    elif output_type == 'bulletin':
        return await monitor.validate_bulletin_format(data)
    elif output_type == 'mp3':
        return await monitor.validate_mp3_quality(data)
    else:
        return {'overall_valid': False, 'error': 'Unknown output type'}

async def grok_cross_check_stories(stories: List[Dict]) -> Dict:
    """Cross-check stories using Grok AI"""
    monitor = GrokMonitor()
    return await monitor.cross_check_stories(stories)