#!/usr/bin/env python3
"""
Test script to send all types of monitoring messages
This helps verify that all alert formats work correctly
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

WEBSITE_URL = os.getenv('WEBSITE_URL')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')


def send_telegram(message):
    """Send notification via Telegram bot"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ Telegram not configured")
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


def test_down_alert():
    """Test DOWN alert message"""
    print("\n1️⃣ Testing DOWN Alert Message...")

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    message = f"""
🚨 <b>WEBSITE DOWN!</b>

🌐 {WEBSITE_URL}
❌ Status: DOWN
📊 Code: 0
⚠️ Error: Connection timeout
⏰ {timestamp}

<i>This is a test message</i>
"""

    if send_telegram(message):
        print("✅ DOWN alert sent successfully!")
        return True
    else:
        print("❌ Failed to send DOWN alert")
        return False


def test_recovery_alert():
    """Test RECOVERY alert message"""
    print("\n2️⃣ Testing RECOVERY Alert Message...")

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    message = f"""
✅ <b>WEBSITE RECOVERED</b>

🌐 {WEBSITE_URL}
✅ Status: UP
📊 Code: 200
⚡️ Response: 234ms
⏱ Downtime: 125s
⏰ {timestamp}

<i>This is a test message</i>
"""

    if send_telegram(message):
        print("✅ RECOVERY alert sent successfully!")
        return True
    else:
        print("❌ Failed to send RECOVERY alert")
        return False


def test_hourly_report():
    """Test HOURLY REPORT message"""
    print("\n3️⃣ Testing HOURLY Report Message...")

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    message = f"""
📊 <b>Hourly Report</b>

🌐 Website: {WEBSITE_URL}
✅ Status: UP
📈 Uptime: 98.33%
⏱ Avg Response Time: 245ms
🔍 Total Checks: 60
❌ Failed: 1

⏰ {timestamp}

<i>This is a test message</i>
"""

    if send_telegram(message):
        print("✅ HOURLY report sent successfully!")
        return True
    else:
        print("❌ Failed to send HOURLY report")
        return False


def test_startup_message():
    """Test startup notification"""
    print("\n4️⃣ Testing STARTUP Message...")

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    message = f"""
🚀 <b>Monitor Started</b>

🌐 Monitoring: {WEBSITE_URL}
⏱ Check interval: 60 seconds
🤖 Bot: @genius_landing_monitoring_bot
⏰ Started at: {timestamp}

<i>Monitoring is now active!</i>
"""

    if send_telegram(message):
        print("✅ STARTUP message sent successfully!")
        return True
    else:
        print("❌ Failed to send STARTUP message")
        return False


def main():
    """Run all message tests"""
    print("🧪 Testing All Message Types")
    print("=" * 60)

    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ Telegram not configured in .env file")
        sys.exit(1)

    print(f"📱 Sending test messages to chat: {TELEGRAM_CHAT_ID}")
    print("⏳ Please wait 2 seconds between messages to avoid rate limiting...")

    results = []

    # Test all message types with delays
    import time

    results.append(test_down_alert())
    time.sleep(2)

    results.append(test_recovery_alert())
    time.sleep(2)

    results.append(test_hourly_report())
    time.sleep(2)

    results.append(test_startup_message())

    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    print(f"   ✅ Successful: {sum(results)}/4")
    print(f"   ❌ Failed: {4 - sum(results)}/4")

    if all(results):
        print("\n✅ All message types sent successfully!")
        print("📱 Check your Telegram to see the messages")
    else:
        print("\n⚠️ Some messages failed to send")
        sys.exit(1)


if __name__ == '__main__':
    main()
