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
    
    def post_from_analysis(self, analysis_data: Dict[str, Any], test_mode: bool = False) -> Dict[str, Any]:
        """Post a tweet from analysis data."""
        try:
            twitter_text = analysis_data.get("data", {}).get("twitter_text", "")
            chat_url = analysis_data.get("data", {}).get("chat_url", "")
            artifacts = analysis_data.get("data", {}).get("artifacts", [])
            
            if not twitter_text:
                return {
                    "success": False,
                    "error": "No Twitter text found in analysis data",
                    "tweet_id": None
                }
            
            # Use only the twitter_text without any prefix
            tweet_content = twitter_text
            
            # Check character limit and handle bullet points
            if len(tweet_content) > 280:
                self.logger.log_warning(f"⚠️ Tweet too long: {len(tweet_content)}/280 characters")
                # For bullet points, try to preserve as many complete bullets as possible
                tweet_content = self._truncate_with_bullet_points(tweet_content)
            
            # Find the artifact screenshot
            image_path = None
            if artifacts:
                for artifact in artifacts:
                    if artifact.get("type") == "analysis_artifact" and artifact.get("screenshot"):
                        image_path = artifact["screenshot"]
                        break
            
            # In test mode, just return the preview without posting
            if test_mode:
                return {
                    "success": True,
                    "test_mode": True,
                    "tweet_content": tweet_content,
                    "image_path": image_path,
                    "chat_url": chat_url,
                    "tweet_id": "TEST_MODE"
                }
            
            # Post the tweet with image
            result = self.post_tweet(tweet_content, image_path)
            
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
    
    def create_tweet_preview(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a preview of what the tweet will look like without posting."""
        try:
            twitter_text = analysis_data.get("data", {}).get("twitter_text", "")
            chat_url = analysis_data.get("data", {}).get("chat_url", "")
            artifacts = analysis_data.get("data", {}).get("artifacts", [])
            
            if not twitter_text:
                return {
                    "success": False,
                    "error": "No Twitter text found in analysis data"
                }
            
            # Use only the twitter_text without any prefix
            tweet_content = twitter_text
            
            # Check character limit and handle bullet points
            if len(tweet_content) > 280:
                self.logger.log_warning(f"⚠️ Tweet too long: {len(tweet_content)}/280 characters")
                # For bullet points, try to preserve as many complete bullets as possible
                tweet_content = self._truncate_with_bullet_points(tweet_content)
            
            # Find the artifact screenshot
            image_path = None
            if artifacts:
                for artifact in artifacts:
                    if artifact.get("type") == "analysis_artifact" and artifact.get("screenshot"):
                        image_path = artifact["screenshot"]
                        break
            
            return {
                "success": True,
                "tweet_content": tweet_content,
                "image_path": image_path,
                "chat_url": chat_url,
                "character_count": len(tweet_content),
                "has_image": image_path is not None,
                "image_exists": os.path.exists(image_path) if image_path else False
            }
            
        except Exception as e:
            self.logger.log_error(f"Tweet preview creation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def post_reply(self, original_tweet_id: str, reply_text: str) -> Dict[str, Any]:
        """Post a reply to an existing tweet."""
        try:
            if not self.client:
                return {
                    "success": False,
                    "error": "Twitter client not initialized",
                    "tweet_id": None
                }
            
            # Post the reply
            response = self.client.create_tweet(
                text=reply_text,
                in_reply_to_tweet_id=original_tweet_id
            )
            
            reply_id = response.data['id']
            self.logger.log_success(f"✅ Reply posted: {reply_id}")
            
            return {
                "success": True,
                "tweet_id": reply_id,
                "text": reply_text,
                "in_reply_to_tweet_id": original_tweet_id
            }
            
        except Exception as e:
            self.logger.log_error(f"Reply posting failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "tweet_id": None
            }
    
    def post_analysis_link_reply(self, original_tweet_id: str, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Post a reply with a link to the analysis."""
        try:
            chat_url = analysis_data.get("data", {}).get("chat_url", "")
            analysis_prompt = analysis_data.get("prompt", "")
            
            if not chat_url:
                return {
                    "success": False,
                    "error": "No analysis URL found",
                    "tweet_id": None
                }
            
            # Create reply text with the analysis link
            reply_text = f"📊 Full analysis: {chat_url}"
            
            # Check character limit (280 - length of original tweet context)
            if len(reply_text) > 280:
                # Truncate the URL if needed, but keep it functional
                max_text_length = 250  # Leave room for URL
                truncated_prompt = analysis_prompt[:max_text_length - len("📊 Full analysis: ") - 20] + "..."
                reply_text = f"📊 {truncated_prompt}: {chat_url}"
            
            return self.post_reply(original_tweet_id, reply_text)
            
        except Exception as e:
            self.logger.log_error(f"Analysis link reply failed: {e}")
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
    
    def _truncate_with_bullet_points(self, text: str, max_length: int = 280) -> str:
        """Truncate text while preserving complete bullet points."""
        try:
            if len(text) <= max_length:
                return text
            
            lines = text.split('\n')
            truncated_lines = []
            current_length = 0
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Check if adding this line would exceed the limit
                line_length = len(line) + (1 if truncated_lines else 0)  # +1 for newline
                
                if current_length + line_length > max_length - 3:  # -3 for "..."
                    # If we have some content, add truncation indicator
                    if truncated_lines:
                        truncated_lines.append("...")
                    break
                
                truncated_lines.append(line)
                current_length += line_length
            
            result = '\n'.join(truncated_lines)
            self.logger.log_info(f"📝 Truncated tweet to {len(result)} characters, preserving {len([l for l in truncated_lines if l.startswith('•')])} bullet points")
            return result
            
        except Exception as e:
            self.logger.log_error(f"Bullet point truncation failed: {e}")
            # Fallback to simple truncation
            return text[:max_length-3] + "..."
