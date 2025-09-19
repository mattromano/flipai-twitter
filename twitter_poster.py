#!/usr/bin/env python3
"""
Twitter posting system for Flipside AI automation.
Integrates with the current workflow to post analysis results to Twitter.
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  python-dotenv not installed. Install with: pip install python-dotenv")

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    import tweepy
    TWEEPY_AVAILABLE = True
except ImportError:
    TWEEPY_AVAILABLE = False
    print("⚠️  tweepy not installed. Install with: pip install tweepy")

from src.twitter_generator import TwitterGenerator
from src.tweet_formatter import TweetFormatter


class TwitterPoster:
    """Handles Twitter posting with API integration."""
    
    def __init__(self):
        """Initialize the Twitter poster."""
        self.logger = logging.getLogger(__name__)
        self.twitter_generator = TwitterGenerator()
        self.client = None
        self.api = None
        
        # Load Twitter API credentials
        self.load_credentials()
    
    def load_credentials(self):
        """Load Twitter API credentials from environment variables."""
        self.credentials = {
            'bearer_token': os.getenv('TWITTER_BEARER_TOKEN'),
            'consumer_key': os.getenv('TWITTER_CONSUMER_KEY'),
            'consumer_secret': os.getenv('TWITTER_CONSUMER_SECRET'),
            'access_token': os.getenv('TWITTER_ACCESS_TOKEN'),
            'access_token_secret': os.getenv('TWITTER_ACCESS_TOKEN_SECRET'),
        }
        
        # Check if credentials are available
        if all(self.credentials.values()):
            self.credentials_available = True
            self.logger.info("Twitter API credentials loaded successfully")
        else:
            self.credentials_available = False
            missing = [k for k, v in self.credentials.items() if not v]
            self.logger.warning(f"Missing Twitter credentials: {missing}")
    
    def setup_twitter_client(self) -> bool:
        """Setup Twitter API client."""
        if not TWEEPY_AVAILABLE:
            self.logger.error("tweepy not available. Install with: pip install tweepy")
            return False
        
        if not self.credentials_available:
            self.logger.error("Twitter credentials not available")
            return False
        
        try:
            # Setup v2 client for posting
            self.client = tweepy.Client(
                bearer_token=self.credentials['bearer_token'],
                consumer_key=self.credentials['consumer_key'],
                consumer_secret=self.credentials['consumer_secret'],
                access_token=self.credentials['access_token'],
                access_token_secret=self.credentials['access_token_secret'],
                wait_on_rate_limit=True
            )
            
            # Setup v1.1 API for media upload
            auth = tweepy.OAuth1UserHandler(
                self.credentials['consumer_key'],
                self.credentials['consumer_secret'],
                self.credentials['access_token'],
                self.credentials['access_token_secret']
            )
            self.api = tweepy.API(auth, wait_on_rate_limit=True)
            
            self.logger.info("Twitter API client setup successful")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to setup Twitter client: {e}")
            return False
    
    def post_tweet(self, text: str, image_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Post a tweet with optional image.
        
        Args:
            text: Tweet text content
            image_path: Path to image file (optional)
            
        Returns:
            Dictionary with posting results
        """
        if not self.client:
            if not self.setup_twitter_client():
                return {
                    "success": False,
                    "error": "Failed to setup Twitter client",
                    "tweet_id": None
                }
        
        try:
            media_ids = []
            
            # Upload image if provided
            if image_path and os.path.exists(image_path):
                try:
                    media = self.api.media_upload(image_path)
                    media_ids.append(media.media_id)
                    self.logger.info(f"Image uploaded successfully: {image_path}")
                except Exception as e:
                    self.logger.warning(f"Failed to upload image: {e}")
                    # Continue without image
            
            # Post the tweet
            response = self.client.create_tweet(
                text=text,
                media_ids=media_ids if media_ids else None
            )
            
            tweet_id = response.data['id']
            self.logger.info(f"Tweet posted successfully: {tweet_id}")
            
            return {
                "success": True,
                "tweet_id": tweet_id,
                "text": text,
                "image_path": image_path,
                "media_ids": media_ids
            }
            
        except Exception as e:
            self.logger.error(f"Failed to post tweet: {e}")
            return {
                "success": False,
                "error": str(e),
                "tweet_id": None
            }
    
    def post_from_analysis(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Post a tweet generated from analysis data.
        
        Args:
            analysis_data: Analysis results from automation
            
        Returns:
            Dictionary with posting results
        """
        try:
            # Generate tweet content
            tweet_data = self.twitter_generator.generate_tweet_from_analysis(analysis_data)
            
            if not tweet_data.get("success", False):
                return {
                    "success": False,
                    "error": "Failed to generate tweet content",
                    "tweet_data": tweet_data
                }
            
            # Add chat URL to tweet if available
            tweet_content = tweet_data["content"]
            chat_url = analysis_data.get("data", {}).get("chat_url", "")
            
            if chat_url and "Here's the chat link if you want to dive deeper" in tweet_content:
                # Convert to shared format if it's a regular chat URL
                if "/chat/" in chat_url and "/shared/chats/" not in chat_url:
                    # Extract the chat ID and convert to shared format
                    chat_id = chat_url.split("/chat/")[-1]
                    shared_url = f"https://flipsidecrypto.xyz/chat/shared/chats/{chat_id}"
                else:
                    shared_url = chat_url
                
                # Append the URL to the tweet
                tweet_content += f"\n\n{shared_url}"
            
            # Post the tweet
            result = self.post_tweet(
                text=tweet_content,
                image_path=tweet_data.get("image")
            )
            
            # Add tweet generation data to result
            result["tweet_data"] = tweet_data
            result["tweet_data"]["content"] = tweet_content  # Update with final content including URL
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to post from analysis: {e}")
            return {
                "success": False,
                "error": str(e),
                "tweet_data": None
            }
    
    def post_from_latest_analysis(self) -> Dict[str, Any]:
        """
        Post a tweet from the latest analysis results.
        
        Returns:
            Dictionary with posting results
        """
        try:
            # Find the latest analysis file
            logs_dir = Path("logs")
            if not logs_dir.exists():
                return {
                    "success": False,
                    "error": "No logs directory found"
                }
            
            analysis_files = list(logs_dir.glob("analysis_*.json"))
            if not analysis_files:
                return {
                    "success": False,
                    "error": "No analysis files found"
                }
            
            # Get the most recent analysis file
            latest_analysis_file = max(analysis_files, key=os.path.getctime)
            
            # Load analysis data
            with open(latest_analysis_file, 'r', encoding='utf-8') as f:
                analysis_data = json.load(f)
            
            self.logger.info(f"Loaded analysis from: {latest_analysis_file}")
            
            # Post the tweet
            return self.post_from_analysis(analysis_data)
            
        except Exception as e:
            self.logger.error(f"Failed to post from latest analysis: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def preview_tweet(self, analysis_data: Dict[str, Any]) -> str:
        """
        Generate a preview of the tweet without posting.
        
        Args:
            analysis_data: Analysis results from automation
            
        Returns:
            Formatted preview string
        """
        try:
            tweet_data = self.twitter_generator.generate_tweet_from_analysis(analysis_data)
            return self.twitter_generator.format_tweet_for_display(tweet_data)
        except Exception as e:
            return f"❌ Failed to generate preview: {e}"


def main():
    """Main function for testing Twitter posting."""
    print("🐦 Twitter Poster for Flipside AI")
    print("=" * 50)
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize poster
    poster = TwitterPoster()
    
    if not poster.credentials_available:
        print("❌ Twitter credentials not configured")
        print("\n📋 To set up Twitter API credentials:")
        print("1. Go to https://developer.twitter.com/")
        print("2. Create a new app and get your API keys")
        print("3. Set the following environment variables:")
        print("   - TWITTER_BEARER_TOKEN")
        print("   - TWITTER_CONSUMER_KEY")
        print("   - TWITTER_CONSUMER_SECRET")
        print("   - TWITTER_ACCESS_TOKEN")
        print("   - TWITTER_ACCESS_TOKEN_SECRET")
        return
    
    if not TWEEPY_AVAILABLE:
        print("❌ tweepy not installed")
        print("Install with: pip install tweepy")
        return
    
    # Test with latest analysis
    print("🔍 Looking for latest analysis...")
    result = poster.post_from_latest_analysis()
    
    if result["success"]:
        print("✅ Tweet posted successfully!")
        print(f"📱 Tweet ID: {result['tweet_id']}")
        print(f"📝 Text: {result['tweet_data']['content'][:100]}...")
        if result['tweet_data'].get('image'):
            print(f"🖼️  Image: {result['tweet_data']['image']}")
    else:
        print("❌ Failed to post tweet")
        print(f"🚨 Error: {result['error']}")


if __name__ == "__main__":
    main()