"""
Tweet Preview Generator

Generates tweet previews for local testing and review.
"""

import os
import json
import html
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

from modules.shared.logger import AutomationLogger


class TweetPreviewGenerator:
    """Generates tweet previews from analysis data."""
    
    def __init__(self):
        self.logger = AutomationLogger()
        self.previews_dir = Path("tweet_previews")
        self.previews_dir.mkdir(exist_ok=True)
    
    def create_tweet_preview(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a tweet preview from analysis data."""
        try:
            # Extract data
            twitter_text = analysis_data.get("data", {}).get("twitter_text", "")
            chat_url = analysis_data.get("data", {}).get("chat_url", "")
            timestamp = analysis_data.get("timestamp", datetime.now().isoformat())
            character_count = analysis_data.get("data", {}).get("character_count", 0)
            # Create tweet content
            tweet_content = f"🔍 Fresh crypto analysis from FlipsideAI:\n\n{twitter_text}"
            
            # Create tweet data
            tweet_data = {
                "timestamp": timestamp,
                "tweet_content": tweet_content,
                "twitter_text": twitter_text,
                "chat_url": chat_url,
                "analysis_url": chat_url,
                "character_count": len(tweet_content),
                "success": True,
                "preview_mode": True
            }
            
            return tweet_data
            
        except Exception as e:
            self.logger.log_error(f"Tweet preview creation failed: {e}")
            return {}
    
    def save_tweet_preview(self, tweet_data: Dict[str, Any], analysis_file: str) -> tuple:
        """Save tweet preview to files."""
        try:
            # Generate filename from analysis file
            analysis_filename = Path(analysis_file).stem
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Save JSON data
            json_file = self.previews_dir / f"{analysis_filename}_tweet_{timestamp}.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(tweet_data, f, indent=2, ensure_ascii=False)
            
            # Create HTML preview
            html_file = self.previews_dir / f"{analysis_filename}_preview_{timestamp}.html"
            self._create_html_preview(tweet_data, html_file)
            
            # Create markdown preview
            md_file = self.previews_dir / f"{analysis_filename}_preview_{timestamp}.md"
            self._create_markdown_preview(tweet_data, md_file)
            
            return json_file, html_file, md_file
            
        except Exception as e:
            self.logger.log_error(f"Tweet preview save failed: {e}")
            return None, None, None
    
    def generate_preview_from_latest(self) -> bool:
        """Generate preview from the latest analysis file."""
        try:
            # Find the latest analysis file
            logs_dir = Path("logs")
            analysis_files = list(logs_dir.glob("analysis_*.json"))
            
            if not analysis_files:
                self.logger.log_error("❌ No analysis files found")
                return False
            
            # Get the most recent file
            latest_file = max(analysis_files, key=lambda f: f.stat().st_mtime)
            
            self.logger.log_info(f"📊 Generating tweet preview from: {latest_file.name}")
            
            # Load analysis data
            with open(latest_file, 'r', encoding='utf-8') as f:
                analysis_data = json.load(f)
            
            # Create tweet preview
            tweet_data = self.create_tweet_preview(analysis_data)
            
            # Save preview files
            json_file, html_file, md_file = self.save_tweet_preview(tweet_data, latest_file)
            
            if json_file:
                self.logger.log_success(f"✅ Tweet preview generated:")
                self.logger.log_info(f"   📄 JSON: {json_file}")
                self.logger.log_info(f"   🌐 HTML: {html_file}")
                self.logger.log_info(f"   📝 Markdown: {md_file}")
                
                # Display tweet content
                self.logger.log_info(f"\n🐦 Tweet Content ({tweet_data['character_count']}/280 characters):")
                self.logger.log_info("=" * 50)
                self.logger.log_info(tweet_data['tweet_content'])
                self.logger.log_info("=" * 50)
                
                if tweet_data['character_count'] > 280:
                    self.logger.log_warning("⚠️  WARNING: Tweet is too long!")
                else:
                    self.logger.log_success("✅ Tweet is ready to post!")
                
                return True
            else:
                return False
                
        except Exception as e:
            self.logger.log_error(f"Preview generation failed: {e}")
            return False
    
    def _create_html_preview(self, tweet_data: Dict[str, Any], output_file: Path):
        """Create an HTML preview of the tweet."""
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tweet Preview - {tweet_data['timestamp'][:10]}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background: #f7f9fa;
        }}
        .tweet-container {{
            background: white;
            border: 1px solid #e1e8ed;
            border-radius: 16px;
            padding: 20px;
            margin: 20px 0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        .tweet-header {{
            display: flex;
            align-items: center;
            margin-bottom: 12px;
        }}
        .avatar {{
            width: 48px;
            height: 48px;
            border-radius: 50%;
            background: #1da1f2;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            margin-right: 12px;
        }}
        .user-info {{
            flex: 1;
        }}
        .username {{
            font-weight: bold;
            color: #14171a;
            margin: 0;
        }}
        .handle {{
            color: #657786;
            margin: 0;
            font-size: 14px;
        }}
        .tweet-content {{
            font-size: 16px;
            line-height: 1.4;
            color: #14171a;
            white-space: pre-wrap;
            margin: 12px 0;
        }}
        .tweet-meta {{
            color: #657786;
            font-size: 14px;
            margin-top: 12px;
            padding-top: 12px;
            border-top: 1px solid #e1e8ed;
        }}
        .character-count {{
            text-align: right;
            color: {'#e0245e' if tweet_data['character_count'] > 280 else '#657786'};
            font-weight: bold;
        }}
        .analysis-info {{
            background: #f7f9fa;
            border: 1px solid #e1e8ed;
            border-radius: 8px;
            padding: 16px;
            margin: 20px 0;
        }}
        .analysis-info h3 {{
            margin: 0 0 12px 0;
            color: #14171a;
        }}
        .analysis-info p {{
            margin: 8px 0;
            color: #657786;
        }}
        .chat-link {{
            display: inline-block;
            background: #1da1f2;
            color: white;
            text-decoration: none;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 14px;
            margin-top: 12px;
        }}
        .chat-link:hover {{
            background: #0d8bd9;
        }}
    </style>
</head>
<body>
    <h1>🐦 Tweet Preview</h1>
    
    <div class="tweet-container">
        <div class="tweet-header">
            <div class="avatar">AF</div>
            <div class="user-info">
                <p class="username">AgentFlippy</p>
                <p class="handle">@AgentFlipp61663</p>
            </div>
        </div>
        
        <div class="tweet-content">{html.escape(tweet_data['tweet_content'])}</div>
        
        <div class="tweet-meta">
            <div class="character-count">{tweet_data['character_count']}/280 characters</div>
            <div>📅 {tweet_data['timestamp']}</div>
        </div>
    </div>
    
    <div class="analysis-info">
        <h3>📊 Analysis Information</h3>
        <p><strong>Twitter Text:</strong> {html.escape(tweet_data['twitter_text'])}</p>
        <p><strong>Character Count:</strong> {tweet_data['character_count']}/280</p>
        <p><strong>Status:</strong> {'✅ Ready to post' if tweet_data['character_count'] <= 280 else '⚠️ Too long'}</p>
        <a href="{tweet_data['chat_url']}" class="chat-link" target="_blank">🔗 View Full Analysis</a>
    </div>
</body>
</html>
"""
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def _create_markdown_preview(self, tweet_data: Dict[str, Any], output_file: Path):
        """Create a markdown preview of the tweet."""
        md_content = f"""# 🐦 Tweet Preview

## Tweet Content
```
{tweet_data['tweet_content']}
```

## Analysis Information
- **Twitter Text**: {tweet_data['twitter_text']}
- **Character Count**: {tweet_data['character_count']}/280
- **Status**: {'✅ Ready to post' if tweet_data['character_count'] <= 280 else '⚠️ Too long'}
- **Chat URL**: {tweet_data['chat_url']}
- **Timestamp**: {tweet_data['timestamp']}

## Preview
> **@AgentFlipp61663** (AgentFlippy)
> 
> {tweet_data['tweet_content']}
> 
> 📅 {tweet_data['timestamp']}
> 🔗 [View Full Analysis]({tweet_data['chat_url']})
"""
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(md_content)
