#!/usr/bin/env python3
"""
Generate a Twitter-optimized chart that shows all 4 charts properly.
"""

import os
import sys
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from html_to_png_converter import create_html_to_png_converter, extract_html_chart_from_response

def generate_twitter_optimized():
    """Generate a Twitter-optimized chart that shows all 4 charts properly."""
    print("🐦 Generating Twitter-optimized chart with all 4 charts visible...")
    
    # Read the response text from our previous extraction
    response_file = "logs/final_working_response.txt"
    
    if not os.path.exists(response_file):
        print(f"❌ Response file not found: {response_file}")
        return
    
    with open(response_file, 'r', encoding='utf-8') as f:
        response_text = f.read()
    
    # Extract the HTML chart
    html_chart = extract_html_chart_from_response(response_text)
    
    if not html_chart:
        print("❌ No HTML chart found in response")
        return
    
    print("📊 HTML chart extracted from response")
    print(f"HTML length: {len(html_chart)} characters")
    
    # Create the converter
    converter = create_html_to_png_converter()
    
    # Twitter-optimized configurations that should show all charts
    twitter_configs = [
        {"width": 1400, "height": 1000, "name": "twitter_optimized", "description": "Twitter optimized (1400x1000)"},
        {"width": 1200, "height": 1000, "name": "twitter_standard_tall", "description": "Twitter standard tall (1200x1000)"},
        {"width": 1600, "height": 900, "name": "twitter_wide", "description": "Twitter wide (1600x900)"},
    ]
    
    for config in twitter_configs:
        print(f"\n🖼️  Generating {config['description']}...")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        png_path = f"charts/{config['name']}_{timestamp}.png"
        
        png_path = converter(
            html_chart, 
            output_path=png_path, 
            width=config['width'], 
            height=config['height']
        )
        
        if png_path:
            if os.path.exists(png_path):
                file_size = os.path.getsize(png_path)
                file_size_kb = file_size / 1024
                print(f"✅ {config['description']}: {png_path}")
                print(f"   📁 File size: {file_size:,} bytes ({file_size_kb:.1f} KB)")
                
                # Check if file size is Twitter-friendly
                if file_size < 5 * 1024 * 1024:  # Under 5MB
                    print(f"   ✅ Twitter-friendly size")
                else:
                    print(f"   ⚠️  Large file size for Twitter")
            else:
                print(f"❌ {config['description']} file was not created")
        else:
            print(f"❌ Failed to generate {config['description']}")
    
    print("\n🎉 Twitter-optimized chart generation completed!")
    print("\n📋 Twitter posting tips:")
    print("• Use the format that shows all 4 charts completely")
    print("• Twitter supports images up to 5MB")
    print("• The 1400x1000 format should be optimal for showing all charts")
    print("• You can also use the 1200x1000 format for a more standard Twitter size")

if __name__ == "__main__":
    generate_twitter_optimized()
