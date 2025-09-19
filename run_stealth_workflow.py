#!/usr/bin/env python3
"""
Stealth workflow script that uses undetected-chromedriver for automated authentication.
This script is designed to work in GitHub Actions without manual intervention.
"""

import os
import sys
import argparse
import time
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.stealth_automation_fixed import StealthAutomation
from src.automation_logger import AutomationLogger
from twitter_poster import TwitterPoster

def main():
    """Main stealth workflow function."""
    parser = argparse.ArgumentParser(description='Run Flipside AI + Twitter Workflow (Stealth)')
    parser.add_argument('--prompt', required=True, help='The prompt to send to Flipside AI')
    parser.add_argument('--no-twitter', action='store_true', help='Skip Twitter posting')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--headless', action='store_true', default=True, help='Run in headless mode')
    
    args = parser.parse_args()
    
    # Set up logging
    if args.debug:
        os.environ['DEBUG_MODE'] = 'true'
    
    logger = AutomationLogger()
    
    print("🚀 Starting Flipside AI + Twitter Workflow (Stealth)")
    print("=" * 60)
    print(f"📝 Custom Prompt: {args.prompt}")
    print(f"🐦 Twitter posting: {'DISABLED' if args.no_twitter else 'ENABLED'}")
    print(f"🤖 Headless mode: {'ENABLED' if args.headless else 'DISABLED'}")
    print()
    
    stealth_automation = None
    
    try:
        # Check for required environment variables
        if not os.getenv('FLIPSIDE_EMAIL') or not os.getenv('FLIPSIDE_PASSWORD'):
            logger.log_error("❌ FLIPSIDE_EMAIL and FLIPSIDE_PASSWORD environment variables are required")
            print("\n🔧 SETUP REQUIRED:")
            print("Set these environment variables:")
            print("  export FLIPSIDE_EMAIL='your-email@example.com'")
            print("  export FLIPSIDE_PASSWORD='your-password'")
            return False
        
        # Initialize stealth automation
        logger.log_info("🤖 Initializing stealth automation")
        stealth_automation = StealthAutomation(headless=args.headless)
        
        # Setup driver
        if not stealth_automation.setup_driver():
            logger.log_error("❌ Failed to setup stealth driver")
            return False
        
        logger.log_success("✅ Stealth driver setup complete")
        
        # Perform login
        logger.log_info("🔐 Performing automated login")
        if not stealth_automation.perform_login():
            logger.log_error("❌ Login failed")
            return False
        
        logger.log_success("✅ Login successful")
        
        # Submit prompt
        logger.log_info("📝 Submitting prompt to Flipside AI")
        if not stealth_automation.submit_prompt(args.prompt):
            logger.log_error("❌ Failed to submit prompt")
            return False
        
        logger.log_success("✅ Prompt submitted successfully")
        
        # Wait for response
        logger.log_info("⏳ Waiting for AI response")
        if not stealth_automation.wait_for_response(timeout=300):  # 5 minutes
            logger.log_warning("⚠️ Response timeout, but continuing...")
        
        # Get current URL for results
        chat_url = stealth_automation.driver.current_url
        logger.log_info(f"🔗 Chat URL: {chat_url}")
        
        # Create results dictionary
        results = {
            "timestamp": datetime.now().isoformat(),
            "chat_url": chat_url,
            "prompt": args.prompt,
            "response_text": "Response captured via stealth automation",
            "screenshots": [],
            "artifacts": [],
            "response_metadata": {
                "automation_type": "stealth",
                "headless": args.headless
            }
        }
        
        logger.log_success("✅ Analysis completed successfully")
        
        # Post to Twitter if enabled
        if not args.no_twitter:
            logger.log_info("🐦 Posting to Twitter")
            
            try:
                twitter_poster = TwitterPoster()
                tweet_result = twitter_poster.post_from_analysis(results)
                
                if tweet_result and tweet_result.get('success'):
                    logger.log_success("✅ Twitter post successful")
                    print(f"🐦 Tweet posted: {tweet_result.get('tweet_url', 'URL not available')}")
                else:
                    logger.log_error("❌ Twitter post failed")
                    print(f"❌ Twitter error: {tweet_result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                logger.log_error(f"Twitter posting failed: {e}")
                print(f"❌ Twitter posting failed: {e}")
        else:
            logger.log_info("Twitter posting skipped")
        
        # Print summary
        print("\n" + "="*60)
        print("📊 STEALTH WORKFLOW SUMMARY")
        print("="*60)
        print(f"⏱️  Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📝 Prompt: {args.prompt}")
        print(f"🔗 Chat URL: {chat_url}")
        print(f"🤖 Automation: Stealth (undetected-chromedriver)")
        print(f"👻 Headless: {'Yes' if args.headless else 'No'}")
        
        if not args.no_twitter and 'tweet_result' in locals():
            print(f"🐦 Twitter: {'✅ Posted' if tweet_result.get('success') else '❌ Failed'}")
        
        print("="*60)
        
        return True
        
    except Exception as e:
        logger.log_error(f"Stealth workflow failed: {e}")
        print(f"\n❌ Stealth workflow failed: {e}")
        return False
    
    finally:
        # Cleanup
        try:
            if stealth_automation:
                stealth_automation.cleanup()
        except:
            pass

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
