#!/usr/bin/env python3
"""
Advanced tweet formatting utilities for better content extraction and formatting.
"""

import re
from typing import List, Dict, Any, Tuple


class TweetFormatter:
    """Advanced formatting utilities for tweet content."""
    
    @staticmethod
    def extract_key_metrics(text: str) -> List[str]:
        """Extract key financial metrics from text."""
        metrics = []
        
        # Price patterns
        price_patterns = [
            r'\$[\d,]+(?:\.\d+)?',  # $45,230
            r'[\d,]+(?:\.\d+)?\s*USD',  # 45230 USD
        ]
        
        # Percentage patterns
        percent_patterns = [
            r'[\d,]+(?:\.\d+)?%',  # 2.3%
            r'[\+\-][\d,]+(?:\.\d+)?%',  # +2.3%
        ]
        
        # Volume patterns
        volume_patterns = [
            r'[\d,]+(?:\.\d+)?\s*[Bb]illion',  # 2.1 billion
            r'[\d,]+(?:\.\d+)?\s*[Mm]illion',  # 500 million
            r'[\d,]+(?:\.\d+)?\s*[Kk]',  # 1.2K
            r'\$[\d,]+(?:\.\d+)?[BbMmKk]',  # $2.1B
        ]
        
        all_patterns = price_patterns + percent_patterns + volume_patterns
        
        for pattern in all_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            metrics.extend(matches)
        
        # Remove duplicates and limit
        unique_metrics = list(dict.fromkeys(metrics))
        return unique_metrics[:3]  # Top 3 metrics
    
    @staticmethod
    def extract_key_insights(text: str) -> List[str]:
        """Extract key insights and findings."""
        insights = []
        
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        
        # Keywords that indicate important insights
        insight_keywords = [
            'significant', 'notable', 'important', 'key finding', 'major',
            'breakthrough', 'surge', 'drop', 'increase', 'decrease',
            'all-time high', 'all-time low', 'record', 'unprecedented',
            'bullish', 'bearish', 'momentum', 'resistance', 'support'
        ]
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 20 or len(sentence) > 100:
                continue
                
            sentence_lower = sentence.lower()
            if any(keyword in sentence_lower for keyword in insight_keywords):
                # Clean the sentence
                clean_sentence = re.sub(r'[^\w\s$%.,!?-]', '', sentence).strip()
                if clean_sentence:
                    insights.append(clean_sentence)
        
        return insights[:2]  # Top 2 insights
    
    @staticmethod
    def extract_trends(text: str) -> List[str]:
        """Extract trend information."""
        trends = []
        
        sentences = re.split(r'[.!?]+', text)
        
        trend_keywords = [
            'trending', 'trend', 'momentum', 'direction', 'pattern',
            'bullish', 'bearish', 'uptrend', 'downtrend', 'sideways',
            'breaking', 'resistance', 'support', 'breakthrough'
        ]
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 15 or len(sentence) > 80:
                continue
                
            sentence_lower = sentence.lower()
            if any(keyword in sentence_lower for keyword in trend_keywords):
                clean_sentence = re.sub(r'[^\w\s$%.,!?-]', '', sentence).strip()
                if clean_sentence:
                    trends.append(clean_sentence)
        
        return trends[:2]  # Top 2 trends
    
    @staticmethod
    def extract_recommendations(text: str) -> List[str]:
        """Extract trading recommendations."""
        recommendations = []
        
        sentences = re.split(r'[.!?]+', text)
        
        rec_keywords = [
            'recommend', 'suggest', 'consider', 'should', 'advise',
            'buy', 'sell', 'hold', 'watch', 'monitor', 'target',
            'stop loss', 'resistance', 'support'
        ]
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 20 or len(sentence) > 90:
                continue
                
            sentence_lower = sentence.lower()
            if any(keyword in sentence_lower for keyword in rec_keywords):
                clean_sentence = re.sub(r'[^\w\s$%.,!?-]', '', sentence).strip()
                if clean_sentence:
                    recommendations.append(clean_sentence)
        
        return recommendations[:1]  # Top 1 recommendation
    
    @staticmethod
    def format_tweet_content(metrics: List[str], insights: List[str], 
                           trends: List[str], recommendations: List[str],
                           analysis_type: str, max_length: int = 280) -> str:
        """Format all extracted content into a tweet."""
        
        # Analysis type emojis
        emoji_map = {
            "market_analysis": "📈",
            "volume_analysis": "📊", 
            "user_analysis": "👥",
            "defi_analysis": "🏦",
            "unknown": "🔍"
        }
        
        emoji = emoji_map.get(analysis_type, "🔍")
        
        # Start building tweet
        tweet_parts = [f"{emoji} Fresh crypto analysis from FlipsideAI:"]
        
        # Add metrics if available
        if metrics:
            metrics_text = " | ".join(metrics[:2])  # Top 2 metrics
            tweet_parts.append(f"📊 Key metrics: {metrics_text}")
        
        # Add main insight
        if insights:
            insight = insights[0]
            if len(insight) > 60:
                insight = insight[:57] + "..."
            tweet_parts.append(f"💡 {insight}")
        elif trends:
            # Use trend as insight if no insights
            trend = trends[0]
            if len(trend) > 60:
                trend = trend[:57] + "..."
            tweet_parts.append(f"📈 {trend}")
        
        # Add trend if available and different from insight
        if trends and len(trends) > 1:
            trend = trends[1]
            if len(trend) > 50:
                trend = trend[:47] + "..."
            tweet_parts.append(f"📈 {trend}")
        
        # Add recommendation if space allows
        if recommendations:
            rec = recommendations[0]
            if len(rec) > 40:
                rec = rec[:37] + "..."
            tweet_parts.append(f"🎯 {rec}")
        
        # Join parts
        tweet_content = "\n\n".join(tweet_parts)
        
        # Add hashtags
        hashtags = [
            "#CryptoAnalysis", "#FlipsideAI", "#BlockchainData", 
            "#CryptoInsights", "#DeFi", "#Bitcoin", "#Ethereum"
        ]
        
        available_space = max_length - len(tweet_content) - 1
        hashtags_to_add = []
        
        for hashtag in hashtags:
            if len(hashtag) + 1 <= available_space:
                hashtags_to_add.append(hashtag)
                available_space -= len(hashtag) + 1
            else:
                break
        
        if hashtags_to_add:
            tweet_content += "\n\n" + " ".join(hashtags_to_add)
        
        # Final length check
        if len(tweet_content) > max_length:
            tweet_content = tweet_content[:max_length - 3] + "..."
        
        return tweet_content
    
    @staticmethod
    def create_engaging_tweet(response_text: str, analysis_type: str = "unknown") -> str:
        """Create an engaging tweet from analysis response."""
        
        # Extract all components
        metrics = TweetFormatter.extract_key_metrics(response_text)
        insights = TweetFormatter.extract_key_insights(response_text)
        trends = TweetFormatter.extract_trends(response_text)
        recommendations = TweetFormatter.extract_recommendations(response_text)
        
        # Format into tweet
        return TweetFormatter.format_tweet_content(
            metrics, insights, trends, recommendations, analysis_type
        )
