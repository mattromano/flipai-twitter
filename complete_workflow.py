#!/usr/bin/env python3
"""
Complete workflow: Extract response, get Twitter text, and generate PNG chart.
"""

import os
import sys
import time
import tempfile
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.chat_automation_robust import RobustFlipsideChatAutomation
from html_to_png_converter import create_html_to_png_converter

def extract_response_from_page_text(page_text):
    """Extract the actual response content from the full page text."""
    lines = page_text.split('\n')
    
    # Find the start of the response (after the prompt)
    response_start = -1
    for i, line in enumerate(lines):
        if 'I\'ll analyze' in line or 'Let me start' in line:
            response_start = i
            break
    
    if response_start == -1:
        return None
    
    # Extract the response content
    response_lines = []
    in_response = False
    
    for i in range(response_start, len(lines)):
        line = lines[i].strip()
        
        # Skip empty lines at the start
        if not line and not in_response:
            continue
            
        # Start collecting when we hit the actual response
        if 'I\'ll analyze' in line or 'Let me start' in line:
            in_response = True
        
        if in_response:
            # Stop at certain UI elements that indicate end of response
            if line in ['Copy message', 'Regenerate response', 'Twitter Response Formats']:
                break
            response_lines.append(line)
    
    return '\n'.join(response_lines)

def extract_twitter_text(response_text):
    """Extract the TWITTER_TEXT section from the response."""
    lines = response_text.split('\n')
    twitter_text = None
    
    for i, line in enumerate(lines):
        if 'TWITTER_TEXT:' in line:
            # Get the text after "TWITTER_TEXT:"
            twitter_text = line.split('TWITTER_TEXT:', 1)[1].strip()
            break
    
    return twitter_text

def extract_html_chart_from_response(response_text):
    """Extract the HTML chart section from the response text."""
    lines = response_text.split('\n')
    
    # Find the start of the HTML chart
    html_start = -1
    for i, line in enumerate(lines):
        if line.strip() == 'HTML_CHART:':
            html_start = i + 1
            break
    
    if html_start == -1:
        return None
    
    # Extract the HTML content
    html_lines = []
    for i in range(html_start, len(lines)):
        line = lines[i].strip()
        if line and not line.startswith('Key Findings:'):
            html_lines.append(line)
        elif line.startswith('Key Findings:'):
            break
    
    return '\n'.join(html_lines)

def complete_workflow(chat_url):
    """Complete workflow: Extract response, get Twitter text, and generate PNG chart."""
    print("🚀 Starting complete workflow...")
    
    # Setup automation
    automation = RobustFlipsideChatAutomation()
    
    try:
        # Setup WebDriver
        print("🌐 Setting up Chrome WebDriver...")
        if not automation.setup_chrome_driver():
            raise Exception("Failed to setup Chrome driver")
        
        # Setup session
        print("🍪 Setting up session...")
        if not automation.setup_session_with_timeout(60):
            raise Exception("Failed to setup session")
        
        # Navigate to the chat URL
        print(f"🧭 Navigating to: {chat_url}")
        automation.driver.get(chat_url)
        
        # Wait for page to load
        time.sleep(5)
        print("✅ Page loaded successfully")
        
        # Get the full page text
        page_text = automation.driver.find_element("tag name", "body").text
        print(f"📄 Page text length: {len(page_text)} characters")
        
        # Extract the response content
        print("🔍 Extracting response content...")
        response_text = extract_response_from_page_text(page_text)
        
        if not response_text:
            raise Exception("Failed to extract response content")
        
        print(f"✅ Response extracted: {len(response_text)} characters")
        
        # Extract Twitter text
        print("🐦 Extracting Twitter text...")
        twitter_text = extract_twitter_text(response_text)
        
        if not twitter_text:
            print("⚠️  No Twitter text found in response")
        else:
            print(f"✅ Twitter text extracted: {twitter_text}")
        
        # Extract HTML chart
        print("📊 Extracting HTML chart...")
        html_chart = extract_html_chart_from_response(response_text)
        
        if not html_chart:
            print("⚠️  No HTML chart found in response")
            png_path = None
        else:
            print(f"✅ HTML chart extracted: {len(html_chart)} characters")
            
            # Convert HTML to PNG
            print("🖼️  Converting HTML chart to PNG...")
            converter = create_html_to_png_converter()
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            png_path = f"charts/chart_{timestamp}.png"
            
            png_path = converter(html_chart, output_path=png_path, width=1200, height=800)
            
            if png_path:
                print(f"✅ PNG chart generated: {png_path}")
                if os.path.exists(png_path):
                    file_size = os.path.getsize(png_path)
                    print(f"📁 PNG file size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
            else:
                print("❌ Failed to generate PNG chart")
        
        # Save results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save full response
        response_file = f"outputs/response_{timestamp}.txt"
        os.makedirs("outputs", exist_ok=True)
        with open(response_file, 'w', encoding='utf-8') as f:
            f.write(response_text)
        print(f"💾 Response saved to: {response_file}")
        
        # Save Twitter text
        if twitter_text:
            twitter_file = f"outputs/twitter_text_{timestamp}.txt"
            with open(twitter_file, 'w', encoding='utf-8') as f:
                f.write(twitter_text)
            print(f"💾 Twitter text saved to: {twitter_file}")
        
        # Save HTML chart
        if html_chart:
            html_file = f"outputs/chart_{timestamp}.html"
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_chart)
            print(f"💾 HTML chart saved to: {html_file}")
        
        # Return results
        return {
            "success": True,
            "response_text": response_text,
            "twitter_text": twitter_text,
            "html_chart": html_chart,
            "png_path": png_path,
            "response_file": response_file,
            "twitter_file": twitter_file if twitter_text else None,
            "html_file": html_file if html_chart else None
        }
        
    except Exception as e:
        print(f"❌ Workflow failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }
    
    finally:
        if automation.driver:
            try:
                automation.driver.quit()
                print("🧹 WebDriver cleanup complete")
            except Exception as e:
                print(f"⚠️  Error during WebDriver cleanup: {e}")

def main():
    """Main function to run the complete workflow."""
    # Use the chat URL we've been testing with
    chat_url = "https://flipsidecrypto.xyz/chat/ba2e61e8-329c-4410-9d3d-cffdbe5417e1"
    
    results = complete_workflow(chat_url)
    
    if results["success"]:
        print("\n🎉 Complete workflow finished successfully!")
        print("=" * 50)
        print(f"📄 Response length: {len(results['response_text'])} characters")
        if results.get("twitter_text"):
            print(f"🐦 Twitter text: {results['twitter_text']}")
        if results.get("png_path"):
            print(f"🖼️  PNG chart: {results['png_path']}")
        print("=" * 50)
    else:
        print(f"\n❌ Workflow failed: {results['error']}")

if __name__ == "__main__":
    main()
