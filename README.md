# Flipside Chat Automation

A Python automation tool for analyzing Flipside Crypto chat data using Selenium, designed to run in GitHub Actions with daily scheduling.

## 🚀 Features

- **Automated Chat Analysis**: Submits analysis prompts to Flipside Crypto chat
- **Session Management**: Handles authentication via stored cookies
- **Screenshot Capture**: Captures charts and visualizations
- **GitHub Actions Integration**: Runs daily with automated scheduling
- **Comprehensive Logging**: Detailed logs for debugging and monitoring
- **Retry Logic**: Robust error handling with automatic retries
- **Multiple Prompt Templates**: Rotating analysis prompts for variety

## 📁 Project Structure

```
flipside-chat-bot/
├── .github/
│   └── workflows/
│       └── daily-analysis.yml    # GitHub Actions workflow
├── src/
│   ├── __init__.py
│   ├── chat_automation.py        # Main automation script
│   ├── session_manager.py        # Cookie and session management
│   └── utils.py                  # Utility functions
├── config/
│   └── prompts.py                # Analysis prompt templates
├── scripts/
│   ├── setup_local.py            # Local environment setup
│   └── activate_venv.py          # Virtual environment helper
├── requirements.txt              # Python dependencies
├── setup.py                      # Package configuration
├── .env.example                  # Environment variables template
└── .gitignore                    # Git ignore rules
```

## 🛠️ Setup Instructions

### Prerequisites

- Python 3.8 or higher
- Chrome browser (for local development)
- Flipside Crypto account with valid session cookies

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd flipside-chat-bot
   ```

2. **Run the setup script**
   ```bash
   python scripts/setup_local.py
   ```

3. **Activate the virtual environment**
   ```bash
   # On macOS/Linux
   source venv/bin/activate
   
   # On Windows
   venv\Scripts\activate
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your actual values
   ```

5. **Test the installation**
   ```bash
   python scripts/activate_venv.py check
   ```

### Environment Variables

Create a `.env` file with the following variables:

```env
# Base64 encoded session cookies from Flipside Crypto
FLIPSIDE_COOKIES=your_base64_encoded_cookies_here

# Enable verbose logging and longer waits for debugging
DEBUG_MODE=false

# Seconds to wait for analysis completion (default: 60)
ANALYSIS_TIMEOUT=60

# Chrome options for local development
CHROME_HEADLESS=true
CHROME_WINDOW_SIZE=1920,1080
```

### Getting Your Session Cookies

1. **Login to Flipside Crypto** in your browser
2. **Open Developer Tools** (F12)
3. **Go to Application/Storage tab**
4. **Find Cookies** for `flipsidecrypto.xyz`
5. **Copy all cookies** and encode them to base64

You can use this Python script to encode your cookies:

```python
import json
import base64
from selenium import webdriver

# Get cookies from your browser session
driver = webdriver.Chrome()
driver.get("https://flipsidecrypto.xyz")
cookies = driver.get_cookies()

