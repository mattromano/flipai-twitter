#!/usr/bin/env python3
"""
Analyze the page structure to understand where the chat response is located.
"""

import os
import sys
import time
import logging
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.chat_automation_robust import RobustFlipsideChatAutomation
from src.automation_logger import setup_automation_logging

def setup_error_logging():
    """Set up error logging to a specific file."""
    error_logger = logging.getLogger('error_logger')
    error_logger.setLevel(logging.ERROR)
    
    # Create error log file
    error_log_file = f"logs/error_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    os.makedirs("logs", exist_ok=True)
    
    handler = logging.FileHandler(error_log_file)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    error_logger.addHandler(handler)
    
    return error_logger, error_log_file

def analyze_page_structure():
    """Analyze the page structure to find the chat response."""
    # Setup logging
    automation_logger = setup_automation_logger(debug_mode=True)
    
    automation_logger.log_info("Starting page structure analysis...")
    
    automation = RobustFlipsideChatAutomation()
    
    try:
        # Setup WebDriver
        automation_logger.log_info("Setting up Chrome WebDriver...")
        if not automation.setup_chrome_driver():
            raise Exception("Failed to setup Chrome driver")
        
        # Setup session
        automation_logger.log_info("Setting up session...")
        if not automation.setup_session_with_timeout(60):
            raise Exception("Failed to setup session")
        
        # Navigate to the specific chat URL
        target_url = "https://flipsidecrypto.xyz/chat/ba2e61e8-329c-4410-9d3d-cffdbe5417e1"
        automation_logger.log_info(f"Navigating to: {target_url}")
        automation.driver.get(target_url)
        
        # Wait for page to load
        time.sleep(10)  # Wait longer for everything to load
        automation_logger.log_success("Page loaded")
        
        # Take screenshot
        screenshot_path = automation.driver.save_screenshot(f"screenshots/analysis_page_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        automation_logger.log_info(f"Screenshot saved: {screenshot_path}")
        
        # Get page source for analysis
        page_source = automation.driver.page_source
        source_file = f"logs/page_source_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        with open(source_file, 'w', encoding='utf-8') as f:
            f.write(page_source)
        automation_logger.log_info(f"Page source saved to: {source_file}")
        
        # Analyze different sections of the page
        automation_logger.log_info("Analyzing page structure...")
        
        # Get all divs and analyze their content
        divs = automation.driver.find_elements("css selector", "div")
        automation_logger.log_info(f"Found {len(divs)} div elements")
        
        # Look for divs with substantial text content
        substantial_divs = []
        for i, div in enumerate(divs):
            try:
                if div.is_displayed():
                    text = div.text.strip()
                    if len(text) > 50:  # Look for substantial content
                        substantial_divs.append({
                            'index': i,
                            'text_length': len(text),
                            'text_preview': text[:100],
                            'class': div.get_attribute('class') or '',
                            'id': div.get_attribute('id') or '',
                            'data_testid': div.get_attribute('data-testid') or ''
                        })
            except:
                continue
        
        # Sort by text length
        substantial_divs.sort(key=lambda x: x['text_length'], reverse=True)
        
        automation_logger.log_info(f"Found {len(substantial_divs)} substantial divs")
        
        # Log the top 10 substantial divs
        for i, div_info in enumerate(substantial_divs[:10]):
            automation_logger.log_info(f"Div {i+1}: {div_info['text_length']} chars, class='{div_info['class'][:50]}', id='{div_info['id']}', data-testid='{div_info['data_testid']}'")
            automation_logger.log_info(f"  Preview: {div_info['text_preview']}...")
        
        # Look for specific elements that might contain the response
        automation_logger.log_info("Looking for specific response elements...")
        
        # Check for elements with specific classes or attributes
        response_selectors = [
            '[data-testid*="message"]',
            '[data-testid*="response"]',
            '[data-testid*="content"]',
            '[data-testid*="chat"]',
            '[class*="message"]',
            '[class*="response"]',
            '[class*="content"]',
            '[class*="chat"]',
            '[class*="prose"]',
            '[class*="markdown"]',
            'main',
            'article',
            'section'
        ]
        
        for selector in response_selectors:
            try:
                elements = automation.driver.find_elements("css selector", selector)
                automation_logger.log_info(f"Selector '{selector}': {len(elements)} elements")
                
                for i, element in enumerate(elements):
                    if element.is_displayed():
                        text = element.text.strip()
                        if len(text) > 100:
                            automation_logger.log_info(f"  Element {i}: {len(text)} chars - {text[:100]}...")
            except Exception as e:
                automation_logger.log_warning(f"Error with selector '{selector}': {e}")
        
        # Look for any text that contains our keywords
        automation_logger.log_info("Searching for keyword matches...")
        page_text = automation.driver.find_element("tag name", "body").text
        lines = page_text.split('\n')
        
        keyword_matches = []
        for i, line in enumerate(lines):
            line = line.strip()
            if any(keyword in line.lower() for keyword in [
                'compound', 'aave', 'lending', 'ethereum', 'market', 'analysis',
                'defi', 'protocol', 'tvl', 'borrowing', 'interest', 'rate',
                'comparison', 'since 2019', 'growth', 'adoption', 'tvl'
            ]):
                keyword_matches.append({
                    'line_number': i,
                    'text': line,
                    'length': len(line)
                })
        
        automation_logger.log_info(f"Found {len(keyword_matches)} lines with keywords")
        for match in keyword_matches[:10]:  # Show first 10 matches
            automation_logger.log_info(f"  Line {match['line_number']}: {match['text']}")
        
        # Save analysis results
        analysis_file = f"logs/page_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(analysis_file, 'w', encoding='utf-8') as f:
            f.write("PAGE STRUCTURE ANALYSIS\n")
            f.write("=" * 50 + "\n\n")
            
            f.write(f"Total divs: {len(divs)}\n")
            f.write(f"Substantial divs: {len(substantial_divs)}\n")
            f.write(f"Keyword matches: {len(keyword_matches)}\n\n")
            
            f.write("TOP SUBSTANTIAL DIVS:\n")
            f.write("-" * 30 + "\n")
            for i, div_info in enumerate(substantial_divs[:10]):
                f.write(f"{i+1}. {div_info['text_length']} chars\n")
                f.write(f"   Class: {div_info['class']}\n")
                f.write(f"   ID: {div_info['id']}\n")
                f.write(f"   Data-testid: {div_info['data_testid']}\n")
                f.write(f"   Preview: {div_info['text_preview']}\n\n")
            
            f.write("KEYWORD MATCHES:\n")
            f.write("-" * 30 + "\n")
            for match in keyword_matches:
                f.write(f"Line {match['line_number']}: {match['text']}\n")
        
        automation_logger.log_success(f"Analysis saved to: {analysis_file}")
        
        return {
            "success": True,
            "total_divs": len(divs),
            "substantial_divs": len(substantial_divs),
            "keyword_matches": len(keyword_matches),
            "analysis_file": analysis_file,
            "page_source_file": source_file,
            "screenshot": screenshot_path
        }
        
    except Exception as e:
        automation_logger.log_error(f"Analysis failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }
    
    finally:
        if automation.driver:
            try:
                automation.driver.quit()
                automation_logger.log_info("WebDriver cleanup complete")
            except Exception as e:
                automation_logger.log_warning(f"Error during WebDriver cleanup: {e}")

if __name__ == "__main__":
    try:
        results = analyze_page_structure()
        if results["success"]:
            print("✅ Analysis completed successfully!")
            print(f"Total divs: {results['total_divs']}")
            print(f"Substantial divs: {results['substantial_divs']}")
            print(f"Keyword matches: {results['keyword_matches']}")
            print(f"Analysis saved to: {results['analysis_file']}")
        else:
            print(f"❌ Analysis failed: {results['error']}")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        sys.exit(1)
