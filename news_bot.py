import os
import requests
import feedparser
from datetime import datetime, timedelta, timezone

# --- Configuration ---
# This dictionary is now populated with all the specified RSS feeds.
RSS_FEEDS = {
    # First Batch
    "Bridge.xyz (Stripe)": "https://news.google.com/rss/search?q=%22Stripe%20Bridge%22%20OR%20%22Bridge.xyz%22%20OR%20(%22Bridge%22%2B%22Stripe%22)&hl=en-US&gl=US&ceid=US:en",
    "BVNK": "https://news.google.com/rss/search?q=%22BVNK%22&hl=en-US&gl=US&ceid=US:en",
    "Merge Money": "https://news.google.com/rss/search?q=%22Merge%20Money%22%20OR%20(%22Merge.dev%22%2B%22payments%22)%20OR%20(%22Merge%22%2B%22payments%20API%22)&hl=en-US&gl=US&ceid=US:en",
    "Rail.io": "https://news.google.com/rss/search?q=%22Rail.io%22%20OR%20(%22Rail%22%2B%22DeFi%22)%20OR%20%22Layer2Financial%22&hl=en-US&gl=US&ceid=US:en",
    "IRON (Moonpay)": "https://news.google.com/rss/search?q=(%22Moonpay%22%2B%22IRON%22)%20OR%20%22IRON%20Stablecoin%22&hl=en-US&gl=US&ceid=US:en",
    "Tazapay": "https://news.google.com/rss/search?q=%22Tazapay%22&hl=en-US&gl=US&ceid=US:en",
    # Second Batch
    "Airwallex": "https://news.google.com/rss/search?q=%22Airwallex%22&hl=en-US&gl=US&ceid=US:en",
    "Terrapay": "https://news.google.com/rss/search?q=%22Terrapay%22&hl=en-US&gl=US&ceid=US:en",
    "Rapyd": "https://news.google.com/rss/search?q=%22Rapyd%22&hl=en-US&gl=US&ceid=US:en",
    "Thunes": "https://news.google.com/rss/search?q=%22Thunes%22&hl=en-US&gl=US&ceid=US:en",
    "Lightnet": "https://news.google.com/rss/search?q=(%22Lightnet%22%2B%22fintech%22)%20OR%20(%22Lightnet%22%2B%22blockchain%22)&hl=en-US&gl=US&ceid=US:en",
    "Revolut": "https://news.google.com/rss/search?q=%22Revolut%22&hl=en-US&gl=US&ceid=US:en",
    "Wise (TransferWise)": "https://news.google.com/rss/search?q=(%22Wise%22%2B%22money%20transfer%22)%20OR%20(%22Wise%22%2B%22payments%22)%20OR%20%22TransferWise%22&hl=en-US&gl=US&ceid=US:en",
}

# The Slack Webhook URL is retrieved from GitHub Secrets
SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL")

# --- Main Script ---
def fetch_and_send_news():
    """Fetches news from the last 24 hours and sends it to Slack."""
    if not SLACK_WEBHOOK_URL:
        print("Error: SLACK_WEBHOOK_URL not set.")
        return

    # Set the time window for "new" articles
    twenty_four_hours_ago = datetime.now(timezone.utc) - timedelta(hours=24)
    
    all_news_items = []
    
    print("Fetching news...")
    for source_name, feed_url in RSS_FEEDS.items():
        feed = feedparser.parse(feed_url)
        news_for_source = []
        for entry in feed.entries:
            # Parse publication date and make it timezone-aware
            published_time = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
            if published_time >= twenty_four_hours_ago:
                news_for_source.append(f"• <{entry.link}|{entry.title}>")
        
        if news_for_source:
            all_news_items.append(f"*{source_name}*\n" + "\n".join(news_for_source))

    # --- Prepare the Slack Message ---
    if not all_news_items:
        message_text = ":zzz: No significant news found for your keywords in the last 24 hours."
        print("No new articles found.")
    else:
        today_str = datetime.now().strftime("%B %d, %Y")
        message_text = f":newspaper: *Hourly News Digest - {today_str}*\n\n" + "\n\n".join(all_news_items)
        print(f"Found {len(all_news_items)} sources with news.")

    # --- Send to Slack ---
    try:
        response = requests.post(
            SLACK_WEBHOOK_URL,
            json={"text": message_text},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        response.raise_for_status()  # Raises an exception for bad responses (4xx or 5xx)
        print("Message posted to Slack successfully.")
    except requests.exceptions.RequestException as e:
        print(f"Error posting to Slack: {e}")

if __name__ == "__main__":
    fetch_and_send_news()
