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
    
    def _find_artifact_screenshot(self, analysis_data: Dict[str, Any]) -> Optional[str]:
        """Find the artifact screenshot from analysis data using multiple fallback methods."""
        artifacts = analysis_data.get("data", {}).get("artifacts", [])
        
        # Method 1: Look in artifacts list
        if artifacts:
            for artifact in artifacts:
                if artifact.get("type") == "analysis_artifact" and artifact.get("screenshot"):
                    screenshot_path = artifact["screenshot"]
                    if screenshot_path and screenshot_path.strip() and os.path.exists(screenshot_path):
                        self.logger.log_info(f"📸 Found artifact screenshot in artifacts list: {screenshot_path}")
                        return screenshot_path
        
        # Method 2: Fallback - check artifact_screenshot field directly
        artifact_screenshot = analysis_data.get("data", {}).get("artifact_screenshot", "")
        if artifact_screenshot and artifact_screenshot.strip() and os.path.exists(artifact_screenshot):
            self.logger.log_info(f"📸 Found artifact screenshot in artifact_screenshot field: {artifact_screenshot}")
            return artifact_screenshot
        
        # Method 3: Fallback - check screenshots list for artifact screenshots
        screenshots = analysis_data.get("data", {}).get("screenshots", [])
        for screenshot in screenshots:
            if screenshot and isinstance(screenshot, str) and "artifact" in screenshot.lower() and os.path.exists(screenshot):
                self.logger.log_info(f"📸 Found artifact screenshot in screenshots list: {screenshot}")
                return screenshot
        
        # Method 4: Last resort - use first screenshot if available
        if screenshots:
            for screenshot in screenshots:
                if screenshot and isinstance(screenshot, str) and os.path.exists(screenshot):
                    self.logger.log_info(f"📸 Using first available screenshot as fallback: {screenshot}")
                    return screenshot
        
        self.logger.log_warning("⚠️ No artifact screenshot found")
        return None
    
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
    
    def _text_to_bold_unicode(self, text: str) -> str:
        """Convert text to Unicode mathematical bold characters."""
        # Map regular characters to mathematical bold Unicode
        bold_map = {
            'A': '\U0001D400', 'B': '\U0001D401', 'C': '\U0001D402', 'D': '\U0001D403',
            'E': '\U0001D404', 'F': '\U0001D405', 'G': '\U0001D406', 'H': '\U0001D407',
            'I': '\U0001D408', 'J': '\U0001D409', 'K': '\U0001D40A', 'L': '\U0001D40B',
            'M': '\U0001D40C', 'N': '\U0001D40D', 'O': '\U0001D40E', 'P': '\U0001D40F',
            'Q': '\U0001D410', 'R': '\U0001D411', 'S': '\U0001D412', 'T': '\U0001D413',
            'U': '\U0001D414', 'V': '\U0001D415', 'W': '\U0001D416', 'X': '\U0001D417',
            'Y': '\U0001D418', 'Z': '\U0001D419',
            'a': '\U0001D41A', 'b': '\U0001D41B', 'c': '\U0001D41C', 'd': '\U0001D41D',
            'e': '\U0001D41E', 'f': '\U0001D41F', 'g': '\U0001D420', 'h': '\U0001D421',
            'i': '\U0001D422', 'j': '\U0001D423', 'k': '\U0001D424', 'l': '\U0001D425',
            'm': '\U0001D426', 'n': '\U0001D427', 'o': '\U0001D428', 'p': '\U0001D429',
            'q': '\U0001D42A', 'r': '\U0001D42B', 's': '\U0001D42C', 't': '\U0001D42D',
            'u': '\U0001D42E', 'v': '\U0001D42F', 'w': '\U0001D430', 'x': '\U0001D431',
            'y': '\U0001D432', 'z': '\U0001D433',
            '0': '\U0001D7CE', '1': '\U0001D7CF', '2': '\U0001D7D0', '3': '\U0001D7D1',
            '4': '\U0001D7D2', '5': '\U0001D7D3', '6': '\U0001D7D4', '7': '\U0001D7D5',
            '8': '\U0001D7D6', '9': '\U0001D7D7',
            ' ': ' ', ':': ':', '%': '%', '$': '$', '(': '(', ')': ')', 
            '&': '&', '#': '#', '!': '!', '?': '?', '-': '-', '=': '=',
            '/': '/', '.': '.', ',': ',', '≠': '≠', '>': '>', '<': '<',
        }
        return ''.join(bold_map.get(c, c) for c in text)
    
    def _format_twitter_text(self, text: str) -> str:
        """Format Twitter text: remove leading colon, add line breaks for bullets, bold/underline title."""
        try:
            if not text:
                return text
            
            # Remove leading ": " if present
            text = text.lstrip(": ").strip()
            
            # Handle case where text might be all on one line with inline bullets
            # First, split by common patterns to identify title and bullets
            lines = text.split('\n')
            if len(lines) == 1:
                # Single line - need to parse it
                # Pattern: "Title: • bullet1 • bullet2 • bullet3"
                if ':' in text and '•' in text:
                    # Split by colon to separate title from bullets
                    parts = text.split(':', 1)
                    if len(parts) == 2:
                        title = parts[0].strip()
                        bullets_text = parts[1].strip()
                        # Now split bullets
                        bullets = [b.strip() for b in bullets_text.split('•') if b.strip()]
                        # Reconstruct with proper formatting
                        lines = [f"{title}:"] + [f"• {b}" for b in bullets]
            
            formatted_lines = []
            title_found = False
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Check if this is the title (first non-bullet line, or line ending with colon)
                if not title_found:
                    # Check if line ends with colon (title pattern) or doesn't start with bullet
                    if line.endswith(':') or not line.startswith(('•', '-', '*', '◦', '▪', '▫')):
                        # This is the title
                        title = line.rstrip(':').strip()
                        # Remove any leading colon if still present
                        title = title.lstrip(": ").strip()
                        
                        # Apply bold and underline using Unicode
                        # Use mathematical bold Unicode for bold
                        bold_title = self._text_to_bold_unicode(title)
                        # Add underline using box drawing characters - match title length
                        underline_length = min(len(title), 50)  # Cap at 50 characters for readability
                        underline = "━" * underline_length
                        formatted_title = f"{underline}\n{bold_title}\n{underline}"
                        
                        formatted_lines.append(formatted_title)
                        title_found = True
                    else:
                        # First line is a bullet, no title
                        formatted_lines.append(line)
                else:
                    # After title, process bullets
                    if line.startswith(('•', '-', '*', '◦', '▪', '▫')):
                        formatted_lines.append(line)
                    else:
                        # Might be inline bullets, split them
                        if '•' in line:
                            # Split by bullet and reformat
                            parts = [p.strip() for p in line.split('•') if p.strip()]
                            for part in parts:
                                if not part.startswith(('•', '-', '*')):
                                    formatted_lines.append(f"• {part}")
                                else:
                                    formatted_lines.append(part)
                        else:
                            formatted_lines.append(line)
            
            # Join with newlines
            formatted_text = '\n'.join(formatted_lines)
            
            # Final cleanup: ensure bullet points are on separate lines
            # Replace patterns like "• item1 • item2" with "• item1\n• item2"
            formatted_text = formatted_text.replace(' • ', '\n• ')
            formatted_text = formatted_text.replace(' - ', '\n- ')
            formatted_text = formatted_text.replace(' * ', '\n* ')
            
            # Remove any double newlines
            while '\n\n\n' in formatted_text:
                formatted_text = formatted_text.replace('\n\n\n', '\n\n')
            
            return formatted_text.strip()
            
        except Exception as e:
            self.logger.log_error(f"Twitter text formatting failed: {e}")
            return text
    
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
            
            # Format the Twitter text
            tweet_content = self._format_twitter_text(twitter_text)
            
            # Check character limit and handle bullet points
            if len(tweet_content) > 280:
                self.logger.log_warning(f"⚠️ Tweet too long: {len(tweet_content)}/280 characters")
                # For bullet points, try to preserve as many complete bullets as possible
                tweet_content = self._truncate_with_bullet_points(tweet_content)
            
            # Find the artifact screenshot using helper method
            image_path = self._find_artifact_screenshot(analysis_data)
            
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
            
            # Format the Twitter text
            tweet_content = self._format_twitter_text(twitter_text)
            
            # Check character limit and handle bullet points
            if len(tweet_content) > 280:
                self.logger.log_warning(f"⚠️ Tweet too long: {len(tweet_content)}/280 characters")
                # For bullet points, try to preserve as many complete bullets as possible
                tweet_content = self._truncate_with_bullet_points(tweet_content)
            
            # Find the artifact screenshot using helper method
            image_path = self._find_artifact_screenshot(analysis_data)
            
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
