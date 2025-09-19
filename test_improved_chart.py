#!/usr/bin/env python3
"""
Test the improved chart generation with different dimensions.
"""

import os
import sys
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from html_to_png_converter import create_html_to_png_converter, extract_html_chart_from_response

def test_improved_chart():
    """Test the improved chart generation."""
    print("🧪 Testing improved chart generation...")
    
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
    
    # Test different dimensions
    test_configs = [
        {"width": 1200, "height": 800, "name": "standard"},
        {"width": 1200, "height": 900, "name": "tall"},
        {"width": 1400, "height": 800, "name": "wide"},
        {"width": 1000, "height": 1000, "name": "square"},
    ]
    
    for config in test_configs:
        print(f"\n🖼️  Testing {config['name']} format ({config['width']}x{config['height']})...")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        png_path = f"charts/chart_{config['name']}_{timestamp}.png"
        
        png_path = converter(
            html_chart, 
            output_path=png_path, 
            width=config['width'], 
            height=config['height']
        )
        
        if png_path:
            if os.path.exists(png_path):
                file_size = os.path.getsize(png_path)
                print(f"✅ {config['name']} chart: {png_path} ({file_size:,} bytes)")
            else:
                print(f"❌ {config['name']} chart file was not created")
        else:
            print(f"❌ Failed to generate {config['name']} chart")
    
    print("\n🎉 Chart generation test completed!")

if __name__ == "__main__":
    test_improved_chart()
