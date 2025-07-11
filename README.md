# छत्तीसगढ़ न्यूज़ बॉट (Chhattisgarh News Bot)

Automated Hindi News Bot for Chhattisgarh with WhatsApp/Telegram delivery, news scraping, verification, and MP4 bulletin generation.

## 🌟 Features

- **Automated News Scraping**: Scrapes news from 30+ Chhattisgarh sources
- **AI-Powered Verification**: Uses Hindi-BERT for cross-source validation
- **Smart Formatting**: Creates emoji-rich bulletins in proper Hindi format
- **TTS Integration**: Generates 1-2 minute MP4 news bulletins with natural Hindi pronunciation
- **Multi-Platform Delivery**: Delivers to WhatsApp and Telegram groups
- **Google Drive Storage**: Stores verified articles with functional URLs
- **Health Monitoring**: 100% reliability with fallback mechanisms
- **Scheduled Operations**: Fully automated daily workflow

## 📱 Delivery Format

```
🌟 छत्तीसगढ़ की ताज़ा खबरें – 11 जुलाई 2025

📌 हाई कोर्ट का फैसला: बी.ई. डिग्रीधारकों को PHE भर्ती परीक्षा में आवेदन की अनुमति।

🚨 डिजिटल अरेस्ट फ्रॉड: रायपुर में बुजुर्ग महिला से 22 लाख की ठगी।

🛣️ फोरलेन सड़क परियोजना: गढ़वा-अंबिकापुर तक 160 किमी फोरलेन सड़क बनेगी।

⸻
```

## 🏗️ Architecture

### Core Modules

1. **News Scraper** (`src/news_scraper.py`)
   - RSS feed scraping
   - Web page scraping
   - URL verification
   - Chhattisgarh keyword filtering

2. **News Verifier** (`src/news_verifier.py`)
   - Hindi-BERT embeddings
   - Cross-source validation
   - Opinion piece filtering
   - Importance scoring

3. **Bulletin Formatter** (`src/bulletin_formatter.py`)
   - Emoji categorization
   - WhatsApp/Telegram formatting
   - TTS-optimized text

4. **TTS Generator** (`src/tts_generator.py`)
   - Natural Hindi pronunciation
   - MP4 video generation
   - Duration validation

5. **Delivery Manager** (`src/delivery_manager.py`)
   - Multi-platform delivery
   - Retry mechanisms
   - Usage tracking

6. **Storage Manager** (`src/storage_manager.py`)
   - Google Drive integration
   - JSON structure
   - Data validation

7. **Health Monitor** (`src/health_monitor.py`)
   - System monitoring
   - API health checks
   - Fallback mechanisms

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/Pinaka10/ChhattisgarhNewsBot.git
cd ChhattisgarhNewsBot
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
cp .env.example .env
# Edit .env with your API tokens
```

### 4. Set Up APIs

#### Telegram Bot
1. Message @BotFather on Telegram
2. Create new bot: `/newbot`
3. Get token and add to `.env`

#### WhatsApp Business API
1. Register at Meta Developer Portal
2. Set up WhatsApp Business API
3. Get token and phone number

#### Google Drive
1. Create Google Cloud Project
2. Enable Drive API
3. Download credentials.json

### 5. Deploy to Heroku

#### Option A: Manual Deploy
```bash
heroku create chhattisgarh-news-bot
heroku config:set TELEGRAM_TOKEN=your_token
heroku config:set WHATSAPP_TOKEN=your_token
git push heroku main
```

#### Option B: One-Click Deploy
[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/Pinaka10/ChhattisgarhNewsBot)

## ⏰ Daily Schedule

- **4 AM, 12 PM, 4 PM IST**: News scraping
- **5 PM IST**: News verification
- **6 PM IST**: Summary generation
- **7 PM IST**: Bulletin and MP4 creation
- **8 PM IST**: Delivery to WhatsApp/Telegram

## 📊 News Sources

### Print Media
- हरिभूमि, नवभारत, देशबंधु, पत्रिका, दैनिक भास्कर
- दैनिक छत्तीसगढ़, अमृत संदेश, नई दुनिया, जागरण

### TV Web Portals
- IBC-24, Zee MP-CG, News18 छत्तीसगढ़, Capital TV
- Grand News, BTV News, HM News, CG News

### Web Channels
- छत्तीसगढ़ Today, CG Wall, रायपुर News
- छत्तीसगढ़ी खबर, बिलासपुर Live

## 🔧 Configuration

### Environment Variables
```bash
TELEGRAM_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_chat_id
WHATSAPP_TOKEN=your_whatsapp_token
WHATSAPP_PHONE_NUMBER=your_phone_number
GOOGLE_DRIVE_CREDENTIALS=path_to_credentials.json
GOOGLE_DRIVE_FOLDER_ID=your_drive_folder_id
```

### Customization
- Modify `src/news_scraper.py` to add new sources
- Update `src/bulletin_formatter.py` for format changes
- Adjust `src/health_monitor.py` for monitoring preferences

## 📈 Monitoring

### Health Checks
- System resource monitoring
- API availability checks
- Scraping success rates
- Delivery confirmation

### Fallback Mechanisms
- Cached data usage
- Alternative source switching
- Retry logic with exponential backoff
- Error alerting via Telegram

## 🛠️ Development

### Local Testing
```bash
python -m pytest tests/
python main.py  # Run locally
```

### Adding New Sources
1. Add source to `news_scraper.py`
2. Test scraping functionality
3. Update verification logic if needed

### Debugging
- Check logs: `tail -f chhattisgarh_news_bot.log`
- Monitor health: Check Telegram alerts
- Validate data: Review Google Drive JSON files

## 📝 Data Storage

### JSON Structure
```json
{
  "date": "2025-07-11",
  "generated_at": "2025-07-11T20:00:00+05:30",
  "total_articles": 8,
  "sources_used": ["haribhoomi", "patrika", "ibc24"],
  "stories": [
    {
      "id": 1,
      "source": "haribhoomi",
      "title": "न्यूज़ शीर्षक",
      "body": "न्यूज़ विवरण",
      "url": "https://example.com/news",
      "timestamp": "2025-07-11T15:30:00+05:30",
      "summary": "संक्षिप्त सारांश",
      "category": "politics",
      "importance": 2.5,
      "verified": true,
      "source_count": 3,
      "url_status": "active"
    }
  ]
}
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/Pinaka10/ChhattisgarhNewsBot/issues)
- **Documentation**: [Wiki](https://github.com/Pinaka10/ChhattisgarhNewsBot/wiki)
- **Contact**: Create an issue for support

## 🙏 Acknowledgments

- **Bhindi AI Platform** for infrastructure
- **Hindi-BERT** for natural language processing
- **Chhattisgarh News Sources** for content
- **Open Source Community** for tools and libraries

---

**Made with ❤️ for छत्तीसगढ़**