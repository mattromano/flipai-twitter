#!/usr/bin/env python3
"""
Convert HTML chart to PNG image for Twitter posting.
"""

import os
import sys
import time
import tempfile
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def create_html_to_png_converter():
    """Create a converter that takes HTML chart code and converts it to PNG."""
    
    def convert_html_to_png(html_content, output_path=None, width=1200, height=800):
        """
        Convert HTML chart content to PNG image.
        
        Args:
            html_content (str): The HTML content containing the chart
            output_path (str): Path to save the PNG file (optional)
            width (int): Width of the rendered image
            height (int): Height of the rendered image
            
        Returns:
            str: Path to the generated PNG file
        """
        if output_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f"charts/chart_{timestamp}.png"
        
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Modify HTML to ensure proper sizing
        modified_html = modify_html_for_full_capture(html_content, width, height)
        
        # Set up Chrome options for headless rendering with Highcharts support
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument(f'--window-size={width},{height}')
        chrome_options.add_argument('--disable-web-security')
        chrome_options.add_argument('--allow-running-insecure-content')
        chrome_options.add_argument('--force-device-scale-factor=1')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-plugins')
        chrome_options.add_argument('--disable-images')  # Faster loading
        # Note: JavaScript must be enabled for Highcharts to work
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Set up ChromeDriver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        try:
            # Create a temporary HTML file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as temp_file:
                temp_file.write(modified_html)
                temp_file_path = temp_file.name
            
            # Load the HTML file
            file_url = f"file://{temp_file_path}"
            driver.get(file_url)
            
            # Wait for Highcharts to load and render
            time.sleep(3)
            
            # Set the window size to ensure full capture
            driver.set_window_size(width, height)
            
            # Wait for Highcharts to re-render with new dimensions
            time.sleep(3)
            
            # Additional wait to ensure all charts are fully rendered
            time.sleep(2)
            
            # Take a screenshot
            driver.save_screenshot(output_path)
            
            print(f"✅ Chart saved as PNG: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"❌ Error converting HTML to PNG: {e}")
            return None
            
        finally:
            driver.quit()
            # Clean up temporary file
            try:
                os.unlink(temp_file_path)
            except:
                pass
    
    return convert_html_to_png

def modify_html_for_full_capture(html_content, width, height):
    """Modify HTML to dynamically fit all charts to any size while preserving Highcharts styling."""
    # Calculate dynamic dimensions based on available space
    # Reserve space for header, margins, and gaps
    header_height = min(100, height * 0.15)  # 15% of height or max 100px
    margin = min(40, width * 0.03)  # 3% of width or max 40px
    gap = min(20, width * 0.02)  # 2% of width or max 20px
    
    # Calculate available space for charts
    available_width = width - (margin * 2)
    available_height = height - header_height - (margin * 2)
    
    # Calculate chart dimensions for 2x2 grid
    chart_width = (available_width - gap) // 2
    chart_height = (available_height - gap) // 2
    
    # Ensure minimum chart sizes
    chart_width = max(chart_width, 200)
    chart_height = max(chart_height, 150)
    
    # Replace the CSS styles to ensure proper sizing while preserving Highcharts appearance
    modified_css = f"""
    <style>
        * {{
            box-sizing: border-box;
        }}
        body {{ 
            margin: 0; 
            padding: {margin}px; 
            font-family: Arial, sans-serif; 
            background-color: white;
            width: {width}px;
            height: {height}px;
            overflow: hidden;
        }}
        .container {{ 
            width: 100%; 
            height: 100%; 
            margin: 0; 
            font-family: Arial, sans-serif; 
            display: flex;
            flex-direction: column;
        }}
        .header {{ 
            text-align: center; 
            margin-bottom: {gap}px; 
            height: {header_height}px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}
        .header h2 {{ 
            margin: 0; 
            font-size: {min(24, width * 0.02)}px; 
            color: #333;
            font-weight: bold;
        }}
        .header p {{ 
            margin: 5px 0 0 0; 
            font-size: {min(16, width * 0.015)}px; 
            color: #666;
        }}
        .charts-container {{
            flex: 1;
            display: flex;
            flex-direction: column;
            gap: {gap}px;
        }}
        .charts-row {{ 
            display: flex; 
            gap: {gap}px; 
            flex: 1;
            justify-content: center;
            align-items: stretch;
        }}
        .chart {{ 
            flex: 1;
            max-width: {chart_width}px;
            max-height: {chart_height}px;
            min-width: 200px;
            min-height: 150px;
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            background-color: #f8f9fa;
            position: relative;
        }}
        /* Ensure Highcharts renders properly and fills the container */
        .highcharts-container {{
            width: 100% !important;
            height: 100% !important;
            position: absolute !important;
            top: 0 !important;
            left: 0 !important;
        }}
        .highcharts-root {{
            width: 100% !important;
            height: 100% !important;
        }}
        .highcharts-plot-area {{
            width: 100% !important;
            height: 100% !important;
        }}
        /* Responsive text sizing */
        .highcharts-title {{
            font-size: {min(16, width * 0.012)}px !important;
        }}
        .highcharts-subtitle {{
            font-size: {min(12, width * 0.01)}px !important;
        }}
        .highcharts-axis-labels {{
            font-size: {min(10, width * 0.008)}px !important;
        }}
    </style>
    """
    
    # Replace the original style section
    if '<style>' in html_content and '</style>' in html_content:
        start = html_content.find('<style>')
        end = html_content.find('</style>') + 8
        html_content = html_content[:start] + modified_css + html_content[end:]
    else:
        # If no style section, add it after the head tag
        head_end = html_content.find('</head>')
        html_content = html_content[:head_end] + modified_css + html_content[head_end:]
    
    return html_content

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

def main():
    """Main function to test the HTML to PNG conversion."""
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
    
    # Convert to PNG
    png_path = converter(html_chart, width=1200, height=600)
    
    if png_path:
        print(f"✅ Successfully converted HTML chart to PNG: {png_path}")
        
        # Check if file exists and get size
        if os.path.exists(png_path):
            file_size = os.path.getsize(png_path)
            print(f"📁 PNG file size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
        else:
            print("❌ PNG file was not created")
    else:
        print("❌ Failed to convert HTML to PNG")

if __name__ == "__main__":
    main()