# Encode cookies for GitHub secrets
cookies_json = json.dumps(cookies)
encoded = base64.b64encode(cookies_json.encode('utf-8')).decode('utf-8')
print(f"FLIPSIDE_COOKIES={encoded}")
```

## 🚀 Usage

### Running Locally

1. **Activate virtual environment**
   ```bash
   source venv/bin/activate  # macOS/Linux
   # or
   venv\Scripts\activate     # Windows
   ```

2. **Run the automation**
   ```bash
   python src/chat_automation.py
   ```

3. **Using the helper script**
   ```bash
   python scripts/activate_venv.py run
   ```

### GitHub Actions Setup

1. **Fork or clone this repository**

2. **Add GitHub Secrets**
   - Go to your repository settings
   - Navigate to "Secrets and variables" → "Actions"
   - Add a new secret named `FLIPSIDE_COOKIES`
   - Set the value to your base64-encoded cookies

3. **Enable GitHub Actions**
   - The workflow will run automatically daily at 9 AM UTC
   - You can also trigger it manually from the Actions tab

4. **Monitor Results**
   - Check the Actions tab for run status
   - Download artifacts (screenshots and logs) from completed runs

## 📊 Analysis Prompts

The system includes various analysis prompt categories:

- **DeFi Protocols**: Protocol activity, TVL analysis, yield farming trends
- **Layer 2 Solutions**: L2 comparison, gas fees, adoption metrics
- **Market Insights**: On-chain trends, whale movements, market sentiment
- **User Behavior**: Onboarding patterns, retention rates, usage analytics
- **Protocol Deep Dives**: Specific protocol analysis and governance
- **Emerging Trends**: New protocols, innovations, market developments
- **Twitter Summaries**: Social media optimized content

### Prompt Rotation

- **Daily**: Deterministic rotation based on day of year
- **Weekly**: Curated prompts for each day of the week
- **Monthly**: Extended rotation for long-term analysis
- **Random**: Random selection for variety

## 🔧 Configuration

### Chrome Configuration

The automation uses Chrome with the following optimizations:

- **Headless mode** for GitHub Actions
- **Window size**: 1920x1080 for consistent screenshots
- **Performance options**: Disabled GPU, sandbox, and dev-shm-usage
- **Logging enabled** for debugging

### Wait Strategies

- **WebDriverWait** with custom expected conditions
- **Loading completion detection** (no spinners)
- **Chart rendering wait** (canvas, svg, highcharts)
- **Configurable timeouts** (default: 60 seconds)

### Error Handling

- **Retry logic** for transient failures
- **Screenshot capture** on errors for debugging
- **Graceful degradation** if charts don't load
- **Proper cleanup** in all scenarios

## 📸 Output

The automation captures:

- **Full page screenshots** of the chat interface
- **Chart screenshots** of generated visualizations
- **Response text** from the analysis
- **Chat URLs** for sharing results
- **Comprehensive logs** for debugging

## 🧪 Testing

### Test Commands

```bash
# Check package installation
python scripts/activate_venv.py check

# Test Selenium import
python -c "import selenium; print('Selenium version:', selenium.__version__)"

# Run with debug mode
DEBUG_MODE=true python src/chat_automation.py

# Test prompt selection
python -c "from config.prompts import get_prompt_for_today; print(get_prompt_for_today())"
```

### Local Testing

1. **Set debug mode** in `.env`:
   ```env
   DEBUG_MODE=true
   ANALYSIS_TIMEOUT=120
   ```

2. **Run with verbose logging**:
   ```bash
   python src/chat_automation.py
   ```

3. **Check logs** in the `logs/` directory

4. **Review screenshots** in the `screenshots/` directory

## 🐛 Troubleshooting

### Common Issues

1. **Session expired**
   - Update your cookies in the `.env` file
   - Re-encode cookies and update GitHub secrets

2. **Chrome driver issues**
   - The script uses `webdriver-manager` to handle ChromeDriver
   - Ensure Chrome browser is installed

3. **Element not found**
   - Flipside may have updated their UI
   - Check the selectors in `src/chat_automation.py`
   - Enable debug mode for detailed logging

4. **Analysis timeout**
   - Increase `ANALYSIS_TIMEOUT` in `.env`
   - Check network connectivity
   - Verify Flipside service status

### Debug Mode

Enable debug mode for detailed logging:

```env
DEBUG_MODE=true
ANALYSIS_TIMEOUT=120
```

This will:
- Show detailed WebDriver logs
- Capture more screenshots
- Use longer timeouts
- Provide verbose console output

## 📝 Development

### Adding New Prompts

Edit `config/prompts.py` to add new analysis prompts:

```python
NEW_CATEGORY = [
    "Your new analysis prompt here",
    "Another prompt for this category"
]
```

### Modifying Selectors

Update element selectors in `src/chat_automation.py` if Flipside changes their UI:

```python
input_selectors = [
    "textarea[placeholder*='message']",
    "textarea[data-testid='chat-input']",
    # Add new selectors here
]
```

### Extending Functionality

- **New utilities**: Add to `src/utils.py`
- **Session management**: Extend `src/session_manager.py`
- **Configuration**: Modify `config/prompts.py`

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For issues and questions:

1. Check the troubleshooting section
2. Review the logs in the `logs/` directory
3. Enable debug mode for detailed information
4. Open an issue on GitHub

## 🔄 Updates

The automation is designed to be robust and handle:

- UI changes on Flipside Crypto
- Network connectivity issues
- Session expiration
- Analysis timeouts
- Chart rendering delays

Regular updates may be needed as Flipside evolves their platform.
