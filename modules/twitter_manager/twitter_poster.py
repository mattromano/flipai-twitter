"""
Twitter Poster

Handles posting tweets to Twitter API.
"""

import os
import json
from typing import Dict, Any, Optional
from datetime import datetime

import tweepy
from tweepy import OAuth1UserHandler, Client

from modules.shared.logger import AutomationLogger


class TwitterPoster:
    """Handles Twitter API interactions."""
    
    def __init__(self):
        self.logger = AutomationLogger()
        self.client: Optional[Client] = None
        self.api: Optional[tweepy.API] = None
        self._setup_twitter_client()
    
    def _setup_twitter_client(self) -> bool:
        """Setup Twitter API client."""
        try:
            # Get credentials from environment
            api_key = os.getenv("TWITTER_API_KEY") or os.getenv("TWITTER_CONSUMER_KEY")
            api_secret = os.getenv("TWITTER_API_SECRET") or os.getenv("TWITTER_CONSUMER_SECRET")
            access_token = os.getenv("TWITTER_ACCESS_TOKEN")
            access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
            bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
            
            if not all([api_key, api_secret, access_token, access_token_secret, bearer_token]):
                self.logger.log_error("❌ Missing Twitter API credentials")
                return False
            
            # Setup v1.1 API for media upload
            auth = OAuth1UserHandler(
                api_key, api_secret, access_token, access_token_secret
            )
            self.api = tweepy.API(auth, wait_on_rate_limit=True)
            
            # Setup v2 API for posting
            self.client = Client(
                bearer_token=bearer_token,
                consumer_key=api_key,
                consumer_secret=api_secret,
                access_token=access_token,
                access_token_secret=access_token_secret,
                wait_on_rate_limit=True
            )
            
            self.logger.log_success("✅ Twitter API client setup complete")
            return True
            
        except Exception as e:
            self.logger.log_error(f"Twitter client setup failed: {e}")
            return False
    
    def post_tweet(self, text: str, image_path: Optional[str] = None) -> Dict[str, Any]:
        """Post a tweet with optional image."""
        try:
            if not self.client:
                return {
                    "success": False,
                    "error": "Twitter client not initialized",
                    "tweet_id": None
                }
            
            media_ids = []
            
            # Upload image if provided
            if image_path and os.path.exists(image_path):
                try:
                    media = self.api.media_upload(image_path)
                    media_ids.append(media.media_id)
                    self.logger.log_info(f"📸 Image uploaded: {image_path}")
                except Exception as e:
                    self.logger.log_warning(f"Failed to upload image: {e}")
            
            # Post the tweet
            response = self.client.create_tweet(
                text=text,
                media_ids=media_ids if media_ids else None
            )
            
            tweet_id = response.data['id']
            self.logger.log_success(f"✅ Tweet posted: {tweet_id}")
            
            return {
                "success": True,
                "tweet_id": tweet_id,
                "text": text,
                "image_path": image_path,
                "media_ids": media_ids
            }
            
        except Exception as e:
            self.logger.log_error(f"Tweet posting failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "tweet_id": None
            }
    
    def post_from_analysis(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Post a tweet from analysis data."""
        try:
            twitter_text = analysis_data.get("data", {}).get("twitter_text", "")
            chat_url = analysis_data.get("data", {}).get("chat_url", "")
            
            if not twitter_text:
                return {
                    "success": False,
                    "error": "No Twitter text found in analysis data",
                    "tweet_id": None
                }
            
            # Create tweet content
            tweet_content = f"🔍 Fresh crypto analysis from FlipsideAI:\n\n{twitter_text}"
            
            # Check character limit
            if len(tweet_content) > 280:
                self.logger.log_warning(f"⚠️ Tweet too long: {len(tweet_content)}/280 characters")
                # Truncate if needed
                max_content_length = 280 - 50  # Leave room for truncation indicator
                tweet_content = tweet_content[:max_content_length] + "..."
            
            # Post the tweet
            result = self.post_tweet(tweet_content)
            
            # Log the post
            self._log_twitter_post(result, analysis_data)
            
            return result
            
        except Exception as e:
            self.logger.log_error(f"Analysis tweet posting failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "tweet_id": None
            }
    
    def _log_twitter_post(self, result: Dict[str, Any], analysis_data: Dict[str, Any]):
        """Log Twitter post to file."""
        try:
            log_data = {
                "timestamp": datetime.now().isoformat(),
                "tweet_id": result.get("tweet_id"),
                "tweet_content": result.get("text", ""),
                "image_path": result.get("image_path", ""),
                "analysis_prompt": analysis_data.get("prompt", ""),
                "analysis_url": analysis_data.get("data", {}).get("chat_url", ""),
                "success": result.get("success", False),
                "error": result.get("error", "")
            }
            
            # Save to daily log file
            log_file = f"logs/twitter_posts_{datetime.now().strftime('%Y%m%d')}.jsonl"
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_data, ensure_ascii=False) + '\n')
            
            self.logger.log_info(f"📝 Twitter post logged to: {log_file}")
            
        except Exception as e:
            self.logger.log_error(f"Failed to log Twitter post: {e}")
