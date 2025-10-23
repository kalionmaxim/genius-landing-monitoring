#!/usr/bin/env python3
"""
Website Monitoring Script with Telegram & Email Alerts
Continuously monitors website uptime and sends notifications
"""

import os
import time
import requests
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration from environment variables
WEBSITE_URL = os.getenv('WEBSITE_URL')
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', 60))
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
EMAIL_FROM = os.getenv('EMAIL_FROM', '')
EMAIL_TO = os.getenv('EMAIL_TO', '')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', '')
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))

# Statistics tracking
stats = {
    'total_checks': 0,
    'successful_checks': 0,
    'failed_checks': 0,
    'response_times': [],  # Last 60 response times for rolling average
    'is_up': None,  # Current state: None (unknown), True (up), False (down)
    'down_since': None,  # Timestamp when site went down
    'last_hourly_report': datetime.now(),
    'checks_this_hour': 0
}


def send_telegram(message):
    """
    Send notification via Telegram bot
    Uses Telegram Bot API directly without external libraries
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return False

    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': message,
            'parse_mode': 'HTML'
        }
        response = requests.post(url, json=payload, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Telegram error: {e}")
        return False


def send_email(subject, body):
    """
    Send notification via email (optional)
    Uses SMTP with TLS for Gmail
    """
    # Skip if email is not configured
    if not EMAIL_FROM or not EMAIL_TO or not EMAIL_PASSWORD:
        return False

    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = EMAIL_FROM
        msg['To'] = EMAIL_TO
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # Send via SMTP
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"❌ Email error: {e}")
        return False


def check_website():
    """
    Check website availability and measure response time
    Returns dict with: is_up, status_code, response_time, error
    """
    try:
        start_time = time.time()
        response = requests.get(WEBSITE_URL, timeout=10)
        response_time = (time.time() - start_time) * 1000  # Convert to milliseconds

        # Consider 2xx and 3xx status codes as "up"
        is_up = response.status_code < 400

        return {
            'is_up': is_up,
            'status_code': response.status_code,
            'response_time': response_time,
            'error': None if is_up else f"HTTP {response.status_code}"
        }
    except requests.exceptions.Timeout:
        return {
            'is_up': False,
            'status_code': 0,
            'response_time': None,
            'error': 'Connection timeout'
        }
    except requests.exceptions.ConnectionError:
        return {
            'is_up': False,
            'status_code': 0,
            'response_time': None,
            'error': 'Connection failed'
        }
    except Exception as e:
        return {
            'is_up': False,
            'status_code': 0,
            'response_time': None,
            'error': str(e)
        }


def calculate_uptime():
    """Calculate uptime percentage from statistics"""
    if stats['total_checks'] == 0:
        return 0.0
    return (stats['successful_checks'] / stats['total_checks']) * 100


def calculate_avg_response_time():
    """Calculate average response time from recent checks"""
    if not stats['response_times']:
        return 0.0
    return sum(stats['response_times']) / len(stats['response_times'])


def send_down_alert(result):
    """Send alert when website goes down"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Telegram message with HTML formatting
    telegram_msg = f"""
🚨 <b>WEBSITE DOWN!</b>

🌐 {WEBSITE_URL}
❌ Status: DOWN
📊 Code: {result['status_code']}
⚠️ Error: {result['error']}
⏰ {timestamp}
"""

    # Email message (plain text)
    email_subject = f"🚨 WEBSITE DOWN: {WEBSITE_URL}"
    email_body = f"""
WEBSITE DOWN ALERT

URL: {WEBSITE_URL}
Status: DOWN
Status Code: {result['status_code']}
Error: {result['error']}
Time: {timestamp}

This is an automated alert from your website monitoring system.
"""

    send_telegram(telegram_msg)
    send_email(email_subject, email_body)
    print(f"🚨 DOWN | {result['error']} | {timestamp}")


def send_recovery_alert(result):
    """Send alert when website comes back online"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Calculate downtime duration
    downtime = 0
    if stats['down_since']:
        downtime = int((datetime.now() - stats['down_since']).total_seconds())

    # Telegram message with HTML formatting
    telegram_msg = f"""
✅ <b>WEBSITE RECOVERED</b>

🌐 {WEBSITE_URL}
✅ Status: UP
📊 Code: {result['status_code']}
⚡️ Response: {result['response_time']:.0f}ms
⏱ Downtime: {downtime}s
⏰ {timestamp}
"""

    # Email message
    email_subject = f"✅ WEBSITE RECOVERED: {WEBSITE_URL}"
    email_body = f"""
WEBSITE RECOVERY ALERT

URL: {WEBSITE_URL}
Status: UP
Status Code: {result['status_code']}
Response Time: {result['response_time']:.0f}ms
Downtime Duration: {downtime} seconds
Time: {timestamp}

