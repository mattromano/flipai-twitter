"""
Analysis Prompts Configuration for Flipside Chat Automation

Contains various crypto analysis prompts focused on generating insights,
visualizations, and Twitter-worthy summaries.
"""

from typing import List, Dict
from datetime import datetime, timedelta


class AnalysisPrompts:
    """Collection of analysis prompts for different focus areas."""
    
    # DeFi Protocol Analysis Prompts
    DEFI_PROTOCOLS = [
        "Analyze Ethereum DeFi protocol activity over the past 7 days. Which protocols saw the biggest user growth? Create a visualization showing the top 10 protocols by unique users.",
        
        "Compare TVL and transaction volume across the top 5 DeFi protocols this week. Which protocol is showing the most sustainable growth patterns?",
        
        "Analyze yield farming trends across major DeFi protocols. What are the highest yielding strategies and how have they changed in the last 30 days?",
        
        "Examine DEX trading volume and liquidity depth across Uniswap, SushiSwap, and Curve. Which DEX is gaining market share and why?",
        
        "Analyze lending protocol utilization rates (Aave, Compound, MakerDAO). What are the current borrowing trends and which assets are most in demand?"
    ]
    
    # Layer 2 and Scaling Solutions
    LAYER2_ANALYSIS = [
        "Compare quality user behavior across Base, Arbitrum, and Optimism this month. Create a visualization showing daily active users and transaction patterns.",
        
        "Analyze gas fee trends and transaction throughput on Ethereum L2s. Which solution is providing the best cost-performance ratio?",
        
        "Examine DeFi protocol adoption on Layer 2 networks. Which L2 is seeing the fastest growth in DeFi TVL and why?",
        
        "Compare developer activity and new contract deployments across Polygon, Arbitrum, and Optimism. Which ecosystem is most active?",
        
        "Analyze cross-chain bridge usage patterns. What are the most popular routes and how has volume changed over the past 30 days?"
    ]
    
    # Market and Trading Analysis
    MARKET_INSIGHTS = [
        "What's the most significant trend in crypto markets this week based on on-chain data? Focus on whale movements and institutional activity.",
        
        "Analyze stablecoin supply and usage patterns. Which stablecoins are gaining adoption and what does this tell us about market sentiment?",
        
        "Examine Bitcoin and Ethereum on-chain metrics (active addresses, transaction volume, fees). What do these indicators suggest about network health?",
        
        "Analyze NFT marketplace activity and trends. Which collections are driving the most volume and what patterns do you see in buyer behavior?",
        
        "Compare CEX vs DEX trading volumes for major cryptocurrencies. What percentage of trading is happening on-chain vs off-chain?"
    ]
    
    # User Behavior and Adoption
    USER_BEHAVIOR = [
        "Analyze new user onboarding patterns across major crypto platforms. What are the most common first transactions for new users?",
        
        "Examine wallet creation and usage patterns. How many new wallets are being created daily and what's the typical usage lifecycle?",
        
        "Analyze staking participation rates across different networks. Which networks have the highest staking adoption and why?",
        
        "Compare user retention rates across DeFi protocols. Which protocols are best at keeping users engaged over time?",
        
        "Analyze mobile vs desktop usage patterns in crypto applications. What percentage of users are accessing DeFi from mobile devices?"
    ]
    
    # Protocol-Specific Analysis
    PROTOCOL_DEEP_DIVES = [
        "Deep dive into Uniswap V3 liquidity provision patterns. Which fee tiers are most popular and how do they correlate with volatility?",
        
        "Analyze Aave lending pool utilization and interest rate dynamics. What factors drive rate changes and how do users respond?",
        
        "Examine Compound governance participation and proposal success rates. How active is the community in protocol governance?",
        
        "Analyze Curve stablecoin swap patterns and impermanent loss protection. Which pools are most efficient for large trades?",
        
        "Deep dive into MakerDAO collateralization ratios and liquidation patterns. What are the risk management trends?"
    ]
    
    # Emerging Trends and Innovation
    EMERGING_TRENDS = [
        "Identify emerging DeFi protocols with less than $100M TVL that are showing strong growth. What makes them unique?",
        
        "Analyze the rise of liquid staking derivatives. Which protocols are gaining traction and how do they compare to traditional staking?",
        
        "Examine cross-chain DeFi composability patterns. Which protocols are being used together most frequently?",
        
        "Analyze the growth of real-world asset (RWA) tokenization in DeFi. What assets are being tokenized and what's driving adoption?",
        
        "Examine the impact of account abstraction on user experience. How are smart wallets changing user behavior patterns?"
    ]
    
    # Twitter-Optimized Summaries
    TWITTER_SUMMARIES = [
        "Create a Twitter thread summarizing the most important DeFi trends this week. Include key metrics and visualizations.",
        
        "Generate a tweet-worthy summary of Layer 2 adoption trends with key statistics and growth percentages.",
        
        "Summarize the most significant on-chain activity this month in a format suitable for Twitter. Include charts and key insights.",
        
        "Create a Twitter-friendly analysis of stablecoin market dynamics with visual data and key takeaways.",
        
        "Generate a tweet thread about emerging DeFi protocols that are gaining traction. Focus on what makes them unique."
    ]
    
    @classmethod
    def get_all_prompts(cls) -> List[str]:
        """Get all available prompts as a single list."""
        all_prompts = []
        all_prompts.extend(cls.DEFI_PROTOCOLS)
        all_prompts.extend(cls.LAYER2_ANALYSIS)
        all_prompts.extend(cls.MARKET_INSIGHTS)
        all_prompts.extend(cls.USER_BEHAVIOR)
        all_prompts.extend(cls.PROTOCOL_DEEP_DIVES)
        all_prompts.extend(cls.EMERGING_TRENDS)
        all_prompts.extend(cls.TWITTER_SUMMARIES)
        return all_prompts
    
    @classmethod
    def get_prompts_by_category(cls) -> Dict[str, List[str]]:
        """Get prompts organized by category."""
        return {
            "defi_protocols": cls.DEFI_PROTOCOLS,
            "layer2_analysis": cls.LAYER2_ANALYSIS,
            "market_insights": cls.MARKET_INSIGHTS,
            "user_behavior": cls.USER_BEHAVIOR,
            "protocol_deep_dives": cls.PROTOCOL_DEEP_DIVES,
            "emerging_trends": cls.EMERGING_TRENDS,
            "twitter_summaries": cls.TWITTER_SUMMARIES
        }
    
    @classmethod
    def get_daily_prompts(cls, days_ahead: int = 7) -> List[str]:
        """
        Get a list of prompts for the next N days using deterministic rotation.
        
        Args:
            days_ahead: Number of days to generate prompts for
            
        Returns:
            List of prompts for each day
        """
        all_prompts = cls.get_all_prompts()
        daily_prompts = []
        
        for i in range(days_ahead):
            day_of_year = (datetime.now() + timedelta(days=i)).timetuple().tm_yday
            prompt_index = day_of_year % len(all_prompts)
            daily_prompts.append(all_prompts[prompt_index])
        
        return daily_prompts
    
    @classmethod
    def get_weekly_rotation(cls) -> List[str]:
        """Get a curated set of prompts for weekly rotation."""
        return [
            cls.DEFI_PROTOCOLS[0],      # Monday: DeFi protocol analysis
            cls.LAYER2_ANALYSIS[0],     # Tuesday: Layer 2 comparison
            cls.MARKET_INSIGHTS[0],     # Wednesday: Market trends
            cls.USER_BEHAVIOR[0],       # Thursday: User behavior
            cls.PROTOCOL_DEEP_DIVES[0], # Friday: Protocol deep dive
            cls.EMERGING_TRENDS[0],     # Saturday: Emerging trends
            cls.TWITTER_SUMMARIES[0]    # Sunday: Twitter summary
        ]
    
    @classmethod
    def get_monthly_rotation(cls) -> List[str]:
        """Get a curated set of prompts for monthly rotation."""
        return [
            "Analyze the most significant DeFi protocol developments this month. Which protocols gained the most users and TVL?",
            "Compare Layer 2 ecosystem growth across all major networks. Which solutions are winning market share?",
            "Examine the evolution of crypto market structure this month. What new patterns are emerging?",
            "Analyze user adoption trends across different crypto sectors. Where is growth accelerating?",
            "Deep dive into the most innovative DeFi protocols launched this month. What makes them unique?",
            "Examine cross-chain activity and bridge usage patterns. How is the multi-chain ecosystem evolving?",
            "Analyze governance participation and protocol upgrades across major DeFi protocols this month.",
            "Compare staking and yield farming trends. Which strategies are most popular and profitable?",
            "Examine NFT and gaming sector activity. What trends are driving growth in these areas?",
            "Analyze institutional adoption patterns and large transaction flows. What do they reveal about market sentiment?",
            "Deep dive into stablecoin market dynamics and regulatory developments this month.",
            "Examine developer activity and new project launches. Which ecosystems are most active?",
            "Analyze the impact of major protocol upgrades and governance decisions this month.",
            "Compare fee structures and user costs across different networks and protocols.",
            "Examine the growth of real-world asset tokenization and its impact on DeFi.",
            "Analyze the evolution of DeFi composability and protocol integration patterns.",
            "Deep dive into liquid staking derivatives and their growing adoption.",
            "Examine the rise of account abstraction and its impact on user experience.",
            "Analyze the growth of cross-chain DeFi and interoperability solutions.",
            "Compare the performance of different DeFi yield strategies this month.",
            "Examine the impact of regulatory developments on DeFi protocol usage.",
            "Analyze the growth of decentralized identity and reputation systems.",
            "Deep dive into the evolution of automated market makers and their efficiency.",
            "Examine the growth of decentralized insurance and risk management protocols.",
            "Analyze the impact of MEV (Maximal Extractable Value) on DeFi protocols.",
            "Compare the adoption of different consensus mechanisms and their trade-offs.",
            "Examine the growth of decentralized storage and compute solutions.",
            "Analyze the evolution of cross-chain messaging and interoperability protocols.",
            "Deep dive into the growth of decentralized social and content platforms.",
            "Examine the impact of quantum computing threats on cryptographic protocols."
        ]


