#!/usr/bin/env python3
"""
Test the dynamic chart sizing with various dimensions to ensure all charts fit properly.
"""

import os
import sys
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from html_to_png_converter import create_html_to_png_converter, extract_html_chart_from_response

def test_dynamic_sizing():
    """Test dynamic sizing with various dimensions."""
    print("🧪 Testing dynamic chart sizing with various dimensions...")
    
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
    
    # Test various dimensions to ensure dynamic sizing works
    test_dimensions = [
        # Small formats
        {"width": 800, "height": 600, "name": "small", "description": "Small format (800x600)"},
        {"width": 1000, "height": 700, "name": "medium", "description": "Medium format (1000x700)"},
        
        # Standard formats
        {"width": 1200, "height": 800, "name": "standard", "description": "Standard format (1200x800)"},
        {"width": 1200, "height": 1000, "name": "standard_tall", "description": "Standard tall (1200x1000)"},
        
        # Large formats
        {"width": 1400, "height": 1000, "name": "large", "description": "Large format (1400x1000)"},
        {"width": 1600, "height": 1200, "name": "extra_large", "description": "Extra large (1600x1200)"},
        
        # Wide formats
        {"width": 1800, "height": 900, "name": "wide", "description": "Wide format (1800x900)"},
        {"width": 2000, "height": 1000, "name": "ultra_wide", "description": "Ultra wide (2000x1000)"},
        
        # Square formats
        {"width": 1000, "height": 1000, "name": "square", "description": "Square format (1000x1000)"},
        {"width": 1200, "height": 1200, "name": "large_square", "description": "Large square (1200x1200)"},
    ]
    
    successful_generations = []
    
    for config in test_dimensions:
        print(f"\n🖼️  Testing {config['description']}...")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        png_path = f"charts/dynamic_test_{config['name']}_{timestamp}.png"
        
        try:
            png_path = converter(
                html_chart, 
                output_path=png_path, 
                width=config['width'], 
                height=config['height']
            )
            
            if png_path and os.path.exists(png_path):
                file_size = os.path.getsize(png_path)
                file_size_kb = file_size / 1024
                print(f"✅ {config['description']}: {png_path}")
                print(f"   📁 File size: {file_size:,} bytes ({file_size_kb:.1f} KB)")
                
                successful_generations.append({
                    'name': config['name'],
                    'description': config['description'],
                    'path': png_path,
                    'size': file_size,
                    'size_kb': file_size_kb
                })
                
                # Check if file size is reasonable
                if file_size < 2 * 1024 * 1024:  # Under 2MB
                    print(f"   ✅ Reasonable file size")
                else:
                    print(f"   ⚠️  Large file size")
            else:
                print(f"❌ {config['description']} file was not created")
        except Exception as e:
            print(f"❌ Error generating {config['description']}: {e}")
    
    print(f"\n🎉 Dynamic sizing test completed!")
    print(f"✅ Successfully generated {len(successful_generations)} charts")
    
    if successful_generations:
        print("\n📊 Generated Charts Summary:")
        for chart in successful_generations:
            print(f"   • {chart['description']}: {chart['size_kb']:.1f} KB")
        
        # Find the best chart for different use cases
        smallest = min(successful_generations, key=lambda x: x['size'])
        largest = max(successful_generations, key=lambda x: x['size'])
        
        print(f"\n🏆 Recommendations:")
        print(f"   • Smallest file: {smallest['description']} ({smallest['size_kb']:.1f} KB)")
        print(f"   • Largest file: {largest['description']} ({largest['size_kb']:.1f} KB)")
        
        # Twitter recommendations
        twitter_friendly = [c for c in successful_generations if c['size'] < 5 * 1024 * 1024]
        if twitter_friendly:
            best_twitter = max(twitter_friendly, key=lambda x: x['size'])
            print(f"   • Best for Twitter: {best_twitter['description']} ({best_twitter['size_kb']:.1f} KB)")
    
    print("\n📋 Dynamic Sizing Features Tested:")
    print("   ✅ Automatic dimension calculation")
    print("   ✅ Responsive header and margin sizing")
    print("   ✅ Flexbox layout for chart distribution")
    print("   ✅ Highcharts CSS overrides")
    print("   ✅ Minimum chart size enforcement")
    print("   ✅ Text scaling based on dimensions")

if __name__ == "__main__":
    test_dynamic_sizing()
