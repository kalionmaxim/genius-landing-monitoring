#!/usr/bin/env python3
"""
Configuration Testing Script
Validates environment variables and tests connectivity before deployment
"""

import os
import sys
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
WEBSITE_URL = os.getenv('WEBSITE_URL')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
EMAIL_FROM = os.getenv('EMAIL_FROM', '')
EMAIL_TO = os.getenv('EMAIL_TO', '')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', '')
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))


def test_required_variables():
    """Check if required environment variables are set"""
    print("📋 Required Variables:")

    errors = []

    if WEBSITE_URL:
        print(f"  ✅ WEBSITE_URL: {WEBSITE_URL}")
    else:
        print("  ❌ WEBSITE_URL: Not set")
        errors.append("WEBSITE_URL is required")

    if TELEGRAM_BOT_TOKEN:
        # Show only first 10 chars for security
        print(f"  ✅ TELEGRAM_BOT_TOKEN: {TELEGRAM_BOT_TOKEN[:10]}...")
    else:
        print("  ❌ TELEGRAM_BOT_TOKEN: Not set")
        errors.append("TELEGRAM_BOT_TOKEN is required")

    if TELEGRAM_CHAT_ID:
        print(f"  ✅ TELEGRAM_CHAT_ID: {TELEGRAM_CHAT_ID}")
    else:
        print("  ❌ TELEGRAM_CHAT_ID: Not set")
        errors.append("TELEGRAM_CHAT_ID is required")

    print()
    return errors


def test_website():
    """Test website connectivity"""
    print("🌐 Testing Website...")

    if not WEBSITE_URL:
        print("  ❌ Cannot test: WEBSITE_URL not set")
        print()
        return False

    try:
        response = requests.get(WEBSITE_URL, timeout=10)
        status_code = response.status_code
        response_time = response.elapsed.total_seconds() * 1000  # Convert to ms

        print(f"  ✅ Status: {status_code}")
        print(f"  ⚡️ Time: {response_time:.2f}ms")

        if status_code < 400:
            print(f"  ✅ Website is UP")
        else:
            print(f"  ⚠️ Website returned status code {status_code}")

        print()
        return True
    except requests.exceptions.Timeout:
        print("  ❌ Connection timeout (>10s)")
        print()
        return False
    except requests.exceptions.ConnectionError:
        print("  ❌ Connection failed - check URL")
        print()
        return False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        print()
        return False


def test_telegram():
    """Test Telegram bot connection"""
    print("📱 Testing Telegram...")

    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("  ⚠️ Telegram not configured (optional)")
        print()
        return True  # Not an error, it's optional

    try:
        # Test bot token - get bot info
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getMe"
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            print(f"  ❌ Invalid bot token (status: {response.status_code})")
            print()
            return False

        bot_info = response.json()
        if not bot_info.get('ok'):
            print(f"  ❌ Bot token error: {bot_info.get('description', 'Unknown error')}")
            print()
            return False

        bot_username = bot_info['result'].get('username', 'Unknown')
        print(f"  ✅ Bot connected: @{bot_username}")

        # Send test message
        test_message = "🧪 Test message from monitoring setup"
        send_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': test_message
        }
        send_response = requests.post(send_url, json=payload, timeout=10)

        if send_response.status_code == 200:
            print(f"  ✅ Test message sent to chat {TELEGRAM_CHAT_ID}")
            print()
            return True
        else:
            error_data = send_response.json()
            error_msg = error_data.get('description', 'Unknown error')
            print(f"  ❌ Failed to send message: {error_msg}")
            if 'chat not found' in error_msg.lower():
                print("  💡 Tip: Send /start to your bot first!")
            print()
            return False

    except requests.exceptions.Timeout:
        print("  ❌ Telegram API timeout")
        print()
        return False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        print()
        return False


def test_email():
    """Test email configuration"""
    print("📧 Testing Email...")

    # Email is optional
    if not EMAIL_FROM or not EMAIL_TO or not EMAIL_PASSWORD:
        print("  ⚠️ Email not configured (optional)")
        print()
        return True

    try:
        import smtplib
        from email.mime.text import MIMEText

        # Create test message
        msg = MIMEText("Test email from website monitoring setup")
        msg['Subject'] = "🧪 Test Email"
        msg['From'] = EMAIL_FROM
        msg['To'] = EMAIL_TO

        # Try to connect and send
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10)
        server.starttls()
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()

        print(f"  ✅ Test email sent successfully")
        print(f"  📬 From: {EMAIL_FROM}")
        print(f"  📭 To: {EMAIL_TO}")
        print()
        return True

    except smtplib.SMTPAuthenticationError:
        print("  ❌ Authentication failed")
        print("  💡 Tip: Use Gmail App Password, not regular password")
        print("  💡 Create at: https://myaccount.google.com/apppasswords")
        print()
        return False
    except smtplib.SMTPException as e:
        print(f"  ❌ SMTP error: {e}")
        print()
        return False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        print()
        return False


def main():
    """Run all tests"""
    print("🧪 Testing Configuration...")
    print("=" * 60)
    print()

    # Track test results
    all_passed = True

    # Test required variables
    errors = test_required_variables()
    if errors:
        all_passed = False
        print("❌ Configuration errors found:")
        for error in errors:
            print(f"  - {error}")
        print()
        print("💡 Check your .env file and make sure all required variables are set")
        print()
        sys.exit(1)

    # Test website
    if not test_website():
        all_passed = False

    # Test Telegram
    if not test_telegram():
        all_passed = False

    # Test email
    if not test_email():
        all_passed = False

    # Summary
    print("=" * 60)
    if all_passed:
        print("✅ Configuration test complete!")
        print()
        print("🚀 You can now run the monitor:")
        print("   python monitor.py")
        print()
    else:
        print("⚠️ Some tests failed. Please fix the issues above.")
        print()
        sys.exit(1)


if __name__ == '__main__':
    main()
