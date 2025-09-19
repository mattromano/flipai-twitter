# Flipside Chat Automation Setup

Create a Python repository for automating Flipside Crypto chat analysis using Selenium, designed to run in GitHub Actions.

## Repository Structure
```
flipside-chat-bot/
├── .github/
│   └── workflows/
│       └── daily-analysis.yml
├── src/
│   ├── __init__.py
│   ├── chat_automation.py
│   ├── session_manager.py
│   └── utils.py
├── config/
│   └── prompts.py
├── scripts/
│   ├── setup_local.py
│   └── activate_venv.py
├── requirements.txt
├── setup.py
├── README.md
├── .env.example
└── .gitignore
```

## Key Requirements

### 1. GitHub Actions Workflow (`.github/workflows/daily-analysis.yml`)
- Runs on Ubuntu latest with Chrome and ChromeDriver
- **Creates and uses Python virtual environment**
- **Activates venv before installing dependencies**
- Scheduled to run daily at 9 AM UTC 
- Manual trigger capability (`workflow_dispatch`)
- Handles session cookies stored as GitHub secrets
- Uploads screenshots as artifacts for debugging
- Proper error handling and logging

Example workflow structure:
```yaml
- name: Set up Python
  uses: actions/setup-python@v4
  with:
    python-version: '3.11'

- name: Create virtual environment
  run: python -m venv venv

- name: Activate virtual environment and install dependencies
  run: |
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    
- name: Run analysis
  run: |
    source venv/bin/activate
    python src/chat_automation.py
```

### 2. Main Automation Script (`src/chat_automation.py`)
- Chrome WebDriver with headless configuration optimized for GitHub Actions
- Session cookie management (load from base64 encoded GitHub secret)
- Navigate to https://flipsidecrypto.xyz/chat/
- Submit analysis prompts and wait for completion
- Extract chat URL and response text
- Screenshot chart/visualization elements
- Comprehensive error handling with retries
- Logging throughout the process

### 3. Session Manager (`src/session_manager.py`)
- Functions to encode/decode cookies for GitHub secrets storage
- Session validation and refresh logic
- Handle authentication state management
- Cookie persistence utilities

### 4. Utilities (`src/utils.py`)
- Wait functions for dynamic content loading
- Element detection helpers
- Screenshot capture utilities
- Text extraction and cleaning functions
- Prompt rotation logic

### 5. Configuration (`config/prompts.py`)
- Multiple analysis prompt templates
- Daily rotation logic
- Focus areas: DeFi trends, user behavior, protocol analysis, market insights
- Twitter-optimized output requests

## Technical Specifications

### Chrome Configuration
- Headless mode for GitHub Actions
- Window size: 1920x1080 for consistent screenshots  
- Disable GPU, sandbox, and dev-shm-usage
- Enable logging for debugging
- Proper user agent and viewport settings

### Wait Strategies
- WebDriverWait with custom expected conditions
- Wait for analysis completion indicators (no loading spinners)
- Wait for chart rendering (canvas, svg, or highcharts elements)
- Configurable timeouts (default: 60 seconds for analysis)

### Error Handling
- Retry logic for transient failures
- Screenshot capture on errors for debugging
- Graceful degradation if charts don't load
- Proper WebDriver cleanup in all scenarios

### Session Management
- Base64 encode cookies for GitHub secrets
- Session validation before proceeding
- Re-authentication detection and handling
- Cookie expiration management

## Expected File Contents

### requirements.txt
```
selenium>=4.15.0
webdriver-manager>=4.0.0
python-dotenv>=1.0.0
requests>=2.31.0
pillow>=10.0.0
```

### Virtual Environment Setup
Include proper virtual environment management:
- `setup.py` or `pyproject.toml` for package definition
- Virtual environment creation in both local setup and GitHub Actions
- Proper activation and deactivation handling
- Requirements installation within venv

### Chat URL Targets
- Main chat: https://flipsidecrypto.xyz/chat/
- Handle dynamic chat ID generation
- Extract final chat URL for sharing

### Element Selectors (customize based on actual Flipside site)
- Chat textarea: `textarea[placeholder*="message"], textarea[data-testid="chat-input"]`
- Submit button: `button[type="submit"], button[data-testid="send"]`
- Loading indicators: `.loading, .spinner, [data-testid="loading"]`
- Charts: `canvas, svg, .highcharts-container, [data-testid="chart"]`
- Response text: `.message-content, .chat-response, [data-testid="response"]`

### Analysis Prompts
Focus on crypto analysis prompts that generate:
- Specific metrics and insights
- Visual charts/graphs  
- Twitter-worthy summaries
- Recent timeframes (7-30 days)

Example prompts:
- "Analyze Ethereum DeFi protocol activity over the past 7 days. Which protocols saw the biggest user growth?"
- "Compare quality user behavior across Base, Arbitrum, and Optimism this month. Create a visualization."
- "What's the most significant trend in crypto markets this week based on on-chain data?"

## Environment Variables
- `FLIPSIDE_COOKIES`: Base64 encoded session cookies
- `DEBUG_MODE`: Enable verbose logging and longer waits
- `ANALYSIS_TIMEOUT`: Seconds to wait for analysis completion (default: 60)

## Success Criteria
- Successfully authenticates using stored cookies
- Submits analysis prompt and waits for completion
- Captures final chat URL
- Screenshots generated charts
- Extracts key insights from response
- Runs reliably in GitHub Actions environment
- Proper error handling and logging
- Clean resource management

## Additional Features
- **Local virtual environment setup script** (`scripts/setup_local.py`)
- **Virtual environment activation helper** for development
- Multiple prompt templates with rotation
- Configurable analysis timeout
- Debug mode with extended logging
- Screenshot comparison for chart detection
- Retry logic for flaky network conditions

### Local Development Setup
Include a setup script that:
```python
# scripts/setup_local.py
import subprocess
import sys
import os

def setup_local_environment():
    """Set up local development environment with virtual environment"""
    print("Creating virtual environment...")
    subprocess.run([sys.executable, "-m", "venv", "venv"])
    
    if os.name == 'nt':  # Windows
        activate_script = "venv\\Scripts\\activate"
        pip_path = "venv\\Scripts\\pip"
    else:  # Unix/Linux/macOS
        activate_script = "venv/bin/activate" 
        pip_path = "venv/bin/pip"
    
    print("Installing dependencies...")
    subprocess.run([pip_path, "install", "--upgrade", "pip"])
    subprocess.run([pip_path, "install", "-r", "requirements.txt"])
    
    print(f"Setup complete! Activate with: source {activate_script}")
```

Create all necessary files with production-ready code, proper error handling, and comprehensive logging. Include detailed README with setup instructions for both local development and GitHub Actions deployment.