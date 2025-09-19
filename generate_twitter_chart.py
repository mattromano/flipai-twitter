#!/usr/bin/env python3
"""
Generate a Highcharts chart optimized for Twitter posting.
"""

import os
import sys
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from html_to_png_converter import create_html_to_png_converter, extract_html_chart_from_response

def generate_twitter_chart():
    """Generate a chart optimized for Twitter posting."""
    print("🐦 Generating Twitter-optimized chart...")
    
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
    
    # Twitter-optimized dimensions
    # Twitter supports images up to 5MB, but smaller is better for loading
    # Common Twitter image dimensions: 1200x675 (16:9), 1200x800, or 1200x900
    twitter_configs = [
        {"width": 1200, "height": 800, "name": "twitter_standard", "description": "Standard Twitter format"},
        {"width": 1200, "height": 900, "name": "twitter_tall", "description": "Tall format for better chart visibility"},
        {"width": 1200, "height": 1000, "name": "twitter_extra_tall", "description": "Extra tall for maximum chart visibility"},
    ]
    
    for config in twitter_configs:
        print(f"\n🖼️  Generating {config['description']} ({config['width']}x{config['height']})...")
        
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
                
                # Check if file size is Twitter-friendly (under 5MB)
                if file_size < 5 * 1024 * 1024:
                    print(f"   ✅ Twitter-friendly size")
                else:
                    print(f"   ⚠️  Large file size for Twitter")
            else:
                print(f"❌ {config['description']} file was not created")
        else:
            print(f"❌ Failed to generate {config['description']}")
    
    print("\n🎉 Twitter chart generation completed!")
    print("\n📋 Twitter posting tips:")
    print("• Use the chart with the best balance of visibility and file size")
    print("• Twitter supports images up to 5MB, but smaller files load faster")
    print("• The 1200x800 format is often optimal for Twitter")
    print("• Make sure to include the Twitter text with the image")

if __name__ == "__main__":
    generate_twitter_chart()
