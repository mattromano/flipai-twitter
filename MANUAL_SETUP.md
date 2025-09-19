# Manual Setup Guide

If the automated setup scripts are having issues, you can set up the environment manually using these step-by-step instructions.

## Prerequisites

- Python 3.8 or higher
- Chrome browser installed
- Terminal/Command Prompt access

## Step-by-Step Manual Setup

### 1. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 2. Upgrade pip

```bash
# Upgrade pip to latest version
pip install --upgrade pip
```

### 3. Install Dependencies

```bash
# Install all required packages
pip install selenium>=4.15.0
pip install webdriver-manager>=4.0.0
pip install python-dotenv>=1.0.0
pip install requests>=2.31.0
pip install pillow>=10.0.0
```

Or install from requirements.txt if it exists:

```bash
pip install -r requirements.txt
```

### 4. Create Directories

```bash
# Create necessary directories
mkdir screenshots
mkdir logs
mkdir artifacts
```

### 5. Set Up Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit the .env file with your actual values
# You'll need to add your Flipside Crypto session cookies
```

### 6. Test Installation

```bash
# Test that all packages are installed correctly
python -c "import selenium; print('Selenium version:', selenium.__version__)"
python -c "import webdriver_manager; print('WebDriver Manager: OK')"
python -c "import dotenv; print('Python-dotenv: OK')"
```

### 7. Test the Automation

```bash
# Run the automation script
python src/chat_automation.py
```

## Getting Your Session Cookies

To get your Flipside Crypto session cookies:

1. **Login to Flipside Crypto** in your browser
2. **Open Developer Tools** (F12)
3. **Go to Application/Storage tab**
4. **Find Cookies** for `flipsidecrypto.xyz`
5. **Copy all cookies** and encode them to base64

### Cookie Encoding Script

Create a file called `encode_cookies.py`:

```python
import json
import base64
from selenium import webdriver

# Get cookies from your browser session
driver = webdriver.Chrome()
driver.get("https://flipsidecrypto.xyz")

# Login manually in the browser window that opens
input("Press Enter after you've logged in...")

# Get cookies
cookies = driver.get_cookies()
driver.quit()

# Encode cookies for GitHub secrets
cookies_json = json.dumps(cookies)
encoded = base64.b64encode(cookies_json.encode('utf-8')).decode('utf-8')

print(f"FLIPSIDE_COOKIES={encoded}")
print("\nCopy this value to your .env file")
```

Run it with:
```bash
python encode_cookies.py
```

## Troubleshooting

### Virtual Environment Issues

If `python -m venv venv` fails:

1. **Check Python version**: `python --version`
2. **Try with full path**: `/usr/bin/python3 -m venv venv`
3. **Use virtualenv instead**: `pip install virtualenv && virtualenv venv`

### Package Installation Issues

If pip install fails:

1. **Update pip**: `python -m pip install --upgrade pip`
2. **Use specific Python**: `python3 -m pip install selenium`
3. **Install one by one**: Install packages individually to identify issues

### Chrome Driver Issues

The automation uses `webdriver-manager` to handle ChromeDriver automatically, but if you have issues:

1. **Update Chrome browser** to latest version
2. **Check Chrome installation**: Make sure Chrome is in your PATH
3. **Manual ChromeDriver**: Download ChromeDriver manually and add to PATH

### Permission Issues

If you get permission errors:

1. **Use user install**: `pip install --user selenium`
2. **Check file permissions**: Make sure you have write access to the directory
3. **Run as administrator** (Windows) or with `sudo` (macOS/Linux) if needed

## Alternative Setup Methods

### Using Conda

If you prefer conda:

```bash
# Create conda environment
conda create -n flipside-chat python=3.11
conda activate flipside-chat

# Install packages
conda install selenium
pip install webdriver-manager python-dotenv requests pillow
```

### Using Poetry

If you prefer Poetry:

```bash
# Install Poetry first
curl -sSL https://install.python-poetry.org | python3 -

# Create pyproject.toml
poetry init

# Add dependencies
poetry add selenium webdriver-manager python-dotenv requests pillow

# Install and activate
poetry install
poetry shell
```

## Verification

After setup, verify everything works:

```bash
# Check virtual environment is active
which python  # Should show path to venv/bin/python

# Test imports
python -c "from src.chat_automation import FlipsideChatAutomation; print('✅ Import successful')"

# Test prompt system
python -c "from config.prompts import get_prompt_for_today; print('Today\\'s prompt:', get_prompt_for_today()[:50] + '...')"
```

## Next Steps

Once setup is complete:

1. **Configure your .env file** with Flipside cookies
2. **Test the automation** with debug mode: `DEBUG_MODE=true python src/chat_automation.py`
3. **Set up GitHub Actions** for automated daily runs
4. **Customize prompts** in `config/prompts.py` for your needs

## Getting Help

If you continue to have issues:

1. **Check the logs** in the `logs/` directory
2. **Enable debug mode** for detailed output
3. **Review the README.md** for additional troubleshooting
4. **Check system requirements** and Python version compatibility
