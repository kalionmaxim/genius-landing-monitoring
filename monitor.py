#!/usr/bin/env python3
"""
Website Monitoring Script with Telegram & Email Alerts
Continuously monitors website uptime and sends notifications
"""

import os
import time
import requests
import smtplib
import threading
import pytz
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from http.server import HTTPServer, BaseHTTPRequestHandler

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

# Timezone configuration (default: Europe/Kyiv for Ukraine)
TIMEZONE = os.getenv('TZ', 'Europe/Kyiv')
try:
    LOCAL_TZ = pytz.timezone(TIMEZONE)
except pytz.exceptions.UnknownTimeZoneError:
    print(f"⚠️ Warning: Unknown timezone '{TIMEZONE}', using UTC")
    LOCAL_TZ = pytz.UTC

# Content validation settings
MIN_CONTENT_LENGTH = int(os.getenv('MIN_CONTENT_LENGTH', 1000))  # Minimum bytes expected in response
REQUIRED_CONTENT = os.getenv('REQUIRED_CONTENT', '')  # Optional: specific text that must be present

# Report interval in minutes (default: 10 minutes)
REPORT_INTERVAL_MINUTES = int(os.getenv('REPORT_INTERVAL_MINUTES', 10))

# Statistics tracking
stats = {
    'total_checks': 0,
    'successful_checks': 0,
    'failed_checks': 0,
    'response_times': [],  # Last 60 response times for rolling average
    'is_up': None,  # Current state: None (unknown), True (up), False (down)
    'down_since': None,  # Timestamp when site went down
    'last_report_minute': -1,  # Track last report minute to avoid duplicates
    'checks_this_interval': 0,
    'last_check_result': None,  # Store latest check result for reports
}


def get_local_time():
    """Get current time in configured timezone"""
    return datetime.now(LOCAL_TZ)


def format_timestamp(dt=None):
    """Format timestamp in local timezone"""
    if dt is None:
        dt = get_local_time()
    return dt.strftime('%Y-%m-%d %H:%M:%S %Z')


def should_send_report():
    """
    Check if it's time to send a report based on clock time
    Reports are sent at fixed intervals (e.g., :00, :10, :20, :30, etc.)
    This ensures reports align with the clock, not restart time
    """
    now = get_local_time()
    current_minute = now.minute

    # Check if current minute is a report interval (0, 10, 20, 30, 40, 50)
    is_report_time = (current_minute % REPORT_INTERVAL_MINUTES) == 0

    # Only send if it's report time AND we haven't sent for this minute yet
    if is_report_time and stats['last_report_minute'] != current_minute:
        stats['last_report_minute'] = current_minute
        return True

    return False


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
    Validates that we receive full HTML content, not just a status code
    Returns dict with: is_up, status_code, response_time, error, content_length
    """
    try:
        start_time = time.time()
        response = requests.get(WEBSITE_URL, timeout=10)
        response_time = (time.time() - start_time) * 1000  # Convert to milliseconds

        # Get content length
        content_length = len(response.content)

        # Check 1: HTTP status code must be < 400
        if response.status_code >= 400:
            return {
                'is_up': False,
                'status_code': response.status_code,
                'response_time': response_time,
                'content_length': content_length,
                'error': f"HTTP {response.status_code}"
            }

        # Check 2: Content length must meet minimum requirement
        if content_length < MIN_CONTENT_LENGTH:
            return {
                'is_up': False,
                'status_code': response.status_code,
                'response_time': response_time,
                'content_length': content_length,
                'error': f"Content too short ({content_length} bytes, expected >{MIN_CONTENT_LENGTH})"
            }

        # Check 3: Optional - specific content must be present
        if REQUIRED_CONTENT and REQUIRED_CONTENT not in response.text:
            return {
                'is_up': False,
                'status_code': response.status_code,
                'response_time': response_time,
                'content_length': content_length,
                'error': f"Required content '{REQUIRED_CONTENT}' not found"
            }

        # All checks passed
        return {
            'is_up': True,
            'status_code': response.status_code,
            'response_time': response_time,
            'content_length': content_length,
            'error': None
        }
    except requests.exceptions.Timeout:
        return {
            'is_up': False,
            'status_code': 0,
            'response_time': None,
            'content_length': 0,
            'error': 'Connection timeout'
        }
    except requests.exceptions.ConnectionError:
        return {
            'is_up': False,
            'status_code': 0,
            'response_time': None,
            'content_length': 0,
            'error': 'Connection failed'
        }
    except Exception as e:
        return {
            'is_up': False,
            'status_code': 0,
            'response_time': None,
            'content_length': 0,
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
    timestamp = format_timestamp()

    # Include content length in alert if available
    content_info = f"\n📏 Content: {result['content_length']} bytes" if result.get('content_length', 0) > 0 else ""

    # Telegram message with HTML formatting
    telegram_msg = f"""
🚨 <b>WEBSITE DOWN!</b>

🌐 {WEBSITE_URL}
❌ Status: DOWN
📊 Code: {result['status_code']}
⚠️ Error: {result['error']}{content_info}
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
Content Length: {result.get('content_length', 0)} bytes
Time: {timestamp}

