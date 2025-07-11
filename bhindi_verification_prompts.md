# Bhindi AI Verification Prompts for Grok Integration
## Chhattisgarh News Bot - Complete Integration Testing

Copy-paste these prompts into Bhindi AI's premium dashboard to verify Grok integration:

---

## 1. Verify Grok API Connectivity

**Bhindi Prompt:**
```
Check for GROK_API_KEY or Grok 2 HTTP setup in Bhindi environment. If missing, register Grok API at https://x.ai/api or use Azure/Vercel free access. Test with query: 'Check system status.' Send Telegram confirmation: 'Grok API connected successfully' or 'Error: Grok API connection failed.' Verify with Bhindi support that Grok API is free via premium subscription.
```

**Expected Output:** Telegram confirmation of Grok API connectivity
**Health Check:** Log API response; retry if failed
**Fallback:** Use Bhindi's premium support to resolve API issues
**Cost Control:** Confirm free access; alert: "Warning: Grok API may incur $X cost"

---

## 2. Test Grok's Monitoring of Workflow Progress

**Bhindi Prompt:**
```
Run test cycle for July 8, 2025: scrape, verify, summarize, format, MP3, deliver. Send progress updates to Grok API after each stage: scraping (4 AM, 12 PM, 4 PM), verification (5 PM), summarization (6 PM), formatting/MP3 (7 PM), delivery (8 PM). Grok to query Heroku logs and validate schedule. Send Telegram alerts for delays: 'Warning: [Stage] delayed at [Time].' Send status: 'Test cycle progress monitored, all stages completed.'
```

**Expected Output:** Telegram alerts for progress and delays
**Health Check:** Grok logs stage timestamps; flags delays >30 minutes
**Grok Role:** Monitor progress, alert on delays
**Fallback:** Grok triggers Bhindi to restart delayed stages
**Cost Control:** Minimize Grok API calls (~10,000 input tokens/day)

---

## 3. Validate Output Correctness

**Bhindi Prompt:**
```
Grok to validate test cycle outputs: Check Google Drive JSON for 6–8 stories, same-day timestamps, 200-status URLs, sources. Verify Telegram/WhatsApp bulletin for format, 6–8 stories, emojis, no URLs, same-day news. Transcribe MP3 with Whisper, verify Hindi pronunciation ('22 लाख', 'सीबीआई'), duration (1–2 min). Send Telegram alerts: 'Error: [Issue].' Send status: 'Outputs validated, all correct.'
```

**Expected Output:** Telegram validation reports
**Health Check:** Log validation results; retry failed checks
**Grok Role:** Validate JSON, bulletin, MP3; alert on errors
**Fallback:** Grok triggers Bhindi to reprocess incorrect outputs
**Cost Control:** Limit Whisper and Grok API usage

---

## 4. Verify Credibility Checks

**Bhindi Prompt:**
```
Grok to cross-check JSON stories with X posts (minimal DeepSearch) for three-source agreement. Verify no opinions ('चाहिए,' 'कथित'). Detect bias with Think Mode. Send Telegram alerts: 'Warning: [Issue].' Send status: 'Credibility checks passed.'
```

**Expected Output:** Telegram credibility reports
**Health Check:** Log credibility results
**Grok Role:** Ensure three-source verification, alert on issues
**Fallback:** Exclude unverifiable stories
**Cost Control:** Minimize DeepSearch queries

---

## 5. Confirm Delivery Monitoring

**Bhindi Prompt:**
```
Grok to monitor WhatsApp/Telegram for bulletin and MP3 delivery by 8 PM IST. Verify content and WhatsApp 1,000 messages/month limit. Send Telegram alert: 'Error: Delivery delayed past 8 PM IST.' Send status: 'Delivery completed on time.'
```

**Expected Output:** Telegram delivery reports
**Health Check:** Log delivery status
**Grok Role:** Confirm timely delivery, alert on delays
**Fallback:** Grok triggers retry after 5 minutes
**Cost Control:** Monitor WhatsApp limit

---

## 6. Verify System Health Checks

**Bhindi Prompt:**
```
Grok to ping APIs (Telegram, WhatsApp, Google Drive, Bulbul) hourly, check Heroku logs. Send daily Telegram status: 'Bot active, [N] stories delivered, JSON stored.' Alert: 'Error: [API/Process] failed at [Time].'
```

**Expected Output:** Telegram health reports
**Health Check:** Log API and process status
**Grok Role:** Monitor system health, alert on issues
**Fallback:** Grok restarts failed processes
**Cost Control:** Minimize API pings

---

## 7. Verify Cost Control

**Bhindi Prompt:**
```
Confirm Grok API uses free Azure/Vercel access or Bhindi premium coverage. Grok to track API usage (~10,000 input, 5,000 output tokens/day). Send Telegram alert: 'Warning: Grok API cost $X.' Send status: 'Grok API usage within free limits.'
```

**Expected Output:** Telegram cost reports
**Health Check:** Log API usage
**Grok Role:** Monitor costs, alert if non-zero
**Fallback:** Reduce DeepSearch usage if costs detected
**Cost Control:** Prioritize free Grok access

---

## 8. Final Verification

**Bhindi Prompt:**
```
Run test cycle for July 8, 2025. Grok to validate outputs (JSON, bulletin, MP3), progress, credibility, delivery, and costs. Send Telegram report: 'Grok-Bhindi integration verified, all systems operational.'
```

**Expected Output:** Telegram verification report
**Health Check:** Log test results
**Grok Role:** Confirm integration, alert: "Error: Integration issue"
**Fallback:** Refine Bhindi prompts via premium support
**Cost Control:** Ensure zero-cost operation

---

## Quick Verification Script

To run automated verification, use:

```bash
# Set environment variables
export GROK_API_KEY=your_grok_api_key
export TELEGRAM_TOKEN=your_telegram_token
export TELEGRAM_CHAT_ID=your_chat_id

# Run verification
python verify_grok_integration.py
```

## Expected Telegram Alerts

You should receive these alerts during verification:

1. ✅ "Grok API connected successfully"
2. ✅ "Test cycle progress monitored, all stages completed"
3. ✅ "Outputs validated, all correct"
4. ✅ "Credibility checks passed"
5. ✅ "Delivery completed on time"
6. ✅ "Bot active, 8 stories delivered, JSON stored"
7. ✅ "Grok API usage within free limits"
8. 🎉 "Grok-Bhindi integration verified, all systems operational"

## Troubleshooting

**If verification fails:**

1. **API Key Issues:** Get Grok API key from https://x.ai/api
2. **Cost Concerns:** Contact Bhindi support to confirm free access
3. **Integration Problems:** Use Bhindi's premium support
4. **Telegram Alerts:** Check TELEGRAM_TOKEN and TELEGRAM_CHAT_ID

## Cost Monitoring

**Expected daily usage:**
- Input tokens: ~10,000 ($0.03)
- Output tokens: ~5,000 ($0.075)
- **Total: ~$0.105/day** (if charged)

**Free access options:**
- Azure AI (through June 2025)
- Vercel AI marketplace
- Bhindi premium subscription coverage

## Next Steps

1. Copy prompts to Bhindi AI dashboard
2. Run verification cycle
3. Monitor Telegram for alerts
4. Confirm zero-cost operation
5. Deploy to production

---

**🚀 Ready for deployment once all 8 verification steps pass!**