# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Website monitoring system with Telegram and Email alerts. Python-based solution for 24/7 uptime monitoring that checks websites every minute and sends instant notifications via Telegram and email when issues are detected.

**Key Features:**
- Continuous website uptime monitoring (default: 60-second intervals)
- Telegram bot notifications for instant alerts
- Email notifications via SMTP (Gmail)
- Hourly status reports with uptime statistics
- Response time tracking and averages
- Uptime percentage calculation

## Development Commands

### Testing & Running
```bash
# Test configuration (verify Telegram, email, website connectivity)
python test.py

# Run monitoring locally
python monitor.py
```

### Deployment
This project is designed to deploy to DigitalOcean App Platform:
- **Build Command**: None required (Python)
- **Run Command**: `python monitor.py`
- **Cost**: $5/month for Basic plan (512MB RAM, 1 vCPU)

## Configuration

The application uses environment variables loaded from `.env`:

**Required Variables:**
- `WEBSITE_URL` - URL to monitor (e.g., https://l.genius.space/free/)
- `CHECK_INTERVAL` - Check frequency in seconds (default: 60)
- `TELEGRAM_BOT_TOKEN` - Token from @BotFather
- `TELEGRAM_CHAT_ID` - Telegram chat ID for alerts

**Optional Variables (Email):**
- `EMAIL_FROM` - Gmail address for sending alerts
- `EMAIL_TO` - Recipient email address
- `EMAIL_PASSWORD` - Gmail App Password (not regular password)
- `SMTP_SERVER` - SMTP server (default: smtp.gmail.com)
- `SMTP_PORT` - SMTP port (default: 587)

## Architecture

### Core Components

**monitor.py** - Main monitoring loop:
- Continuous HTTP GET requests to target website
- Status tracking (up/down state changes)
- Statistics collection (total checks, failures, response times)
- Alert triggering logic (down alerts, recovery alerts, hourly reports)
- Sends notifications via Telegram and email

**test.py** - Configuration validator:
- Verifies all required environment variables are set
- Tests website connectivity
- Validates Telegram bot connection and sends test message
- Validates email configuration and sends test email

### Expected Implementation Pattern

**Monitoring Cycle:**
1. Make HTTP request with timeout (typically 10 seconds)
2. Record response time and status code
3. Update statistics (rolling averages, uptime %)
4. Compare to previous state
5. Send alerts if state changed (UP → DOWN or DOWN → UP)
6. Send hourly summary reports
7. Sleep for CHECK_INTERVAL seconds
8. Repeat

**Statistics Tracking:**
- Total checks counter
- Successful checks counter
- Failed checks counter
- Response time history (typically last 60 checks)
- Calculate uptime percentage: (successful / total) × 100
- Calculate average response time from history

**Alert Types:**

1. **Down Alert** - Triggered when website becomes unavailable:
   - Website URL
   - Status code (or 0 if no response)
   - Error message
   - Timestamp

2. **Recovery Alert** - Triggered when website comes back online:
   - Website URL
   - Status code (should be 200)
   - Response time
   - Downtime duration in seconds
   - Timestamp

3. **Hourly Report** - Sent every hour:
   - Current status (UP/DOWN)
   - Uptime percentage
   - Average response time
   - Total checks in the hour
   - Failed checks count
   - Timestamp

## Dependencies

Expected Python packages (requirements.txt):
- `requests` - HTTP requests to check website
- `python-dotenv` - Load environment variables from .env
- `python-telegram-bot` or direct API calls - Telegram notifications

## Telegram Bot Setup

The Telegram integration requires:
1. Bot token from @BotFather (format: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)
2. Chat ID from @userinfobot (numeric ID)
3. Bot must be started by user (send /start) before it can send messages

Telegram API endpoint: `https://api.telegram.org/bot<TOKEN>/sendMessage`

## Email Setup

Gmail-specific requirements:
- Must use App Password (created at https://myaccount.google.com/apppasswords)
- Requires 2FA enabled on Gmail account
- Uses TLS on port 587
- App password is 16 characters (format: `abcd efgh ijkl mnop`)

## Error Handling

The implementation should handle:
- Network timeouts (connection to website fails)
- DNS resolution failures
- HTTP errors (4xx, 5xx status codes)
- Telegram API failures (retry or log)
- Email sending failures (should not crash the monitor)
- Invalid environment variables (caught by test.py)

## Monitoring Best Practices

When implementing or modifying:
- Keep timeout reasonable (10 seconds recommended)
- Use rolling statistics window (last 60 checks) to avoid memory growth
- Log all checks with timestamp for debugging
- Ensure monitoring loop continues even if notification fails
- Add User-Agent header if website blocks bots
- Consider rate limiting to avoid being blocked

## Customization Points

Common modifications documented in tech-spec.md:
- Multiple website monitoring (run multiple instances or loop in code)
- Custom check intervals (modify CHECK_INTERVAL)
- Content validation (check for specific text in response)
- SSL certificate expiry monitoring
- Database integration for long-term statistics (SQLite recommended)
- Daily/weekly report generation

## File Structure

Expected structure when implemented:
```
.
├── monitor.py           # Main monitoring script
├── test.py              # Configuration testing script
├── requirements.txt     # Python dependencies
├── .env.example        # Template for environment variables
├── .env                # Actual config (gitignored)
├── runtime.txt         # Python version for DigitalOcean (optional)
├── docs/
│   └── tech-spec.md    # Complete technical specification
└── CLAUDE.md           # This file
```

## Important Notes

- The monitor runs continuously - it's a long-running process, not a cron job
- Downtime detection accuracy is limited by CHECK_INTERVAL (60s default)
- Response time includes full HTTP round-trip, not just server processing
- Statistics reset when the monitor restarts (unless persisted to database)
- Telegram messages have rate limits - avoid sending too frequently
