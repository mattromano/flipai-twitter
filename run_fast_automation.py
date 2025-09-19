#!/usr/bin/env python3
"""
Fast version of Flipside chat automation with optimized performance.
"""

import os
import sys
import time
from datetime import datetime
from src.chat_automation_robust import RobustFlipsideChatAutomation
from src.automation_logger import setup_automation_logging

def main():
    """Run the automation with optimized performance."""
    print("🚀 Fast Flipside Chat Automation")
    print("=" * 50)
    
    # Setup logging
    debug_mode = os.getenv("DEBUG_MODE", "false").lower() == "true"
    logger = setup_automation_logging(debug_mode=debug_mode)
    
    # Initialize automation
    automation = RobustFlipsideChatAutomation()
    
    try:
        # Run the analysis with a custom prompt
        logger.log_info("Starting fast automation workflow...")
        custom_prompt = "Give me a full analysis comparing the supply of USDT and USDC across all the top blockchains"
        
        # Override the slow capture_results method with a fast version
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
                    "response_metadata": {}
                }
                
                # Quick text extraction
                try:
                    body_text = automation.driver.find_element("tag name", "body").text
                    if body_text:
                        results["response_text"] = body_text
                        logger.log_info(f"Extracted page text: {len(body_text)} characters")
                        
                        # Quick Twitter text extraction
                        if "TWITTER_TEXT" in body_text:
                            lines = body_text.split('\n')
                            twitter_content = ""
                            in_twitter_section = False
                            
                            for line in lines:
                                line = line.strip()
                                if "TWITTER_TEXT" in line:
                                    in_twitter_section = True
                                    continue
                                elif in_twitter_section:
                                    if line and not line.startswith("**") and not line.startswith("HTML_CHART"):
                                        twitter_content += line + " "
                                    elif line.startswith("HTML_CHART") or line.startswith("**"):
                                        break
                            
                            if twitter_content:
                                results["twitter_text"] = twitter_content.strip()
                                logger.log_info(f"Extracted Twitter text: {len(twitter_content)} characters")
                except Exception as e:
                    logger.log_warning(f"Failed to extract page text: {e}")
                
                # Quick artifact detection
                try:
                    canvas_elements = automation.driver.find_elements("tag name", "canvas")
                    svg_elements = automation.driver.find_elements("tag name", "svg")
                    
                    for element in canvas_elements + svg_elements:
                        if element.is_displayed() and element.size['width'] > 50 and element.size['height'] > 50:
                            artifact_info = {
                                "type": "visualization",
                                "tag": element.tag_name,
                                "size": element.size,
                                "location": element.location
                            }
                            results["artifacts"].append(artifact_info)
                    
                    logger.log_info(f"Found {len(results['artifacts'])} artifacts")
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
        
        # Run the analysis
        results = automation.run_analysis(custom_prompt)
        
        # Check results
        if results.get("success", False):
            logger.log_success("🎉 Fast automation completed successfully!")
            
            # Show results summary
            data = results.get("data", {})
            response_length = len(data.get("response_text", ""))
            artifacts_count = len(data.get("artifacts", []))
            screenshots_count = len(data.get("screenshots", []))
            
            print(f"\n📊 Results Summary:")
            print(f"  Response Length: {response_length} characters")
            print(f"  Artifacts Found: {artifacts_count}")
            print(f"  Screenshots Taken: {screenshots_count}")
            
            if response_length > 0:
                print(f"\n📝 Response Preview:")
                response_text = data.get("response_text", "")
                preview = response_text[:200] + "..." if len(response_text) > 200 else response_text
                print(f"  {preview}")
            
        else:
            logger.log_error("❌ Fast automation failed!")
            error = results.get("error", "Unknown error")
            print(f"\n🚨 Error: {error}")
            
    except KeyboardInterrupt:
        logger.log_warning("Automation interrupted by user")
        print("\n⏹️  Automation stopped by user")
        
    except Exception as e:
        logger.log_error(f"Unexpected error: {e}")
        print(f"\n💥 Unexpected error: {e}")
    
    print("\n🏁 Fast automation session ended")

if __name__ == "__main__":
    main()
