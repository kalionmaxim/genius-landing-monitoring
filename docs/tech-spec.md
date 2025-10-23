# Website Monitoring with Telegram & Email Alerts 🚨

**Simple Python solution for 24/7 website uptime monitoring**

---

## 📋 Table of Contents

1. [Features](#features)
2. [Quick Start (5 minutes)](#quick-start)
3. [How It Works](#how-it-works)
4. [Configuration](#configuration)
5. [Deploy to DigitalOcean](#deploy-to-digitalocean)
6. [Testing](#testing)
7. [Troubleshooting](#troubleshooting)
8. [Customization](#customization)

---

## ✨ Features

- ✅ **Website uptime monitoring** - Check every minute
- 📱 **Telegram notifications** - Instant alerts
- 📧 **Email notifications** - Backup channel
- 📊 **Hourly reports** - Status summaries
- ⚡️ **Response time tracking** - Performance monitoring
- 📈 **Uptime statistics** - Calculate availability %
- 🚀 **Simple deployment** - Ready for DigitalOcean
- 💰 **Cost effective** - $5/month for 24/7 monitoring

---

## 🚀 Quick Start

### What You Need

| Item | Time | Where to Get |
|------|------|--------------|
| Telegram Bot Token | 2 min | @BotFather in Telegram |
| Telegram Chat ID | 1 min | @userinfobot in Telegram |
| Gmail App Password | 2 min | https://myaccount.google.com/apppasswords |

### Installation

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Copy configuration template
cp .env.example .env

# 3. Edit .env with your values
nano .env  # or use any text editor

# 4. Test configuration
python test.py

# 5. Start monitoring
python monitor.py
```

---

## 🔧 Configuration

### Step 1: Create Telegram Bot

1. Open Telegram and search for `@BotFather`
2. Send command: `/newbot`
3. Follow the prompts:
   - **Bot name**: `My Website Monitor`
   - **Bot username**: `my_website_monitor_bot` (must be unique)
4. Copy the token (looks like `7234567890:AAGHfJ8kLmNoPqRsTuVwXyZ1234567890AB`)
5. **Save this token** - you'll need it!

### Step 2: Get Your Chat ID

**Option A: Using @userinfobot (Easiest)**
1. Search for `@userinfobot` in Telegram
2. Send `/start`
3. Copy your ID (example: `123456789`)

**Option B: Manual Method**
1. Start a chat with YOUR bot (send `/start`)
2. Open this URL in browser (replace `<YOUR_TOKEN>` with your bot token):
   ```
   https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates
   ```
3. Look for `"chat":{"id":123456789` and copy the number

### Step 3: Gmail App Password (Optional, for Email Alerts)

1. Go to https://myaccount.google.com/apppasswords
2. Sign in to your Gmail account
3. Create new app password:
   - App name: `Website Monitor`
   - Click **Create**
4. Copy the 16-character password (looks like: `abcd efgh ijkl mnop`)
5. **Save this password** - you'll need it!

### Step 4: Configure .env File

Edit your `.env` file with your values:

```env
# Website to monitor
WEBSITE_URL=https://l.genius.space/free/

# Check interval in seconds (60 = every minute)
CHECK_INTERVAL=60

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=7234567890:AAGHfJ8kLmNoPqRsTuVwXyZ1234567890AB
TELEGRAM_CHAT_ID=123456789

# Email Configuration (Optional - leave empty to disable)
EMAIL_FROM=your.email@gmail.com
EMAIL_TO=alerts@example.com
EMAIL_PASSWORD=abcd efgh ijkl mnop
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

---

## 🧪 Testing

Before deploying, test your configuration:

```bash
python test.py
```

**Expected output:**
```
🧪 Testing Configuration...

📋 Required Variables:
  ✅ WEBSITE_URL: https://l.genius.space/free/
  ✅ TELEGRAM_BOT_TOKEN: 7234567890...
  ✅ TELEGRAM_CHAT_ID: 123456789

🌐 Testing Website...
  ✅ Status: 200
  ⚡️ Time: 234.56ms
  ✅ Website is UP

📱 Testing Telegram...
  ✅ Bot connected: @my_website_monitor_bot
  ✅ Test message sent to chat 123456789

📧 Testing Email...
  ✅ Test email sent successfully

✅ Configuration test complete!
```

---

## 🎯 How It Works

### Monitoring Loop

The script runs continuously and:

1. **Checks website every minute** (configurable)
   - Makes HTTP GET request
   - Measures response time
   - Records status code

2. **Tracks statistics**
   - Total checks
   - Successful checks
   - Failed checks
   - Average response time
   - Uptime percentage

3. **Sends alerts when:**
   - Website goes DOWN
   - Website comes back UP
   - Hourly status report

### Alert Examples

#### 🚨 Down Alert
```
🚨 WEBSITE DOWN!

🌐 https://l.genius.space/free/
❌ Status: DOWN
📊 Code: 0
⚠️ Error: Connection timeout
⏰ 2025-10-23 14:30:15
```

#### ✅ Recovery Alert
```
✅ WEBSITE RECOVERED

🌐 https://l.genius.space/free/
✅ Status: UP
📊 Code: 200
⚡️ Response: 234ms
⏱ Downtime: 125s
```

#### 📊 Hourly Report
```
📊 Hourly Report

🌐 Website: https://l.genius.space/free/
✅ Status: UP
📈 Uptime: 98.33%
⏱ Avg Response Time: 245ms
🔍 Total Checks: 60
❌ Failed: 1

⏰ 2025-10-23 15:00:00
```

---

## 🚢 Deploy to DigitalOcean

### Prerequisites

- GitHub account
- DigitalOcean account (free trial available)
- Your project pushed to GitHub

### Step-by-Step Deployment

#### 1. Push to GitHub

```bash
# Initialize git repository
git init

# Add files
git add .

# Commit
git commit -m "Initial commit: Website monitor"

# Add remote (replace with your repo URL)
git remote add origin https://github.com/YOUR_USERNAME/website-monitor.git

# Push
git push -u origin main
```

#### 2. Create App on DigitalOcean

1. Go to https://cloud.digitalocean.com/apps
2. Click **Create App**
3. Choose **GitHub** as source
4. Authorize DigitalOcean to access your repos
5. Select your `website-monitor` repository
6. Branch: `main`
7. Click **Next**

#### 3. Configure App Settings

**Basic Settings:**
- **Name**: `website-monitor`
- **Region**: Choose closest to you (e.g., `Frankfurt`)
- **Plan**: Select **Basic ($5/month)**

**Build & Run:**
- **Build Command**: Leave empty (Python doesn't need build)
- **Run Command**: `python monitor.py`

Click **Next**

#### 4. Add Environment Variables

Click **Add Environment Variable** for each:

| Variable Name | Value | Encrypt? |
|---------------|-------|----------|
| `WEBSITE_URL` | `https://l.genius.space/free/` | No |
| `CHECK_INTERVAL` | `60` | No |
| `TELEGRAM_BOT_TOKEN` | Your bot token from @BotFather | **✅ YES** |
| `TELEGRAM_CHAT_ID` | Your chat ID from @userinfobot | **✅ YES** |
| `EMAIL_FROM` | Your Gmail address | **✅ YES** |
| `EMAIL_TO` | Alert recipient email | No |
| `EMAIL_PASSWORD` | Gmail app password | **✅ YES** |
| `SMTP_SERVER` | `smtp.gmail.com` | No |
| `SMTP_PORT` | `587` | No |

**Important:** Mark sensitive values (tokens, passwords) as encrypted!

#### 5. Review & Deploy

1. Review all settings
2. Click **Create Resources**
3. Wait 3-5 minutes for deployment
4. Watch the logs for:
   ```
   🚀 Starting monitor for https://l.genius.space/free/
   ⏱ Check interval: 60s
   ✅ UP | 234.56ms | 2025-10-23T14:30:00
   ```

#### 6. Verify It's Working

Within 1-2 minutes, you should receive:
- Telegram message confirming the monitor is running
- First status check notification

---

## 🔍 Monitoring & Logs

### View Logs in DigitalOcean

1. Go to your App dashboard
2. Click **Logs** tab
3. You'll see real-time output:
   ```
   ✅ UP | 234ms | 2025-10-23T14:30:00
   ✅ UP | 245ms | 2025-10-23T14:31:00
   ✅ UP | 231ms | 2025-10-23T14:32:00
   ```

### View Stats in Telegram

Your bot will automatically send:
- Instant alerts when site goes down
- Recovery notifications when site comes back up
- Hourly summary reports with statistics

---

## 🛠 Troubleshooting

### Telegram Not Working?

**Issue:** No messages received

**Solutions:**
- ✅ Verify bot token is correct (from @BotFather)
- ✅ Make sure you sent `/start` to your bot first
- ✅ Check chat ID is a number (no quotes in .env)
- ✅ Test with: `python test.py`

**Test manually:**
```bash
# Replace with your values
curl "https://api.telegram.org/bot<YOUR_TOKEN>/sendMessage?chat_id=<YOUR_CHAT_ID>&text=Test"
```

### Email Not Working?

**Issue:** Emails not being sent

**Solutions:**
- ✅ Use App Password, NOT regular Gmail password
- ✅ Enable 2FA in Gmail first (required for app passwords)
- ✅ Check spam/junk folder
- ✅ Verify SMTP settings are correct
- ✅ Test with: `python test.py`

**Gmail App Password:**
1. Must have 2FA enabled
2. Go to: https://myaccount.google.com/apppasswords
3. Create new app password
4. Use this 16-char password (no spaces)

### Website Always Shows "DOWN"?

**Issue:** Site appears down but it's actually up

**Solutions:**
- ✅ Check URL is correct (include `https://`)
- ✅ Try opening URL in browser
- ✅ Check if site requires authentication
- ✅ Increase timeout: modify `timeout=10` in `monitor.py`
- ✅ Check if site blocks bots (add User-Agent header)

### DigitalOcean Deployment Fails?

**Issue:** App fails to build or deploy

**Solutions:**
- ✅ Check `requirements.txt` has correct packages
- ✅ Verify `runtime.txt` specifies Python version
- ✅ Review build logs for errors
- ✅ Make sure all files are committed to Git
- ✅ Check environment variables are set correctly

---

## 🎨 Customization

### Monitor Multiple Websites

**Option 1: Run Multiple Instances**

Create separate `.env` files:
```bash
# .env.site1
WEBSITE_URL=https://site1.com
TELEGRAM_CHAT_ID=123456789

# .env.site2
WEBSITE_URL=https://site2.com
TELEGRAM_CHAT_ID=123456789
```

Run each:
```bash
python monitor.py --env .env.site1 &
python monitor.py --env .env.site2 &
```

**Option 2: Modify Script**

Edit `monitor.py` to check multiple URLs in a loop.

### Change Check Frequency

```env
# Check every 30 seconds
CHECK_INTERVAL=30

# Check every 5 minutes
CHECK_INTERVAL=300

# Check every 10 minutes
CHECK_INTERVAL=600
```

### Customize Alert Messages

Edit the message templates in `monitor.py`:

```python
# Down alert (line ~120)
message = f"""
🚨 ALERT: WEBSITE DOWN!

Your custom message here
URL: {WEBSITE_URL}
...
"""

# Hourly report (line ~85)
message = f"""
📊 Your Custom Report

Add your own stats and formatting
...
"""
```

### Disable Email (Telegram Only)

Just don't set these variables in `.env`:
```env
# Leave these empty or remove them
EMAIL_FROM=
EMAIL_TO=
EMAIL_PASSWORD=
```

### Add Content Checking

Check if page contains specific text:

```python
def check_website():
    response = requests.get(WEBSITE_URL, timeout=10)
    
    # Check status code
    if response.status_code != 200:
        return {'is_up': False, ...}
    
    # Check content
    if "Expected Text" not in response.text:
        return {'is_up': False, 'error': 'Content check failed'}
    
    return {'is_up': True, ...}
```

### Add SSL Certificate Monitoring

Check SSL expiry:

```python
import ssl
import socket
from datetime import datetime

def check_ssl_expiry(hostname):
    context = ssl.create_default_context()
    with socket.create_connection((hostname, 443)) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
            cert = ssock.getpeercert()
            expiry = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
            days_left = (expiry - datetime.now()).days
            return days_left
```

---

## 📊 Statistics & Reporting

### Current Implementation

The script tracks:
- ✅ Total checks
- ✅ Successful checks
- ✅ Failed checks
- ✅ Uptime percentage
- ✅ Average response time
- ✅ Last 60 response times

### Add Database for Long-term Stats

For historical data, add SQLite:

```python
import sqlite3

# Create database
conn = sqlite3.connect('monitoring.db')
c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS checks
    (timestamp TEXT, status INTEGER, response_time REAL)
''')

# Save each check
def save_check(result):
    c.execute(
        'INSERT INTO checks VALUES (?, ?, ?)',
        (result['timestamp'], result['status_code'], result['response_time'])
    )
    conn.commit()
```

### Generate Daily Reports

Add a scheduled daily summary:

```python
def send_daily_report():
    # Calculate stats for last 24 hours
    uptime_24h = calculate_uptime_24h()
    avg_response = calculate_avg_response_24h()
    incidents = count_incidents_24h()
    
    message = f"""
📊 Daily Report - {datetime.now().strftime('%Y-%m-%d')}

📈 24h Uptime: {uptime_24h}%
⏱ Avg Response: {avg_response}ms
🚨 Incidents: {incidents}
"""
    send_telegram(message)
```

---

## 💰 Cost Breakdown

### DigitalOcean Pricing

| Plan | Price | RAM | CPU | Suitable For |
|------|-------|-----|-----|--------------|
| Basic | **$5/month** | 512MB | 1 vCPU | 1-5 sites |
| Professional | $12/month | 1GB | 1 vCPU | 5-10 sites |

**Included in $5 plan:**
- ✅ 24/7 uptime
- ✅ Automatic SSL
- ✅ Git integration
- ✅ Build/deploy logs
- ✅ Environment variables

### Alternative FREE Options

1. **Run on your own server** - $0 if you have one
2. **Heroku free tier** - Limited hours/month
3. **Raspberry Pi at home** - $35 one-time + electricity
4. **Oracle Cloud free tier** - Limited resources

---

## 📚 Additional Resources

### Documentation
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [DigitalOcean App Platform](https://docs.digitalocean.com/products/app-platform/)
- [Python Requests](https://requests.readthedocs.io/)

### Community
- GitHub Issues - Report bugs or request features
- Telegram Group - Join for support and tips

### Improvements Ideas
- 📊 Add web dashboard with charts
- 📱 Add SMS notifications via Twilio
- 🔔 Add Slack/Discord integration
- 📅 Weekly/monthly summary reports
- 🗄️ PostgreSQL for enterprise stats
- 🔐 SSL certificate expiry monitoring
- 🌍 Multi-region monitoring
- 📈 Response time graphs

---

## 📝 License

MIT License - Feel free to use and modify!

---

## ❓ FAQ

**Q: How accurate is the uptime monitoring?**  
A: Check interval is 60 seconds by default. Downtime shorter than this may not be detected.

**Q: Can I monitor HTTPS sites?**  
A: Yes! The script supports both HTTP and HTTPS.

**Q: What if DigitalOcean goes down?**  
A: Use a different hosting provider or run locally. Consider multi-region monitoring.

**Q: Can I get alerts on my phone?**  
A: Yes! Telegram notifications appear instantly on your phone.

**Q: How do I stop monitoring?**  
A: In DigitalOcean dashboard, go to your app and click "Destroy". Locally, press Ctrl+C.

**Q: Can I monitor APIs instead of websites?**  
A: Yes! Just set `WEBSITE_URL` to your API endpoint.

**Q: How much bandwidth does this use?**  
A: Minimal - approximately 1-2 MB per day for checking every minute.

**Q: Can I check more than just the status code?**  
A: Yes! Modify the script to check response content, headers, etc.

---

## 🎯 Summary

You now have:
- ✅ Simple 150-line Python monitoring script
- ✅ Telegram + Email alerts configured
- ✅ Ready to deploy to DigitalOcean
- ✅ Hourly reports with statistics
- ✅ Complete documentation

**Next steps:**
1. Configure your `.env` file
2. Run `python test.py` to verify setup
3. Test locally with `python monitor.py`
4. Deploy to DigitalOcean
5. Relax knowing your site is monitored 24/7! 😎

---

**Happy Monitoring! 🚀**

If you found this helpful, consider:
- ⭐️ Star the repository
- 🐛 Report bugs
- 💡 Suggest improvements
- 📢 Share with others

---

*Created with ❤️ for simple and effective website monitoring*
