#!/usr/bin/env python3
"""
Generate a chart with dimensions that ensure all 4 charts are fully visible.
"""

import os
import sys
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from html_to_png_converter import create_html_to_png_converter, extract_html_chart_from_response

def generate_full_chart():
    """Generate a chart with dimensions that show all 4 charts completely."""
    print("📊 Generating full chart with all 4 charts visible...")
    
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
    
    # Test configurations with much larger dimensions to ensure all charts are visible
    test_configs = [
        {"width": 1400, "height": 1000, "name": "extra_large", "description": "Extra large format"},
        {"width": 1600, "height": 1200, "name": "huge", "description": "Huge format for maximum visibility"},
        {"width": 1200, "height": 1200, "name": "square_large", "description": "Large square format"},
        {"width": 1800, "height": 1000, "name": "ultra_wide", "description": "Ultra wide format"},
    ]
    
    for config in test_configs:
        print(f"\n🖼️  Testing {config['description']} ({config['width']}x{config['height']})...")
        
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
                file_size_kb = file_size / 1024
                print(f"✅ {config['description']}: {png_path}")
                print(f"   📁 File size: {file_size:,} bytes ({file_size_kb:.1f} KB)")
                
                # Check if file size is reasonable
                if file_size < 2 * 1024 * 1024:  # Under 2MB
                    print(f"   ✅ Reasonable file size")
                else:
                    print(f"   ⚠️  Large file size")
            else:
                print(f"❌ {config['description']} file was not created")
        else:
            print(f"❌ Failed to generate {config['description']}")
    
    print("\n🎉 Full chart generation completed!")
    print("\n📋 Recommendations:")
    print("• Use the format that shows all 4 charts completely")
    print("• For Twitter, you may need to crop or resize the image")
    print("• The extra_large or huge formats should show all charts")

if __name__ == "__main__":
    generate_full_chart()
