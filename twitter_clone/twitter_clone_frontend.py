#!/usr/bin/env python3
"""
Twitter Clone Frontend - Display tweet previews in a Twitter-like interface.
"""

import os
import json
import webbrowser
from pathlib import Path
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading
import time

class TwitterCloneHandler(SimpleHTTPRequestHandler):
    """Custom handler for serving the Twitter clone."""
    
    def do_GET(self):
        if self.path == '/':
            self.path = '/twitter_clone.html'
        return super().do_GET()

def load_tweet_data():
    """Load all tweet preview data."""
    # Look for tweet_previews in parent directory
    previews_dir = Path("../tweet_previews")
    if not previews_dir.exists():
        return []
    
    tweets = []
    json_files = list(previews_dir.glob("*_tweet_*.json"))
    
    for json_file in sorted(json_files, key=lambda f: f.stat().st_mtime, reverse=True):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                tweet_data = json.load(f)
            
            # Extract metadata from filename
            filename_parts = json_file.stem.split('_')
            analysis_date = filename_parts[1] if len(filename_parts) > 1 else "unknown"
            preview_time = filename_parts[-1] if len(filename_parts) > 2 else "unknown"
            
            # Parse timestamp
            try:
                tweet_time = datetime.fromisoformat(tweet_data['timestamp'].replace('Z', '+00:00'))
                formatted_time = tweet_time.strftime("%b %d, %Y at %I:%M %p")
            except:
                formatted_time = f"{analysis_date} at {preview_time}"
            
            tweets.append({
                'id': json_file.stem,
                'content': tweet_data['tweet_content'],
                'twitter_text': tweet_data['twitter_text'],
                'character_count': tweet_data['character_count'],
                'chat_url': tweet_data['chat_url'],
                'timestamp': formatted_time,
                'analysis_date': analysis_date,
                'preview_time': preview_time,
                'status': 'ready' if tweet_data['character_count'] <= 280 else 'too_long'
            })
        except Exception as e:
            print(f"Error loading {json_file}: {e}")
    
    return tweets

