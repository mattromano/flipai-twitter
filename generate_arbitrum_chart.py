#!/usr/bin/env python3
"""
Generate chart image from HTML and post to Twitter with chat link.
"""

import os
import sys
import json
import tempfile
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    import tweepy
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
except ImportError as e:
    print(f"❌ Missing dependency: {e}")
    sys.exit(1)

def extract_html_chart(analysis_data):
    """Extract HTML chart from analysis data."""
    response_text = analysis_data['data']['response_text']
    
    # Find the HTML_CHART section
    if 'HTML_CHART:' in response_text:
        html_start = response_text.find('HTML_CHART:') + len('HTML_CHART:')
        html_end = response_text.find('\nThe data reveals', html_start)
        if html_end == -1:
            html_end = response_text.find('\nNext steps', html_start)
        if html_end == -1:
            html_end = len(response_text)
        
        html_content = response_text[html_start:html_end].strip()
        if html_content.startswith('html'):
            html_content = html_content[4:].strip()
        
        return html_content
    
    return None

def html_to_png(html_content, output_path, chat_url):
    """Convert HTML chart to PNG image."""
    # Add chat URL to the HTML
    modified_html = html_content.replace(
        '<body>',
        f'''<body>
    <div style="position: absolute; bottom: 10px; right: 10px; background: rgba(255,255,255,0.9); padding: 8px; border-radius: 4px; font-size: 12px; color: #333;">
        <a href="{chat_url}" style="color: #1da1f2; text-decoration: none;">🔗 View Full Analysis</a>
    </div>'''
    )
    
    # Setup Chrome in headless mode
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1200,700')
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Create temporary HTML file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            f.write(modified_html)
            temp_html_path = f.name
        
        # Load the HTML file
        driver.get(f'file://{temp_html_path}')
        
        # Wait for chart to load
        import time
        time.sleep(3)
        
        # Take screenshot
        driver.save_screenshot(output_path)
        
        # Clean up
        os.unlink(temp_html_path)
        
        return True
        
    except Exception as e:
        print(f"❌ Error converting HTML to PNG: {e}")
        return False
    finally:
        driver.quit()

def post_tweet_with_image(tweet_text, image_path, chat_url):
    """Post tweet with image."""
    # Get credentials
    bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
    consumer_key = os.getenv('TWITTER_CONSUMER_KEY')
    consumer_secret = os.getenv('TWITTER_CONSUMER_SECRET')
    access_token = os.getenv('TWITTER_ACCESS_TOKEN')
    access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
    
    try:
        # Setup v1.1 API for media upload
        auth = tweepy.OAuth1UserHandler(
            consumer_key, consumer_secret, access_token, access_token_secret
        )
        api = tweepy.API(auth)
        
        # Setup v2 client for posting
        client = tweepy.Client(
            bearer_token=bearer_token,
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            access_token=access_token,
            access_token_secret=access_token_secret,
            wait_on_rate_limit=True
        )
        
        # Upload media
        print("📤 Uploading image...")
        media = api.media_upload(image_path)
        print(f"✅ Image uploaded: {media.media_id}")
        
        # Create tweet with media (shorter version, URL will be in image)
        tweet_content = tweet_text
        
        print(f"📝 Posting tweet with image...")
        print(f"Content: {tweet_content}")
        print(f"Length: {len(tweet_content)} characters")
        
        response = client.create_tweet(
            text=tweet_content,
            media_ids=[media.media_id]
        )
        
        if response.data:
            print(f"✅ Tweet posted successfully!")
            print(f"📱 Tweet ID: {response.data['id']}")
            print(f"🔗 Tweet URL: https://twitter.com/AgentFlipp61663/status/{response.data['id']}")
            return True
        else:
            print("❌ No response data")
            return False
            
    except Exception as e:
        print(f"❌ Error posting tweet: {e}")
        return False

def main():
    """Main function."""
    print("🎨 Generating Arbitrum Chart & Posting to Twitter")
    print("=" * 60)
    
    # Load analysis data
    with open('logs/analysis_20250919_091453.json', 'r') as f:
        analysis_data = json.load(f)
    
    # Extract data
    twitter_text = analysis_data['data']['twitter_text']
    chat_url = analysis_data['data']['chat_url']
    
    print(f"📝 Twitter text: {twitter_text}")
    print(f"🔗 Chat URL: {chat_url}")
    
    # Extract HTML chart
    html_chart = extract_html_chart(analysis_data)
    if not html_chart:
        print("❌ No HTML chart found in analysis data")
        return False
    
    print("✅ HTML chart extracted")
    
    # Convert to PNG
    chart_path = "charts/arbitrum_analysis_20250919.png"
    os.makedirs("charts", exist_ok=True)
    
    print("🎨 Converting HTML chart to PNG...")
    if not html_to_png(html_chart, chart_path, chat_url):
        print("❌ Failed to convert HTML to PNG")
        return False
    
    print(f"✅ Chart saved to: {chart_path}")
    
    # Post to Twitter
    tweet_text = f"🔍 Fresh crypto analysis from FlipsideAI:\n\n{twitter_text}"
    
    if post_tweet_with_image(tweet_text, chart_path, chat_url):
        print("🎉 Successfully posted chart to Twitter!")
        return True
    else:
        print("❌ Failed to post to Twitter")
        return False

if __name__ == "__main__":
    main()