Your website is back online!
"""

    send_telegram(telegram_msg)
    send_email(email_subject, email_body)
    print(f"✅ RECOVERED | {result['response_time']:.0f}ms | Downtime: {downtime}s | {timestamp}")


def send_hourly_report():
    """Send hourly status report with statistics"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    uptime = calculate_uptime()
    avg_response = calculate_avg_response_time()

    current_status = "UP" if stats['is_up'] else "DOWN"
    status_emoji = "✅" if stats['is_up'] else "❌"

    # Telegram message
    telegram_msg = f"""
📊 <b>Hourly Report</b>

🌐 Website: {WEBSITE_URL}
{status_emoji} Status: {current_status}
📈 Uptime: {uptime:.2f}%
⏱ Avg Response Time: {avg_response:.0f}ms
🔍 Total Checks: {stats['total_checks']}
❌ Failed: {stats['failed_checks']}

⏰ {timestamp}
"""

    # Email message
    email_subject = f"📊 Hourly Report: {WEBSITE_URL}"
    email_body = f"""
HOURLY STATUS REPORT

Website: {WEBSITE_URL}
Current Status: {current_status}
Uptime: {uptime:.2f}%
Average Response Time: {avg_response:.0f}ms
Total Checks: {stats['total_checks']}
Failed Checks: {stats['failed_checks']}

Time: {timestamp}
"""

    send_telegram(telegram_msg)
    send_email(email_subject, email_body)
    print(f"📊 REPORT | Uptime: {uptime:.2f}% | Avg: {avg_response:.0f}ms | {timestamp}")


def send_startup_notification():
    """Send notification when monitoring starts"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Telegram message
    telegram_msg = f"""
🚀 <b>Monitor Started</b>

🌐 Monitoring: {WEBSITE_URL}
⏱ Check interval: {CHECK_INTERVAL} seconds
📊 Hourly reports: Enabled
⏰ Started at: {timestamp}

Monitoring is now active!
"""

    # Email message
    email_subject = f"🚀 Monitor Started: {WEBSITE_URL}"
    email_body = f"""
MONITORING STARTED

Website: {WEBSITE_URL}
Check Interval: {CHECK_INTERVAL} seconds
Started at: {timestamp}

The monitoring system is now active and will send alerts if the website goes down.
"""

    send_telegram(telegram_msg)
    send_email(email_subject, email_body)
    print(f"📨 Startup notification sent | {timestamp}")


def monitor_loop():
    """
    Main monitoring loop
    Continuously checks website and sends alerts based on state changes
    """
    print(f"🚀 Starting monitor for {WEBSITE_URL}")
    print(f"⏱ Check interval: {CHECK_INTERVAL}s")
    print("=" * 60)

    # Send startup notification
    send_startup_notification()

    while True:
        try:
            # Check website
            result = check_website()
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Update statistics
            stats['total_checks'] += 1
            stats['checks_this_hour'] += 1

            if result['is_up']:
                stats['successful_checks'] += 1
                if result['response_time']:
                    # Keep only last 60 response times for rolling average
                    stats['response_times'].append(result['response_time'])
                    if len(stats['response_times']) > 60:
                        stats['response_times'].pop(0)

                # Check if this is a recovery (was down, now up)
                if stats['is_up'] is False:
                    send_recovery_alert(result)
                    stats['down_since'] = None

                stats['is_up'] = True
                print(f"✅ UP | {result['response_time']:.2f}ms | {timestamp}")
            else:
                stats['failed_checks'] += 1

                # Check if this is a new outage (was up, now down)
                if stats['is_up'] is True or stats['is_up'] is None:
                    send_down_alert(result)
                    stats['down_since'] = datetime.now()

                stats['is_up'] = False

            # Check if it's time for hourly report (every 60 checks, roughly 1 hour with 60s interval)
            hours_passed = (datetime.now() - stats['last_hourly_report']).total_seconds() / 3600
            if hours_passed >= 1.0:
                send_hourly_report()
                stats['last_hourly_report'] = datetime.now()
                stats['checks_this_hour'] = 0

            # Wait before next check
            time.sleep(CHECK_INTERVAL)

        except KeyboardInterrupt:
            print("\n⏹ Monitoring stopped by user")
            break
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            time.sleep(CHECK_INTERVAL)


if __name__ == '__main__':
    # Validate required configuration
    print("🔍 Checking configuration...")

    errors = []
    if not WEBSITE_URL:
        errors.append("WEBSITE_URL not set")
    if not TELEGRAM_BOT_TOKEN:
        errors.append("TELEGRAM_BOT_TOKEN not set")
    if not TELEGRAM_CHAT_ID:
        errors.append("TELEGRAM_CHAT_ID not set")

    if errors:
        print("❌ Configuration errors:")
        for error in errors:
            print(f"   - {error}")
        print("\n💡 Please set these environment variables and try again")
        print("📚 See .env.example for reference")
        exit(1)

    print("✅ Configuration validated")

    # Start monitoring
    try:
        monitor_loop()
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