This is an automated alert from your website monitoring system.
"""

    send_telegram(telegram_msg)
    send_email(email_subject, email_body)
    print(f"🚨 DOWN | {result['error']} | {result.get('content_length', 0)}B | {timestamp}")


def send_recovery_alert(result):
    """Send alert when website comes back online"""
    timestamp = format_timestamp()

    # Calculate downtime duration
    downtime = 0
    if stats['down_since']:
        downtime = int((get_local_time() - stats['down_since']).total_seconds())

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
    """Send periodic status report with statistics"""
    timestamp = format_timestamp()
    uptime = calculate_uptime()
    avg_response = calculate_avg_response_time()

    current_status = "UP" if stats['is_up'] else "DOWN"
    status_emoji = "✅" if stats['is_up'] else "❌"

    # Get latest check information
    last_check = stats.get('last_check_result', {})
    status_code = last_check.get('status_code', 0)
    content_length = last_check.get('content_length', 0)
    content_kb = content_length / 1024 if content_length > 0 else 0

    # Build HTTP status info
    http_info = f"\n📄 HTTP: {status_code}"
    if content_length > 0:
        http_info += f" | {content_kb:.1f}KB"

    # Telegram message
    telegram_msg = f"""
📊 <b>Status Report</b>

🌐 Website: {WEBSITE_URL}
{status_emoji} Status: {current_status}{http_info}
📈 Uptime: {uptime:.2f}%
⏱ Avg Response Time: {avg_response:.0f}ms

📋 Checks this interval: {stats['checks_this_interval']}
🔍 Total Checks: {stats['total_checks']}
❌ Failed: {stats['failed_checks']}

⏰ {timestamp}
"""

    # Email message
    email_subject = f"📊 Status Report: {WEBSITE_URL}"
    email_body = f"""
STATUS REPORT

Website: {WEBSITE_URL}
Current Status: {current_status}
HTTP Status: {status_code}
Content Size: {content_kb:.1f}KB

Uptime: {uptime:.2f}%
Average Response Time: {avg_response:.0f}ms

Checks This Interval: {stats['checks_this_interval']}
Total Checks: {stats['total_checks']}
Failed Checks: {stats['failed_checks']}

Time: {timestamp}
"""

    send_telegram(telegram_msg)
    send_email(email_subject, email_body)
    print(f"📊 REPORT | Uptime: {uptime:.2f}% | Avg: {avg_response:.0f}ms | {timestamp}")


def send_startup_notification():
    """Send notification when monitoring starts"""
    timestamp = format_timestamp()

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
            timestamp = format_timestamp()

            # Update statistics
            stats['total_checks'] += 1
            stats['checks_this_interval'] += 1
            stats['last_check_result'] = result  # Store for reports

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
                content_size = result.get('content_length', 0) / 1024  # Convert to KB
                print(f"✅ UP | {result['response_time']:.2f}ms | {content_size:.1f}KB | {timestamp}")
            else:
                stats['failed_checks'] += 1

                # Check if this is a new outage (was up, now down)
                if stats['is_up'] is True or stats['is_up'] is None:
                    send_down_alert(result)
                    stats['down_since'] = get_local_time()

                stats['is_up'] = False

            # Check if it's time for periodic report (based on clock time, not restart time)
            if should_send_report():
                send_hourly_report()
                stats['checks_this_interval'] = 0

            # Wait before next check
            time.sleep(CHECK_INTERVAL)

        except KeyboardInterrupt:
            print("\n⏹ Monitoring stopped by user")
            break
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            time.sleep(CHECK_INTERVAL)


class HealthCheckHandler(BaseHTTPRequestHandler):
    """
    Simple HTTP handler for health checks
    Responds to DigitalOcean health check pings
    """

    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/' or self.path == '/health':
            # Respond with 200 OK and status information
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            uptime = calculate_uptime()
            status = "UP" if stats['is_up'] else "DOWN" if stats['is_up'] is not None else "STARTING"

            response = f"""
            <html>
            <head><title>Website Monitor Status</title></head>
            <body>
                <h1>Website Monitor - Running</h1>
                <p><strong>Monitoring:</strong> {WEBSITE_URL}</p>
                <p><strong>Current Status:</strong> {status}</p>
                <p><strong>Uptime:</strong> {uptime:.2f}%</p>
                <p><strong>Total Checks:</strong> {stats['total_checks']}</p>
                <p><strong>Check Interval:</strong> {CHECK_INTERVAL}s</p>
            </body>
            </html>
            """
            self.wfile.write(response.encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        """Suppress health check logs to avoid clutter"""
        pass


def start_health_server():
    """Start HTTP server for health checks on port 8080"""
    port = int(os.getenv('PORT', 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    print(f"🏥 Health check server started on port {port}")
    server.serve_forever()


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

    # Start health check server in background thread
    health_thread = threading.Thread(target=start_health_server, daemon=True)
    health_thread.start()

    # Start monitoring (runs in main thread)
    try:
        monitor_loop()
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
