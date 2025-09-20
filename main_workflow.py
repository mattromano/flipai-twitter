#!/usr/bin/env python3
"""
Main Workflow Script

Orchestrates the complete Flipside AI + Twitter automation workflow.
This is the single entry point for all automation tasks.
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  python-dotenv not installed. Install with: pip install python-dotenv")

# Add modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

from chat_manager import FlipsideChatManager
from twitter_manager import TwitterPoster, TweetPreviewGenerator
from shared import AutomationLogger, PromptSelector


class MainWorkflow:
    """Main workflow orchestrator."""
    
    def __init__(self):
        self.logger = AutomationLogger()
        self.chat_manager = FlipsideChatManager()
        self.twitter_poster = None  # Initialize only when needed
        self.tweet_preview = TweetPreviewGenerator()
        self.prompt_selector = PromptSelector()
    
    def run_analysis_only(self, prompt: str, timeout: int = 600) -> dict:
        """Run analysis workflow only (no Twitter posting)."""
        try:
            self.logger.log_info("🚀 Starting Flipside AI Analysis Workflow")
            self.logger.log_info("=" * 60)
            
            # Run the complete analysis workflow with all features
            analysis_result = self.chat_manager.run_analysis(prompt, timeout)
            
            if analysis_result["success"]:
                # Save results
                self._save_analysis_results(analysis_result["data"], prompt)
                
                self.logger.log_success("✅ Analysis workflow completed successfully!")
                return {
                    "success": True,
                    "data": analysis_result["data"],
                    "timestamp": datetime.now().isoformat()
                }
            else:
                self.logger.log_error(f"❌ Analysis failed: {analysis_result.get('error', 'Unknown error')}")
                return {"success": False, "error": analysis_result.get('error', 'Unknown error')}
            
        except Exception as e:
            self.logger.log_error(f"Analysis workflow failed: {e}")
            return {"success": False, "error": str(e)}
    
    def run_full_workflow(self, prompt: str, timeout: int = 600, post_to_twitter: bool = True, test_mode: bool = False) -> dict:
        """Run complete workflow: analysis + Twitter posting."""
        try:
            self.logger.log_info("🚀 Starting Complete Flipside AI + Twitter Workflow")
            self.logger.log_info("=" * 60)
            
            # Step 1: Run analysis
            analysis_result = self.run_analysis_only(prompt, timeout)
            
            if not analysis_result.get("success", False):
                return analysis_result
            
            # Step 2: Generate tweet preview
            self.logger.log_info("🐦 Generating tweet preview...")
            tweet_data = self.tweet_preview.create_tweet_preview(analysis_result)
            
            if tweet_data:
                json_file, html_file, md_file = self.tweet_preview.save_tweet_preview(
                    tweet_data, f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                )
                self.logger.log_success(f"✅ Tweet preview generated: {json_file}")
            
            # Step 3: Post to Twitter (if enabled)
            twitter_result = None
            if post_to_twitter:
                if test_mode:
                    self.logger.log_info("🐦 Creating Twitter preview (test mode)...")
                else:
                    self.logger.log_info("🐦 Posting to Twitter...")
                
                # Initialize Twitter poster only when needed
                if not self.twitter_poster:
                    self.twitter_poster = TwitterPoster()
                
                if test_mode:
                    # Create preview without posting
                    twitter_result = self.twitter_poster.create_tweet_preview(analysis_result)
                    if twitter_result.get("success", False):
                        self.logger.log_success("✅ Tweet preview created successfully")
                        self._print_tweet_preview(twitter_result)
                    else:
                        self.logger.log_warning(f"⚠️ Tweet preview failed: {twitter_result.get('error', 'Unknown error')}")
                else:
                    # Actually post to Twitter
                    twitter_result = self.twitter_poster.post_from_analysis(analysis_result, test_mode=False)
                    if twitter_result.get("success", False):
                        self.logger.log_success(f"✅ Tweet posted successfully: {twitter_result['tweet_id']}")
                        
                        # Post follow-up reply with analysis link
                        original_tweet_id = twitter_result.get('tweet_id')
                        if original_tweet_id:
                            self.logger.log_info("🔗 Posting follow-up reply with analysis link...")
                            reply_result = self.twitter_poster.post_analysis_link_reply(original_tweet_id, analysis_result)
                            if reply_result.get("success", False):
                                self.logger.log_success(f"✅ Analysis link reply posted: {reply_result['tweet_id']}")
                                twitter_result['reply_result'] = reply_result
                            else:
                                self.logger.log_warning(f"⚠️ Analysis link reply failed: {reply_result.get('error', 'Unknown error')}")
                    else:
                        self.logger.log_warning(f"⚠️ Twitter posting failed: {twitter_result.get('error', 'Unknown error')}")
            else:
                self.logger.log_info("⏭️ Twitter posting skipped")
            
            # Step 4: Summary
            self._print_workflow_summary(analysis_result, twitter_result)
            
            return {
                "success": True,
                "analysis_result": analysis_result,
                "twitter_result": twitter_result,
                "tweet_preview": tweet_data,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.log_error(f"Full workflow failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _save_analysis_results(self, analysis_data: dict, prompt: str):
        """Save analysis results to file."""
        try:
            # Create logs directory
            os.makedirs("logs", exist_ok=True)
            
            # Prepare results
            results = {
                "timestamp": datetime.now().isoformat(),
                "prompt": prompt,
                "data": analysis_data
            }
            
            # Save to file
            filename = f"logs/analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            self.logger.log_success(f"📝 Analysis results saved: {filename}")
            
        except Exception as e:
            self.logger.log_error(f"Failed to save analysis results: {e}")
    
    def _print_workflow_summary(self, analysis_result: dict, twitter_result: dict = None):
        """Print workflow summary."""
        try:
            self.logger.log_info("\n📋 Workflow Summary:")
            self.logger.log_info("=" * 50)
            
            # Analysis summary
            data = analysis_result.get("data", {})
            response_length = len(data.get("response_text", ""))
            artifacts_count = len(data.get("artifacts", []))
            screenshots_count = len(data.get("screenshots", []))
            
            self.logger.log_info(f"📊 Analysis Results:")
            self.logger.log_info(f"  Response Length: {response_length} characters")
            self.logger.log_info(f"  Artifacts Found: {artifacts_count}")
            self.logger.log_info(f"  Screenshots Taken: {screenshots_count}")
            
            if response_length > 0:
                self.logger.log_info(f"\n📝 Response Preview:")
                response_text = data.get("response_text", "")
                preview = response_text[:200] + "..." if len(response_text) > 200 else response_text
                self.logger.log_info(f"  {preview}")
            
            # Twitter summary
            if twitter_result:
                self.logger.log_info(f"\n🐦 Twitter Results:")
                if twitter_result.get("success", False):
                    self.logger.log_info(f"  Status: ✅ Posted successfully")
                    self.logger.log_info(f"  Tweet ID: {twitter_result['tweet_id']}")
                    tweet_content = twitter_result.get("text", "")
                    if tweet_content:
                        self.logger.log_info(f"  Content: {tweet_content[:100]}...")
                else:
                    self.logger.log_info(f"  Status: ❌ Failed")
                    self.logger.log_info(f"  Error: {twitter_result.get('error', 'Unknown error')}")
            
        except Exception as e:
            self.logger.log_error(f"Failed to print summary: {e}")
    
    def _print_tweet_preview(self, preview_data: dict):
        """Print tweet preview information."""
        try:
            self.logger.log_info("\n🐦 Tweet Preview:")
            self.logger.log_info("=" * 50)
            
            tweet_content = preview_data.get("tweet_content", "")
            image_path = preview_data.get("image_path", "")
            chat_url = preview_data.get("chat_url", "")
            character_count = preview_data.get("character_count", 0)
            has_image = preview_data.get("has_image", False)
            image_exists = preview_data.get("image_exists", False)
            
            self.logger.log_info(f"📝 Tweet Content ({character_count}/280 characters):")
            self.logger.log_info(f"  {tweet_content}")
            
            if has_image:
                if image_exists:
                    self.logger.log_info(f"📸 Image: {image_path} ✅")
                else:
                    self.logger.log_info(f"📸 Image: {image_path} ❌ (file not found)")
            else:
                self.logger.log_info("📸 Image: None")
            
            if chat_url:
                self.logger.log_info(f"🔗 Chat URL: {chat_url}")
            
        except Exception as e:
            self.logger.log_error(f"Failed to print tweet preview: {e}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Flipside AI + Twitter Automation Workflow",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run analysis only with custom prompt
  python main_workflow.py --prompt "Analyze Bitcoin trends" --analysis-only

  # Run full workflow with Twitter posting
  python main_workflow.py --prompt "Compare DeFi protocols"

  # Select random prompt
  python main_workflow.py --random-prompt

  # Select random prompt from specific category
  python main_workflow.py --random-prompt --category "DeFi Ecosystem Health"

  # Select random prompt by difficulty
  python main_workflow.py --random-prompt --difficulty intermediate

  # Run with custom timeout
  python main_workflow.py --prompt "Complex analysis" --timeout 900

  # Run without Twitter posting
  python main_workflow.py --prompt "Analysis only" --no-twitter

  # Test Twitter posting (preview only, no API call)
  python main_workflow.py --prompt "Test tweet" --test-mode

  # Show prompt usage statistics
  python main_workflow.py --stats
        """
    )
    
    # Prompt selection arguments
    prompt_group = parser.add_mutually_exclusive_group()
    prompt_group.add_argument("--prompt", "-p",
                             help="Analysis prompt")
    prompt_group.add_argument("--random-prompt", action="store_true",
                             help="Select a random prompt from the prompts file")
    
    parser.add_argument("--category", type=str,
                       help="Filter prompts by category (use with --random-prompt)")
    parser.add_argument("--difficulty", type=str, choices=["easy", "mild_intermediate", "intermediate", "advanced"],
                       help="Filter prompts by difficulty (use with --random-prompt)")
    parser.add_argument("--analysis-only", action="store_true",
                       help="Run analysis only (no Twitter posting)")
    parser.add_argument("--no-twitter", action="store_true",
                       help="Skip Twitter posting")
    parser.add_argument("--test-mode", action="store_true",
                       help="Test mode: create tweet preview without posting to Twitter API")
    parser.add_argument("--timeout", "-t", type=int, default=600,
                       help="Response timeout in seconds (default: 600)")
    parser.add_argument("--debug", action="store_true",
                       help="Enable debug mode")
    parser.add_argument("--stats", action="store_true",
                       help="Show prompt usage statistics and exit")
    
    args = parser.parse_args()
    
    # Set debug mode
    if args.debug:
        os.environ["DEBUG_MODE"] = "true"
        print("🐛 Debug mode enabled")
    
    # Handle stats display
    if args.stats:
        workflow = MainWorkflow()
        stats = workflow.prompt_selector.get_usage_stats()
        print("\n📊 Prompt Usage Statistics")
        print("=" * 40)
        print(f"Total Prompts: {stats['total_prompts']}")
        print(f"Used Prompts: {stats['used_prompts']}")
        print(f"Available Prompts: {stats['available_prompts']}")
        print(f"Usage Percentage: {stats['usage_percentage']:.1f}%")
        print(f"Total Runs: {stats['total_runs']}")
        if stats['last_reset']:
            print(f"Last Reset: {stats['last_reset']}")
        print(f"\nAvailable Categories: {', '.join(stats['categories_available'])}")
        print(f"Available Difficulties: {', '.join(stats['difficulty_levels_available'])}")
        sys.exit(0)
    
    # Validate that either prompt or random-prompt is provided
    if not args.prompt and not args.random_prompt:
        parser.error("Either --prompt or --random-prompt must be provided")
    
    # Determine the prompt to use
    workflow = MainWorkflow()
    prompt_to_use = None
    selected_prompt_info = None
    
    if args.prompt:
        prompt_to_use = args.prompt
        print("📝 Using provided prompt")
    elif args.random_prompt:
        selected_prompt_info = workflow.prompt_selector.select_and_mark_prompt(
            category_filter=args.category,
            difficulty_filter=args.difficulty
        )
        
        if selected_prompt_info:
            prompt_to_use = selected_prompt_info["prompt"]
            print(f"🎯 Selected random prompt (ID: {selected_prompt_info['id']})")
            print(f"📂 Category: {selected_prompt_info['category']}")
            print(f"📊 Difficulty: {selected_prompt_info['difficulty']}")
        else:
            print("❌ No available prompts found with the specified criteria")
            sys.exit(1)
    
    # Show what we're running
    print("🚀 Flipside AI + Twitter Automation")
    print("=" * 50)
    print(f"📝 Prompt: {prompt_to_use[:100]}{'...' if len(prompt_to_use) > 100 else ''}")
    print(f"⏱️  Timeout: {args.timeout} seconds")
    
    if args.analysis_only:
        print("📊 Mode: Analysis only")
    elif args.no_twitter:
        print("🐦 Mode: Analysis + Preview (no Twitter posting)")
    elif args.test_mode:
        print("🐦 Mode: Analysis + Twitter Test (preview only)")
    else:
        print("🐦 Mode: Full workflow (Analysis + Twitter)")
    
    print()
    
    # Run workflow
    try:
        if args.analysis_only:
            result = workflow.run_analysis_only(prompt_to_use, args.timeout)
        else:
            result = workflow.run_full_workflow(
                prompt_to_use, 
                args.timeout, 
                post_to_twitter=not args.no_twitter,
                test_mode=args.test_mode
            )
        
        # Log the selected prompt info if using random selection
        if selected_prompt_info:
            workflow.logger.log_info(f"Used prompt ID {selected_prompt_info['id']}: {selected_prompt_info['category']} - {selected_prompt_info['difficulty']}")
        
        # Exit with appropriate code
        sys.exit(0 if result.get("success", False) else 1)
        
    except KeyboardInterrupt:
        print("\n⚠️ Workflow interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
