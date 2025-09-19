#!/usr/bin/env python3
"""
Complete workflow: Flipside AI automation + Twitter posting.
Runs the full pipeline from analysis to Twitter post.
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  python-dotenv not installed. Install with: pip install python-dotenv")

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.chat_automation_robust import RobustFlipsideChatAutomation
from src.automation_logger import setup_automation_logging
from twitter_poster import TwitterPoster


def run_full_workflow(custom_prompt: str = None, post_to_twitter: bool = True):
    """
    Run the complete workflow: analysis + Twitter posting.
    
    Args:
        custom_prompt: Custom analysis prompt (optional)
        post_to_twitter: Whether to post to Twitter (default: True)
    """
    print("🚀 Flipside AI + Twitter Full Workflow")
    print("=" * 60)
    
    # Setup logging
    debug_mode = os.getenv("DEBUG_MODE", "false").lower() == "true"
    logger = setup_automation_logging(debug_mode=debug_mode)
    
    # Initialize automation
    automation = RobustFlipsideChatAutomation()
    
    try:
        # Step 1: Run Flipside AI analysis
        logger.log_info("📊 Starting Flipside AI analysis...")
        
        if not custom_prompt:
            custom_prompt = "Give me a full analysis comparing the supply of USDT and USDC across all the top blockchains"
        
        # Override with fast capture method
        def fast_capture_results():
            """Fast version of capture_results."""
            try:
                logger.log_info("Fast capturing analysis results")
                
                results = {
                    "timestamp": datetime.now().isoformat(),
                    "chat_url": automation.driver.current_url,
                    "response_text": "",
                    "screenshots": [],
                    "artifacts": [],
                    "response_metadata": {},
                    "twitter_text": ""
                }
                
                # Quick text extraction - focus on chat content, not sidebar
                try:
                    # Try to find the main chat content area
                    chat_selectors = [
                        '[data-testid="chat-messages"]',
                        '.chat-messages',
                        '.conversation',
                        '.messages',
                        'main',
                        '[role="main"]'
                    ]
                    
                    chat_text = ""
                    for selector in chat_selectors:
                        try:
                            chat_element = automation.driver.find_element("css selector", selector)
                            if chat_element and chat_element.is_displayed():
                                chat_text = chat_element.text
                                if len(chat_text) > 100:  # Make sure we got substantial content
                                    break
                        except:
                            continue
                    
                    # Fallback to body text if no specific chat area found
                    if not chat_text or len(chat_text) < 100:
                        body_text = automation.driver.find_element("tag name", "body").text
                        # Filter out sidebar content by looking for the main analysis
                        lines = body_text.split('\n')
                        filtered_lines = []
                        skip_sidebar = True
                        
                        for line in lines:
                            line = line.strip()
                            # Skip sidebar content
                            if any(sidebar_word in line.lower() for sidebar_word in ['toggle sidebar', 'start a chat', 'artifacts', 'rules', 'recent chats', 'flipsideai', 'beta']):
                                skip_sidebar = True
                                continue
                            # Start capturing when we see actual content
                            if len(line) > 20 and not skip_sidebar:
                                filtered_lines.append(line)
                            # Look for analysis indicators
                            if any(indicator in line.lower() for indicator in ['analysis', 'data shows', 'according to', 'the results', 'key findings']):
                                skip_sidebar = False
                                filtered_lines.append(line)
                        
                        chat_text = '\n'.join(filtered_lines)
                    
                    if chat_text:
                        results["response_text"] = chat_text
                        logger.log_info(f"Extracted chat text: {len(chat_text)} characters")
                        
                        # Quick Twitter text extraction
                        if "TWITTER_TEXT" in chat_text:
                            lines = chat_text.split('\n')
                            twitter_content = ""
                            
                            for line in lines:
                                line = line.strip()
                                if "TWITTER_TEXT:" in line:
                                    # Extract content after "TWITTER_TEXT:"
                                    twitter_content = line.split("TWITTER_TEXT:", 1)[1].strip()
                                    break
                            
                            if twitter_content:
                                results["twitter_text"] = twitter_content
                                logger.log_info(f"Extracted Twitter text: {len(twitter_content)} characters")
                except Exception as e:
                    logger.log_warning(f"Failed to extract chat text: {e}")

                # Enhanced artifact detection
                try:
                    # Look for various chart/visualization elements
                    artifact_selectors = [
                        "canvas",
                        "svg", 
                        "[data-testid*='chart']",
                        "[class*='chart']",
                        "[class*='visualization']",
                        "[class*='graph']",
                        ".recharts-wrapper",
                        ".plotly",
                        ".highcharts-container",
                        "iframe[src*='chart']",
                        "iframe[src*='visualization']"
                    ]
                    
                    artifacts_found = 0
                    for selector in artifact_selectors:
                        try:
                            if selector.startswith('[') or selector.startswith('.'):
                                elements = automation.driver.find_elements("css selector", selector)
                            else:
                                elements = automation.driver.find_elements("tag name", selector)
                            
                            for element in elements:
                                try:
                                    if element.is_displayed() and element.size['width'] > 50 and element.size['height'] > 50:
                                        artifact_info = {
                                            "type": "visualization",
                                            "tag": element.tag_name,
                                            "selector": selector,
                                            "size": element.size,
                                            "location": element.location
                                        }
                                        results["artifacts"].append(artifact_info)
                                        artifacts_found += 1
                                except:
                                    continue
                        except:
                            continue

                    logger.log_info(f"Found {artifacts_found} artifacts using enhanced detection")
                except Exception as e:
                    logger.log_warning(f"Failed to capture artifacts: {e}")
                
                return results
                
            except Exception as e:
                logger.log_error(f"Failed to capture results: {e}")
                return {
                    "timestamp": datetime.now().isoformat(),
                    "chat_url": automation.driver.current_url if automation.driver else "",
                    "response_text": "",
                    "screenshots": [],
                    "artifacts": [],
                    "response_metadata": {"error": str(e)}
                }
        
        # Replace the slow method with the fast one
        automation.capture_results = fast_capture_results
        
        # Run analysis with longer timeout for charts
        analysis_results = automation.run_analysis(custom_prompt, response_timeout=600)  # 10 minutes
        
        if not analysis_results.get("success", False):
            logger.log_error("❌ Analysis failed!")
            return {
                "success": False,
                "error": "Analysis failed",
                "analysis_results": analysis_results
            }
        
        logger.log_success("✅ Analysis completed successfully!")
        
        # Step 2: Twitter posting (if enabled)
        twitter_results = None
        if post_to_twitter:
            logger.log_info("🐦 Starting Twitter posting...")
            
            try:
                poster = TwitterPoster()
                twitter_results = poster.post_from_analysis(analysis_results)
                
                if twitter_results.get("success", False):
                    logger.log_success("✅ Tweet posted successfully!")
                    logger.log_info(f"📱 Tweet ID: {twitter_results['tweet_id']}")
                    
                    # Log Twitter post data
                    twitter_log_data = {
                        "timestamp": datetime.now().isoformat(),
                        "tweet_id": twitter_results['tweet_id'],
                        "tweet_content": twitter_results.get("tweet_data", {}).get("content", ""),
                        "image_path": twitter_results.get("tweet_data", {}).get("image", ""),
                        "analysis_prompt": custom_prompt,
                        "analysis_url": analysis_results.get("data", {}).get("chat_url", ""),
                        "success": True
                    }
                    
                    # Save to Twitter posts log
                    twitter_log_file = f"logs/twitter_posts_{datetime.now().strftime('%Y%m%d')}.jsonl"
                    with open(twitter_log_file, 'a', encoding='utf-8') as f:
                        f.write(json.dumps(twitter_log_data, ensure_ascii=False) + '\n')
                    
                    logger.log_info(f"📝 Twitter post logged to: {twitter_log_file}")
                    
                else:
                    logger.log_warning(f"⚠️ Twitter posting failed: {twitter_results.get('error', 'Unknown error')}")
                    
                    # Log failed Twitter post
                    twitter_log_data = {
                        "timestamp": datetime.now().isoformat(),
                        "tweet_id": None,
                        "tweet_content": "",
                        "image_path": "",
                        "analysis_prompt": custom_prompt,
                        "analysis_url": analysis_results.get("data", {}).get("chat_url", ""),
                        "success": False,
                        "error": twitter_results.get('error', 'Unknown error')
                    }
                    
                    twitter_log_file = f"logs/twitter_posts_{datetime.now().strftime('%Y%m%d')}.jsonl"
                    with open(twitter_log_file, 'a', encoding='utf-8') as f:
                        f.write(json.dumps(twitter_log_data, ensure_ascii=False) + '\n')
                    
            except Exception as e:
                logger.log_error(f"❌ Twitter posting error: {e}")
                twitter_results = {
                    "success": False,
                    "error": str(e)
                }
                
                # Log error
                twitter_log_data = {
                    "timestamp": datetime.now().isoformat(),
                    "tweet_id": None,
                    "tweet_content": "",
                    "image_path": "",
                    "analysis_prompt": custom_prompt,
                    "analysis_url": analysis_results.get("data", {}).get("chat_url", ""),
                    "success": False,
                    "error": str(e)
                }
                
                twitter_log_file = f"logs/twitter_posts_{datetime.now().strftime('%Y%m%d')}.jsonl"
                with open(twitter_log_file, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(twitter_log_data, ensure_ascii=False) + '\n')
        else:
            logger.log_info("⏭️ Twitter posting skipped")
        
        # Step 3: Summary
        logger.log_info("📋 Workflow Summary:")
        
        # Analysis summary
        data = analysis_results.get("data", {})
        response_length = len(data.get("response_text", ""))
        artifacts_count = len(data.get("artifacts", []))
        screenshots_count = len(data.get("screenshots", []))
        
        print(f"\n📊 Analysis Results:")
        print(f"  Response Length: {response_length} characters")
        print(f"  Artifacts Found: {artifacts_count}")
        print(f"  Screenshots Taken: {screenshots_count}")
        
        if response_length > 0:
            print(f"\n📝 Response Preview:")
            response_text = data.get("response_text", "")
            preview = response_text[:200] + "..." if len(response_text) > 200 else response_text
            print(f"  {preview}")
        
        # Twitter summary
        if twitter_results:
            print(f"\n🐦 Twitter Results:")
            if twitter_results.get("success", False):
                print(f"  Status: ✅ Posted successfully")
                print(f"  Tweet ID: {twitter_results['tweet_id']}")
                tweet_content = twitter_results.get("tweet_data", {}).get("content", "")
                if tweet_content:
                    print(f"  Content: {tweet_content[:100]}...")
            else:
                print(f"  Status: ❌ Failed")
                print(f"  Error: {twitter_results.get('error', 'Unknown error')}")
        
        return {
            "success": True,
            "analysis_results": analysis_results,
            "twitter_results": twitter_results,
            "timestamp": datetime.now().isoformat()
        }
        
    except KeyboardInterrupt:
        logger.log_warning("Workflow interrupted by user")
        return {
            "success": False,
            "error": "Interrupted by user"
        }
        
    except Exception as e:
        logger.log_error(f"Unexpected error: {e}")
        return {
            "success": False,
            "error": str(e)
        }
        
    finally:
        print("\n🏁 Full workflow completed")


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Run Flipside AI + Twitter workflow",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with default prompt
  python run_full_workflow.py
  
  # Run with custom prompt
  python run_full_workflow.py --prompt "Analyze Bitcoin price trends over the last 6 months"
  
  # Run without Twitter posting
  python run_full_workflow.py --no-twitter
  
  # Run with debug mode
  python run_full_workflow.py --debug
  
  # Run with custom prompt and no Twitter
  python run_full_workflow.py --prompt "Compare Ethereum vs Solana DeFi volumes" --no-twitter
        """
    )
    
    parser.add_argument("--prompt", "-p", 
                       help="Custom analysis prompt (default: USDT vs USDC supply analysis)")
    parser.add_argument("--no-twitter", action="store_true", 
                       help="Skip Twitter posting (analysis only)")
    parser.add_argument("--debug", action="store_true", 
                       help="Enable debug mode for verbose logging")
    
    args = parser.parse_args()
    
    # Set debug mode
    if args.debug:
        os.environ["DEBUG_MODE"] = "true"
        print("🐛 Debug mode enabled")
    
    # Show what we're running
    print("🚀 Starting Flipside AI + Twitter Workflow")
    print("=" * 50)
    
    if args.prompt:
        print(f"📝 Custom Prompt: {args.prompt}")
    else:
        print("📝 Using Default Prompt: USDT vs USDC supply analysis")
    
    if args.no_twitter:
        print("⏭️  Twitter posting: DISABLED")
    else:
        print("🐦 Twitter posting: ENABLED")
    
    print()
    
    # Run workflow
    result = run_full_workflow(
        custom_prompt=args.prompt,
        post_to_twitter=not args.no_twitter
    )
    
    # Exit with appropriate code
    sys.exit(0 if result.get("success", False) else 1)


if __name__ == "__main__":
    main()