# Configuration for prompt selection strategy
PROMPT_CONFIG = {
    "rotation_strategy": "daily",  # Options: "daily", "weekly", "monthly", "random"
    "include_visualizations": True,
    "twitter_optimized": True,
    "focus_areas": [
        "defi_protocols",
        "layer2_analysis", 
        "market_insights",
        "user_behavior"
    ],
    "time_frames": ["7d", "30d", "90d"],
    "max_prompt_length": 500
}


def get_prompt_for_today() -> str:
    """
    Get the prompt for today based on the configured rotation strategy.
    
    Returns:
        Selected prompt for today
    """
    strategy = PROMPT_CONFIG.get("rotation_strategy", "daily")
    
    if strategy == "daily":
        prompts = AnalysisPrompts.get_daily_prompts(1)
        return prompts[0] if prompts else AnalysisPrompts.get_all_prompts()[0]
    elif strategy == "weekly":
        day_of_week = datetime.now().weekday()
        prompts = AnalysisPrompts.get_weekly_rotation()
        return prompts[day_of_week] if day_of_week < len(prompts) else prompts[0]
    elif strategy == "monthly":
        day_of_month = datetime.now().day - 1
        prompts = AnalysisPrompts.get_monthly_rotation()
        return prompts[day_of_month % len(prompts)]
    else:  # random
        import random
        prompts = AnalysisPrompts.get_all_prompts()
        return random.choice(prompts)


def get_prompts_for_focus_area(area: str) -> List[str]:
    """
    Get prompts for a specific focus area.
    
    Args:
        area: Focus area name
        
    Returns:
        List of prompts for the focus area
    """
    prompts_by_category = AnalysisPrompts.get_prompts_by_category()
    return prompts_by_category.get(area, [])
