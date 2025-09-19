#!/usr/bin/env python3
"""
Simplified workflow script that uses cookie-based authentication.
This version focuses on reliability and provides clear error messages.
"""

import os
import sys
import argparse
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.chat_automation_robust import ChatAutomationRobust
from src.automation_logger import AutomationLogger
from src.session_manager_simple import SimpleSessionManager
from twitter_poster import TwitterPoster

def main():
    """Main workflow function."""
    parser = argparse.ArgumentParser(description='Run Flipside AI + Twitter Workflow (Simplified)')
    parser.add_argument('--prompt', required=True, help='The prompt to send to Flipside AI')
    parser.add_argument('--no-twitter', action='store_true', help='Skip Twitter posting')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    # Set up logging
    if args.debug:
        os.environ['DEBUG_MODE'] = 'true'
    
    logger = AutomationLogger()
    
    print("🚀 Starting Flipside AI + Twitter Workflow (Simplified)")
    print("=" * 60)
    print(f"📝 Custom Prompt: {args.prompt}")
    print(f"🐦 Twitter posting: {'DISABLED' if args.no_twitter else 'ENABLED'}")
    print()
    
    try:
        # Initialize automation
        automation = ChatAutomationRobust()
        
        # Set up session with simple manager
        logger.log_info("Setting up session with simple cookie-based authentication")
        
        if not automation.setup_webdriver():
            logger.log_error("Failed to setup WebDriver")
            return False
        
        # Use simple session manager
        session_manager = SimpleSessionManager(automation.driver)
        
        if not session_manager.setup_session():
            logger.log_error("❌ Session setup failed!")
            print("\n" + "="*60)
            print("🔧 TROUBLESHOOTING STEPS:")
            print("="*60)
            print("1. Run the cookie generator script:")
            print("   python generate_fresh_cookies.py")
            print()
            print("2. Follow the instructions to log in manually")
            print("3. The script will save fresh cookies for automation")
            print("4. Run this workflow again")
            print()
            print("💡 This is a one-time setup - cookies will work for future runs")
            print("="*60)
            return False
        
        logger.log_success("✅ Session setup successful")
        
        # Run the analysis
        logger.log_info("Starting Flipside AI analysis")
        results = automation.run_analysis(args.prompt)
        
        if not results:
            logger.log_error("❌ Analysis failed")
            return False
        
        logger.log_success("✅ Analysis completed successfully")
        
        # Post to Twitter if enabled
        if not args.no_twitter:
            logger.log_info("Posting to Twitter")
            
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
        print("📊 WORKFLOW SUMMARY")
        print("="*60)
        print(f"⏱️  Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📝 Prompt: {args.prompt}")
        print(f"🔗 Chat URL: {results.get('chat_url', 'Not available')}")
        print(f"📊 Screenshots: {len(results.get('screenshots', []))}")
        print(f"📈 Charts: {len(results.get('artifacts', []))}")
        
        if not args.no_twitter and 'tweet_result' in locals():
            print(f"🐦 Twitter: {'✅ Posted' if tweet_result.get('success') else '❌ Failed'}")
        
        print("="*60)
        
        return True
        
    except Exception as e:
        logger.log_error(f"Workflow failed: {e}")
        print(f"\n❌ Workflow failed: {e}")
        return False
    
    finally:
        # Cleanup
        try:
            if 'automation' in locals():
                automation.cleanup()
        except:
            pass

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
