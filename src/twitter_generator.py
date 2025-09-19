#!/usr/bin/env python3
"""
Twitter content generator for Flipside Chat Automation.
Creates engaging tweets from analysis results and screenshots.
"""

import os
import json
import re
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import logging
from .tweet_formatter import TweetFormatter


class TwitterGenerator:
    """Generates Twitter content from analysis results."""
    
    def __init__(self, max_tweet_length: int = 280):
        """
        Initialize the Twitter generator.
        
        Args:
            max_tweet_length: Maximum characters per tweet (default 280)
        """
        self.max_tweet_length = max_tweet_length
        self.logger = logging.getLogger(__name__)
        
        # Twitter-specific formatting
        self.hashtags = [
            "#CryptoAnalysis", "#FlipsideAI", "#BlockchainData", 
            "#CryptoInsights", "#DeFi", "#Bitcoin", "#Ethereum",
            "#CryptoResearch", "#OnChainData", "#CryptoCharts"
        ]
        
        # Analysis type emojis
        self.analysis_emojis = {
            "market_analysis": "📈",
            "volume_analysis": "📊", 
            "user_analysis": "👥",
            "defi_analysis": "🏦",
            "unknown": "🔍"
        }
    
    def generate_tweet_from_analysis(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a tweet from analysis results.
        
        Args:
            analysis_data: Analysis results from the automation
            
        Returns:
            Dictionary containing tweet content and metadata
        """
        try:
            if not analysis_data.get("success", False):
                return self._generate_error_tweet(analysis_data)
            
            data = analysis_data.get("data", {})
            response_text = data.get("response_text", "")
            response_metadata = data.get("response_metadata", {})
            artifacts = data.get("artifacts", [])
            
            # Check if we have extracted Twitter text from the response
            twitter_text = data.get("twitter_text", "")
            
            if twitter_text:
                # Use the extracted Twitter text as the main content
                tweet_content = twitter_text.strip()
                self.logger.info(f"Using extracted Twitter text: {len(tweet_content)} characters")
            else:
                # Fallback to generating tweet content using formatter
                insights = self._extract_insights(response_text)
                tweet_content = TweetFormatter.create_engaging_tweet(
                    response_text, response_metadata.get("analysis_type", "unknown")
                )
                self.logger.info("No Twitter text found, using generated content")
            
            # Add chat link if available - Twitter will create a link card (doesn't count against character limit)
            chat_url = data.get("chat_url", "")
            if chat_url:
                # Convert to shared format if it's a regular chat URL
                if "/chat/" in chat_url and "/shared/chats/" not in chat_url:
                    # Extract the chat ID and convert to shared format
                    chat_id = chat_url.split("/chat/")[-1]
                    shared_url = f"https://flipsidecrypto.xyz/chat/shared/chats/{chat_id}"
                else:
                    shared_url = chat_url
                
                # Add descriptive text and URL - Twitter will create a link card
                link_text = "\n\nHere's the chat link if you want to dive deeper"
                if len(tweet_content) + len(link_text) <= self.max_tweet_length:
                    tweet_content += link_text
                    # The actual URL will be appended by twitter_poster.py
                else:
                    # If text is too long, just add a simple reference
                    simple_text = "\n\nChat link below ⬇️"
                    if len(tweet_content) + len(simple_text) <= self.max_tweet_length:
                        tweet_content += simple_text
                    # The actual URL will be appended by twitter_poster.py
                    self.logger.info("Using simple link reference due to space constraints")
            
            # Select best screenshot
            tweet_image = self._select_best_screenshot(artifacts, data.get("screenshots", []))
            
            # Create tweet metadata
            tweet_metadata = {
                "timestamp": datetime.now().isoformat(),
                "analysis_type": response_metadata.get("analysis_type", "unknown"),
                "word_count": response_metadata.get("word_count", 0),
                "has_artifacts": len(artifacts) > 0,
                "artifact_types": [a.get("type") for a in artifacts],
                "character_count": len(tweet_content),
                "image_path": tweet_image
            }
            
            return {
                "content": tweet_content,
                "image": tweet_image,
                "metadata": tweet_metadata,
                "success": True
            }
            
        except Exception as e:
            self.logger.error(f"Error generating tweet: {e}")
            return {
                "content": "🚨 Analysis completed but encountered an error generating tweet content.",
                "image": None,
                "metadata": {"error": str(e)},
                "success": False
            }
    
    def _extract_insights(self, response_text: str) -> Dict[str, Any]:
        """
        Extract key insights from the analysis response.
        
        Args:
            response_text: The full analysis response text
            
        Returns:
            Dictionary with extracted insights
        """
        insights = {
            "key_findings": [],
            "numbers": [],
            "trends": [],
            "recommendations": []
        }
        
        if not response_text:
            return insights
        
        text_lower = response_text.lower()
        
        # Extract numbers (prices, percentages, volumes)
        number_patterns = [
            r'\$[\d,]+(?:\.\d+)?',  # Dollar amounts
            r'[\d,]+(?:\.\d+)?%',   # Percentages
            r'[\d,]+(?:\.\d+)?\s*(?:billion|million|thousand|b|m|k)',  # Large numbers
            r'[\d,]+(?:\.\d+)?\s*(?:btc|eth|tokens?)',  # Token amounts
        ]
        
        for pattern in number_patterns:
            matches = re.findall(pattern, response_text, re.IGNORECASE)
            insights["numbers"].extend(matches[:3])  # Limit to top 3
        
        # Extract key findings (sentences with important keywords)
        key_phrases = [
            "significant", "notable", "important", "key finding", "major",
            "breakthrough", "surge", "drop", "increase", "decrease",
            "all-time high", "all-time low", "record", "unprecedented"
        ]
        
        sentences = response_text.split('.')
        for sentence in sentences:
            sentence = sentence.strip()
            if any(phrase in sentence.lower() for phrase in key_phrases):
                if len(sentence) < 100:  # Keep sentences concise
                    insights["key_findings"].append(sentence)
        
        # Extract trends
        trend_phrases = [
            "trending", "trend", "momentum", "direction", "pattern",
            "bullish", "bearish", "uptrend", "downtrend", "sideways"
        ]
        
        for sentence in sentences:
            sentence = sentence.strip()
            if any(phrase in sentence.lower() for phrase in trend_phrases):
                if len(sentence) < 80:
                    insights["trends"].append(sentence)
        
        # Extract recommendations
        rec_phrases = [
            "recommend", "suggest", "consider", "should", "advise",
            "buy", "sell", "hold", "watch", "monitor"
        ]
        
        for sentence in sentences:
            sentence = sentence.strip()
            if any(phrase in sentence.lower() for phrase in rec_phrases):
                if len(sentence) < 90:
                    insights["recommendations"].append(sentence)
        
        # Limit results
        insights["key_findings"] = insights["key_findings"][:2]
        insights["trends"] = insights["trends"][:2]
        insights["recommendations"] = insights["recommendations"][:2]
        
        return insights
    
    def _create_tweet_content(self, insights: Dict[str, Any], 
                            metadata: Dict[str, Any], 
                            artifacts: List[Dict[str, Any]]) -> str:
        """
        Create engaging tweet content from insights.
        
        Args:
            insights: Extracted insights from analysis
            metadata: Response metadata
            artifacts: List of captured artifacts
            
        Returns:
            Formatted tweet content
        """
        analysis_type = metadata.get("analysis_type", "unknown")
        emoji = self.analysis_emojis.get(analysis_type, "🔍")
        
        # Start with emoji and analysis type
        tweet_parts = [f"{emoji} Fresh crypto analysis from FlipsideAI:"]
        
        # Add key numbers if available
        if insights["numbers"]:
            key_numbers = insights["numbers"][:2]  # Top 2 numbers
            numbers_text = " | ".join(key_numbers)
            tweet_parts.append(f"📊 Key metrics: {numbers_text}")
        
        # Add main finding
        if insights["key_findings"]:
            finding = insights["key_findings"][0]
            # Clean up the finding
            finding = re.sub(r'[^\w\s$%.,!?-]', '', finding).strip()
            if len(finding) > 60:
                finding = finding[:57] + "..."
            tweet_parts.append(f"💡 {finding}")
        else:
            # Fallback: extract a key sentence from response
            response_sentences = response_text.split('.')
            for sentence in response_sentences:
                sentence = sentence.strip()
                if len(sentence) > 20 and len(sentence) < 80:
                    # Look for sentences with key metrics or insights
                    if any(word in sentence.lower() for word in ['price', 'volume', 'increase', 'decrease', 'trend', 'analysis']):
                        sentence = re.sub(r'[^\w\s$%.,!?-]', '', sentence).strip()
                        tweet_parts.append(f"💡 {sentence}")
                        break
        
        # Add trend if available
        if insights["trends"]:
            trend = insights["trends"][0]
            trend = re.sub(r'[^\w\s$%.,!?-]', '', trend).strip()
            if len(trend) > 50:
                trend = trend[:47] + "..."
            tweet_parts.append(f"📈 {trend}")
        
        # Add recommendation if available and space permits
        if insights["recommendations"]:
            rec = insights["recommendations"][0]
            rec = re.sub(r'[^\w\s$%.,!?-]', '', rec).strip()
            if len(rec) > 40:
                rec = rec[:37] + "..."
            tweet_parts.append(f"🎯 {rec}")
        
        # Join parts
        tweet_content = "\n\n".join(tweet_parts)
        
        # Add chat link if available (this will be added by the main generator)
        # The chat link will be added in the main generate_tweet_from_analysis method
        
        # Add hashtags (fit as many as possible)
        available_space = self.max_tweet_length - len(tweet_content) - 1
        hashtags_to_add = []
        
        for hashtag in self.hashtags:
            if len(hashtag) + 1 <= available_space:
                hashtags_to_add.append(hashtag)
                available_space -= len(hashtag) + 1
            else:
                break
        
        if hashtags_to_add:
            tweet_content += "\n\n" + " ".join(hashtags_to_add)
        
        # Ensure we don't exceed character limit
        if len(tweet_content) > self.max_tweet_length:
            # Truncate and add ellipsis
            tweet_content = tweet_content[:self.max_tweet_length - 3] + "..."
        
        return tweet_content
    
    def _select_best_screenshot(self, artifacts: List[Dict[str, Any]], 
                              screenshots: List[str]) -> Optional[str]:
        """
        Select the best screenshot for the tweet.
        
        Args:
            artifacts: List of captured artifacts
            screenshots: List of screenshot paths
            
        Returns:
            Path to the best screenshot, or None
        """
        if not artifacts and not screenshots:
            return None
        
        # Prioritize chart artifacts
        chart_artifacts = [a for a in artifacts if a.get("type") == "chart"]
        if chart_artifacts:
            return chart_artifacts[0].get("screenshot")
        
        # Then table artifacts
        table_artifacts = [a for a in artifacts if a.get("type") == "table"]
        if table_artifacts:
            return table_artifacts[0].get("screenshot")
        
        # Then any other artifacts
        if artifacts:
            return artifacts[0].get("screenshot")
        
        # Finally, any screenshots
        if screenshots:
            return screenshots[0]
        
        return None
    
    def _generate_error_tweet(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a tweet for failed analysis.
        
        Args:
            analysis_data: Analysis results with error
            
        Returns:
            Error tweet content
        """
        error_msg = analysis_data.get("error", "Unknown error")
        
        tweet_content = f"🚨 FlipsideAI analysis encountered an issue: {error_msg[:100]}..."
        
        # Add hashtags
        tweet_content += "\n\n#CryptoAnalysis #FlipsideAI #Error"
        
        return {
            "content": tweet_content,
            "image": None,
            "metadata": {
                "error": True,
                "original_error": error_msg
            },
            "success": False
        }
    
    def save_tweet_preview(self, tweet_data: Dict[str, Any], 
                          output_dir: str = "tweet_previews") -> str:
        """
        Save tweet preview to file.
        
        Args:
            tweet_data: Generated tweet data
            output_dir: Directory to save preview
            
        Returns:
            Path to saved preview file
        """
        try:
            output_path = Path(output_dir)
            output_path.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            preview_file = output_path / f"tweet_preview_{timestamp}.json"
            
            with open(preview_file, 'w', encoding='utf-8') as f:
                json.dump(tweet_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Tweet preview saved to: {preview_file}")
            return str(preview_file)
            
        except Exception as e:
            self.logger.error(f"Error saving tweet preview: {e}")
            return ""
    
    def format_tweet_for_display(self, tweet_data: Dict[str, Any]) -> str:
        """
        Format tweet data for nice display.
        
        Args:
            tweet_data: Generated tweet data
            
        Returns:
            Formatted string for display
        """
        if not tweet_data.get("success", False):
            return f"❌ Tweet generation failed: {tweet_data.get('metadata', {}).get('error', 'Unknown error')}"
        
        content = tweet_data.get("content", "")
        metadata = tweet_data.get("metadata", {})
        image = tweet_data.get("image")
        
        display = "🐦 TWEET PREVIEW\n"
        display += "=" * 50 + "\n\n"
        display += f"📝 Content ({metadata.get('character_count', 0)} chars):\n"
        display += f"{content}\n\n"
        
        if image:
            display += f"🖼️  Image: {image}\n"
        else:
            display += "🖼️  Image: None\n"
        
        display += f"\n📊 Metadata:\n"
        display += f"  Analysis Type: {metadata.get('analysis_type', 'unknown')}\n"
        display += f"  Has Artifacts: {metadata.get('has_artifacts', False)}\n"
        display += f"  Artifact Types: {metadata.get('artifact_types', [])}\n"
        display += f"  Word Count: {metadata.get('word_count', 0)}\n"
        
        return display