def generate_twitter_clone_html():
    """Generate the Twitter clone HTML page."""
    
    tweets = load_tweet_data()
    
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🐦 FlipsideAI Tweet Preview</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #000;
            color: #fff;
            line-height: 1.4;
        }}
        
        .header {{
            position: sticky;
            top: 0;
            background: rgba(0, 0, 0, 0.8);
            backdrop-filter: blur(10px);
            border-bottom: 1px solid #333;
            padding: 1rem 0;
            z-index: 100;
        }}
        
        .header-content {{
            max-width: 600px;
            margin: 0 auto;
            padding: 0 1rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        
        .logo {{
            font-size: 1.5rem;
            font-weight: bold;
            color: #1da1f2;
        }}
        
        .stats {{
            font-size: 0.9rem;
            color: #666;
        }}
        
        .main-content {{
            max-width: 600px;
            margin: 0 auto;
            padding: 1rem;
        }}
        
        .tweet {{
            background: #111;
            border: 1px solid #333;
            border-radius: 16px;
            padding: 1rem;
            margin-bottom: 1rem;
            transition: all 0.2s ease;
        }}
        
        .tweet:hover {{
            background: #1a1a1a;
            border-color: #444;
        }}
        
        .tweet-header {{
            display: flex;
            align-items: center;
            margin-bottom: 0.5rem;
        }}
        
        .avatar {{
            width: 48px;
            height: 48px;
            border-radius: 50%;
            background: linear-gradient(45deg, #1da1f2, #0d8bd9);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: 1.2rem;
            margin-right: 12px;
        }}
        
        .user-info {{
            flex: 1;
        }}
        
        .username {{
            font-weight: bold;
            color: #fff;
            margin: 0;
        }}
        
        .handle {{
            color: #666;
            margin: 0;
            font-size: 0.9rem;
        }}
        
        .tweet-content {{
            font-size: 1rem;
            line-height: 1.5;
            color: #fff;
            white-space: pre-wrap;
            margin: 0.5rem 0;
        }}
        
        .tweet-meta {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-top: 1rem;
            padding-top: 0.5rem;
            border-top: 1px solid #333;
            font-size: 0.9rem;
            color: #666;
        }}
        
        .character-count {{
            color: {'#e0245e' if any(t['character_count'] > 280 for t in tweets) else '#666'};
            font-weight: bold;
        }}
        
        .tweet-actions {{
            display: flex;
            gap: 1rem;
            margin-top: 0.5rem;
        }}
        
        .action-button {{
            background: none;
            border: none;
            color: #666;
            cursor: pointer;
            padding: 0.5rem;
            border-radius: 8px;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        
        .action-button:hover {{
            background: #1a1a1a;
            color: #1da1f2;
        }}
        
        .chat-link {{
            color: #1da1f2;
            text-decoration: none;
            font-weight: 500;
        }}
        
        .chat-link:hover {{
            text-decoration: underline;
        }}
        
        .status-badge {{
            display: inline-block;
            padding: 0.25rem 0.5rem;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: bold;
            margin-left: 0.5rem;
        }}
        
        .status-ready {{
            background: #1a5f1a;
            color: #4ade80;
        }}
        
        .status-too-long {{
            background: #5f1a1a;
            color: #f87171;
        }}
        
        .empty-state {{
            text-align: center;
            padding: 3rem 1rem;
            color: #666;
        }}
        
        .empty-state h2 {{
            margin-bottom: 1rem;
            color: #999;
        }}
        
        .refresh-button {{
            background: #1da1f2;
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 20px;
            cursor: pointer;
            font-weight: bold;
            margin-top: 1rem;
            transition: background 0.2s ease;
        }}
        
        .refresh-button:hover {{
            background: #0d8bd9;
        }}
        
        .footer {{
            text-align: center;
            padding: 2rem 1rem;
            color: #666;
            border-top: 1px solid #333;
            margin-top: 2rem;
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="header-content">
            <div class="logo">🐦 FlipsideAI Tweets</div>
            <div class="stats">{len(tweets)} tweet{'s' if len(tweets) != 1 else ''} ready</div>
        </div>
    </div>
    
    <div class="main-content">
        {generate_tweets_html(tweets)}
    </div>
    
    <div class="footer">
        <p>Generated by FlipsideAI Twitter Automation</p>
        <p>Last updated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
    </div>
    
    <script>
        // Auto-refresh every 30 seconds
        setTimeout(() => {{
            location.reload();
        }}, 30000);
        
        // Add click handlers for action buttons
        document.addEventListener('DOMContentLoaded', function() {{
            document.querySelectorAll('.action-button').forEach(button => {{
                button.addEventListener('click', function(e) {{
                    e.preventDefault();
                    const action = this.dataset.action;
                    const tweetId = this.dataset.tweetId;
                    
                    if (action === 'copy') {{
                        const tweetContent = this.closest('.tweet').querySelector('.tweet-content').textContent;
                        navigator.clipboard.writeText(tweetContent).then(() => {{
                            this.textContent = '✓ Copied!';
                            setTimeout(() => {{
                                this.textContent = '📋 Copy';
                            }}, 2000);
                        }});
                    }} else if (action === 'view') {{
                        const chatUrl = this.dataset.chatUrl;
                        window.open(chatUrl, '_blank');
                    }}
                }});
            }});
        }});
    </script>
</body>
</html>
"""
    
    return html_content

def generate_tweets_html(tweets):
    """Generate HTML for all tweets."""
    
    if not tweets:
        return """
        <div class="empty-state">
            <h2>No tweets found</h2>
            <p>Run the tweet preview generator to create some tweets!</p>
            <button class="refresh-button" onclick="location.reload()">🔄 Refresh</button>
        </div>
        """
    
    tweets_html = ""
    
    for tweet in tweets:
        status_class = f"status-{tweet['status']}"
        status_text = "✅ Ready" if tweet['status'] == 'ready' else "⚠️ Too Long"
        
        tweets_html += f"""
        <div class="tweet">
            <div class="tweet-header">
                <div class="avatar">AF</div>
                <div class="user-info">
                    <p class="username">AgentFlippy</p>
                    <p class="handle">@AgentFlipp61663</p>
                </div>
            </div>
            
            <div class="tweet-content">{tweet['content']}</div>
            
            <div class="tweet-meta">
                <div>
                    <span>{tweet['timestamp']}</span>
                    <span class="status-badge {status_class}">{status_text}</span>
                </div>
                <div class="character-count">{tweet['character_count']}/280</div>
            </div>
            
            <div class="tweet-actions">
                <button class="action-button" data-action="copy" data-tweet-id="{tweet['id']}">
                    📋 Copy
                </button>
                <button class="action-button" data-action="view" data-chat-url="{tweet['chat_url']}">
                    🔗 View Analysis
                </button>
                <a href="{tweet['chat_url']}" class="action-button" target="_blank">
                    📊 Full Report
                </a>
            </div>
        </div>
        """
    
    return tweets_html

def start_server(port=8080):
    """Start the local server."""
    
    # Generate the HTML file
    html_content = generate_twitter_clone_html()
    
    with open('twitter_clone.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    # Start server
    server = HTTPServer(('localhost', port), TwitterCloneHandler)
    
    print(f"🐦 Twitter Clone Frontend")
    print(f"=" * 40)
    print(f"🌐 Server starting on http://localhost:{port}")
    print(f"📁 Serving tweet previews from: tweet_previews/")
    print(f"🔄 Auto-refresh every 30 seconds")
    print(f"⏹️  Press Ctrl+C to stop")
    print()
    
    # Open browser
    webbrowser.open(f'http://localhost:{port}')
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print(f"\n👋 Server stopped")
        server.shutdown()

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Start Twitter Clone Frontend")
    parser.add_argument("--port", "-p", type=int, default=8080, help="Port to run server on")
    
    args = parser.parse_args()
    
    start_server(args.port)

if __name__ == "__main__":
    main()
