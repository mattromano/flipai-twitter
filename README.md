# 🚀 Flipside AI + Twitter Automation

A clean, modular automation system for Flipside AI analysis and Twitter posting.

## 📁 Structure

```
flipai-twitter/
├── main_workflow.py              # 🎯 MAIN ENTRY POINT
├── modules/                      # 📦 Modular components
│   ├── chat_manager/            # 💬 Flipside AI automation
│   │   ├── flipside_automation.py    # Core automation logic
│   │   ├── data_extractor.py         # Text data extraction
│   │   └── artifact_capture.py       # Chart/visualization capture
│   ├── twitter_manager/         # 🐦 Twitter functionality
│   │   ├── twitter_poster.py         # Twitter API posting
│   │   └── tweet_preview.py          # Tweet preview generation
│   └── shared/                  # 🔧 Shared utilities
│       ├── logger.py                 # Centralized logging
│       └── authentication.py         # Stealth authentication
├── logs/                        # 📝 Analysis and Twitter logs
├── screenshots/                 # 📸 Screenshots
├── tweet_previews/              # 🐦 Tweet preview files
└── twitter_clone/               # 🌐 Twitter clone frontend
```

## 🚀 Quick Start

### 1. Setup Environment
```bash
# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env with your credentials
```

### 2. Run Analysis
```bash
# Analysis only (no Twitter posting)
python main_workflow.py --prompt "Analyze Bitcoin trends" --analysis-only

# Full workflow with Twitter posting
python main_workflow.py --prompt "Compare DeFi protocols"

# Preview only (no Twitter posting)
python main_workflow.py --prompt "Analysis only" --no-twitter
```

## 🎯 Usage Examples

```bash
# Run analysis only
python main_workflow.py --prompt "Analyze Bitcoin trends" --analysis-only

# Run full workflow with Twitter posting
python main_workflow.py --prompt "Compare DeFi protocols"

# Run with custom timeout (15 minutes)
python main_workflow.py --prompt "Complex analysis" --timeout 900

# Run without Twitter posting (preview only)
python main_workflow.py --prompt "Analysis only" --no-twitter

# Debug mode
python main_workflow.py --prompt "Test prompt" --debug
```

## 🔧 Configuration

### Environment Variables (.env)
```bash
# Flipside Credentials
FLIPSIDE_EMAIL=your_email@example.com
FLIPSIDE_PASSWORD=your_password

# Twitter API Credentials
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret
TWITTER_BEARER_TOKEN=your_bearer_token
```

### Command Line Options
- `--prompt` - Analysis prompt (required)
- `--analysis-only` - Run analysis only (no Twitter)
- `--no-twitter` - Skip Twitter posting (preview only)
- `--timeout` - Response timeout in seconds (default: 600)
- `--debug` - Enable debug mode

## 📊 Workflow Modes

### 1. Analysis Only (`--analysis-only`)
- Authenticates with Flipside
- Submits prompt and waits for response
- Extracts text data and artifacts
- Saves results to logs/
- No Twitter posting

### 2. Preview Mode (`--no-twitter`)
- Runs complete analysis
- Generates tweet preview
- Saves preview files (JSON, HTML, Markdown)
- No Twitter posting

### 3. Full Workflow (default)
- Runs complete analysis
- Generates tweet preview
- Posts to Twitter API
- Logs all activities

## 🐦 Twitter Clone Frontend

View your tweet previews in a beautiful Twitter-like interface:

```bash
# Start the Twitter clone frontend
cd twitter_clone
python twitter_clone_frontend.py

# Access at http://localhost:8080
```

## 📝 Output Files

### Analysis Results
- `logs/analysis_YYYYMMDD_HHMMSS.json` - Complete analysis data
- `screenshots/final_state_YYYYMMDD_HHMMSS.png` - Final screenshot

### Tweet Previews
- `tweet_previews/*_tweet_*.json` - Tweet data
- `tweet_previews/*_preview_*.html` - HTML preview
- `tweet_previews/*_preview_*.md` - Markdown preview

### Twitter Logs
- `logs/twitter_posts_YYYYMMDD.jsonl` - Twitter post history

## 🎉 Features

- ✅ **Single Entry Point**: One script (`main_workflow.py`) for everything
- ✅ **Modular Design**: Clean separation of concerns
- ✅ **Stealth Authentication**: Bypasses bot detection
- ✅ **Enhanced Artifact Detection**: Captures charts and visualizations
- ✅ **Tweet Preview System**: Local testing without API calls
- ✅ **Twitter Clone Frontend**: Beautiful preview interface
- ✅ **Comprehensive Logging**: Detailed activity tracking
- ✅ **Error Handling**: Robust error management
- ✅ **Configurable Timeouts**: Adjustable response waiting

## 🛠️ Development

The system is built with a clean modular architecture:

- **`modules/chat_manager/`** - Handles all Flipside AI automation
- **`modules/twitter_manager/`** - Handles all Twitter functionality
- **`modules/shared/`** - Common utilities and components

Each module is self-contained and can be easily extended or modified.

## 📞 Support

For issues or questions, check the logs in the `logs/` directory for detailed error information.

---

**🎯 Single Entry Point**: `python main_workflow.py --help` for all options!
