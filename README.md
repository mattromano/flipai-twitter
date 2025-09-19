# 🚀 Flipside AI + Twitter Automation

A comprehensive automation system for Flipside AI analysis and Twitter posting with intelligent prompt selection and usage tracking.

## 📁 Repository Structure

```
flipai-twitter/
├── main_workflow.py              # 🎯 MAIN ENTRY POINT - Single script to rule them all
├── modules/                      # 📦 Modular components
│   ├── chat_manager/            # 💬 Flipside AI chat automation
│   │   ├── __init__.py
│   │   ├── flipside_automation.py    # Core chat automation logic
│   │   ├── data_extractor.py         # Text data extraction
│   │   ├── chat_data_extractor.py    # Specialized chat extraction
│   │   └── artifact_capture.py       # Chart/visualization capture
│   ├── twitter_manager/         # 🐦 Twitter functionality
│   │   ├── __init__.py
│   │   ├── twitter_poster.py         # Twitter API posting
│   │   └── tweet_preview.py          # Tweet preview generation
│   └── shared/                  # 🔧 Shared utilities
│       ├── __init__.py
│       ├── logger.py                 # Centralized logging
│       ├── authentication.py         # Stealth authentication
│       └── prompt_selector.py        # 🆕 Random prompt selection & tracking
├── prompts/                     # 📝 Prompt management
│   ├── analysis_prompts_2025_09_19.json  # 50 curated analysis prompts
│   └── prompt_usage.json        # 🆕 Usage tracking data
├── logs/                        # 📝 Analysis and Twitter logs
├── screenshots/                 # 📸 Screenshots
├── tweet_previews/              # 🐦 Tweet preview files
├── twitter_clone/               # 🌐 Twitter clone frontend
└── .github/workflows/           # 🔄 GitHub Actions automation
    └── daily-analysis.yml       # 🆕 Daily automation with prompt selection
```

## 🎯 Main Features

### 🆕 **Intelligent Prompt Selection**
- **50 Curated Prompts**: Pre-built analysis prompts across 10 categories
- **Random Selection**: Automatically picks unused prompts to avoid repetition
- **Usage Tracking**: Persistent tracking prevents duplicate usage
- **Smart Filtering**: Filter by category, difficulty, or both
- **Statistics Dashboard**: Monitor usage patterns and availability

### 🤖 **Complete Automation**
- **Single Entry Point**: One script (`main_workflow.py`) for everything
- **Modular Design**: Clean separation of concerns
- **Stealth Authentication**: Bypasses bot detection
- **Enhanced Artifact Detection**: Captures charts and visualizations
- **Twitter Integration**: Full API integration with preview system

## 🚀 Quick Start

### 1. Setup Environment
```bash
# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env with your credentials
```

### 2. Run Analysis with Random Prompt Selection
```bash
# 🆕 Select a random unused prompt
python main_workflow.py --random-prompt

# 🆕 Select from specific category
python main_workflow.py --random-prompt --category "DeFi Ecosystem Health"

# 🆕 Select by difficulty level
python main_workflow.py --random-prompt --difficulty intermediate

# 🆕 Combined filters
python main_workflow.py --random-prompt --category "NFT Market Intelligence" --difficulty advanced
```

### 3. Traditional Custom Prompts
```bash
# Use your own prompt
python main_workflow.py --prompt "Analyze Bitcoin trends" --analysis-only

# Full workflow with Twitter posting
python main_workflow.py --prompt "Compare DeFi protocols"

# Preview only (no Twitter posting)
python main_workflow.py --prompt "Analysis only" --no-twitter
```

## 🎲 Prompt Selection System

### Available Categories (50 Total Prompts)
- **Ecosystem Growth & User Quality Analysis** (5 prompts)
- **Protocol Performance Deep Dives** (5 prompts)
- **Cross-Chain Comparative Analysis** (5 prompts)
- **User Behavior & Cohort Analysis** (5 prompts)
- **Market Dynamics & Trends** (5 prompts)
- **DeFi Ecosystem Health** (5 prompts)
- **NFT Market Intelligence** (5 prompts)
- **Governance & Staking Analysis** (5 prompts)
- **Advanced Multi-Metric Dashboards** (5 prompts)
- **Arbitrage & MEV Analysis** (5 prompts)

### Difficulty Levels
- **Intermediate**: 35 prompts - Standard analysis complexity
- **Advanced**: 15 prompts - Complex multi-metric analysis

### Usage Tracking
```bash
# 🆕 View prompt usage statistics
python main_workflow.py --stats

# Output shows:
# - Total/Used/Available prompts
# - Usage percentage
# - Available categories and difficulties
# - Usage history and trends
```

## 🎯 Complete Usage Examples

### Random Prompt Selection
```bash
# Basic random selection
python main_workflow.py --random-prompt

# Category filtering
python main_workflow.py --random-prompt --category "DeFi Ecosystem Health"
python main_workflow.py --random-prompt --category "NFT Market Intelligence"

# Difficulty filtering
python main_workflow.py --random-prompt --difficulty intermediate
python main_workflow.py --random-prompt --difficulty advanced

# Combined filtering
python main_workflow.py --random-prompt --category "Market Dynamics & Trends" --difficulty advanced
```

### Custom Prompts
```bash
# Analysis only (no Twitter posting)
python main_workflow.py --prompt "Analyze Bitcoin trends" --analysis-only

# Full workflow with Twitter posting
python main_workflow.py --prompt "Compare DeFi protocols"

# Custom timeout (15 minutes)
python main_workflow.py --prompt "Complex analysis" --timeout 900

# Preview only (no Twitter posting)
python main_workflow.py --prompt "Analysis only" --no-twitter

# Debug mode
python main_workflow.py --prompt "Test prompt" --debug
```

### Management & Statistics
```bash
# View usage statistics
python main_workflow.py --stats

# Direct prompt selector CLI
python modules/shared/prompt_selector.py --select
python modules/shared/prompt_selector.py --stats
python modules/shared/prompt_selector.py --list-available
python modules/shared/prompt_selector.py --reset  # Reset usage tracking
```

## 🔄 GitHub Actions Automation

The system includes automated daily runs with intelligent prompt selection:

### Workflow Features
- **Daily Schedule**: Runs at 9 AM UTC automatically
- **Manual Triggers**: Supports manual runs with custom parameters
- **Prompt Selection**: Random selection with filtering options
- **Usage Tracking**: Persistent across CI/CD runs
- **Artifact Upload**: Screenshots, logs, and results

### Manual Workflow Triggers
When manually triggering the workflow, you can choose:
- **Prompt Type**: Random selection or custom prompt
- **Category Filter**: Filter prompts by category
- **Difficulty Filter**: Choose intermediate or advanced
- **Custom Prompt**: Provide your own analysis prompt

## 🔧 Configuration

### Environment Variables (.env)
```bash
# Flipside Credentials
FLIPSIDE_EMAIL=your_email@example.com
FLIPSIDE_PASSWORD=your_password

# Twitter API Credentials (v1.1 + v2)
TWITTER_BEARER_TOKEN=your_bearer_token
TWITTER_CONSUMER_KEY=your_consumer_key
TWITTER_CONSUMER_SECRET=your_consumer_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret

# Optional: Chrome settings
CHROME_HEADLESS=true
DEBUG_MODE=false
```

### Command Line Options
```bash
# Prompt Selection (choose one)
--prompt "Your custom prompt"           # Use custom prompt
--random-prompt                         # Select random unused prompt

# Filtering (use with --random-prompt)
--category "Category Name"              # Filter by category
--difficulty {intermediate,advanced}    # Filter by difficulty

# Workflow Options
--analysis-only                         # Analysis only (no Twitter)
--no-twitter                           # Skip Twitter posting
--timeout 600                          # Response timeout (seconds)
--debug                                # Enable debug mode
--stats                                # Show usage statistics
```

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
- `screenshots/artifact_YYYYMMDD_HHMMSS.png` - Artifact screenshots

### Tweet Previews
- `tweet_previews/*_tweet_*.json` - Tweet data
- `tweet_previews/*_preview_*.html` - HTML preview
- `tweet_previews/*_preview_*.md` - Markdown preview

### Twitter Logs
- `logs/twitter_posts_YYYYMMDD.jsonl` - Twitter post history

### 🆕 Prompt Management
- `prompts/analysis_prompts_2025_09_19.json` - All available prompts
- `prompts/prompt_usage.json` - Usage tracking data

## 🎉 Key Features

### ✅ **Intelligent Prompt Management**
- 🎲 Random selection from 50 curated prompts
- 📊 Persistent usage tracking prevents duplicates
- 🏷️ Category and difficulty filtering
- 📈 Usage statistics and monitoring
- 🔄 Automatic prompt rotation

### ✅ **Complete Automation**
- 🎯 Single entry point (`main_workflow.py`)
- 📦 Modular design with clear separation
- 🛡️ Stealth authentication bypasses detection
- 📸 Enhanced artifact capture
- 🔄 GitHub Actions integration

### ✅ **Twitter Integration**
- 🐦 Full API integration (v1.1 + v2)
- 👀 Tweet preview generation
- 📝 Character count validation
- 📊 Post logging and tracking

### ✅ **Local Testing**
- 🖥️ Tweet preview system
- 🌐 Twitter clone frontend
- 🚫 No API dependency for testing
- 📄 Multiple output formats

### ✅ **Robust Error Handling**
- 🔍 Comprehensive error management
- 📝 Detailed logging and debugging
- ⏱️ Configurable timeouts
- 🔄 Automatic retry mechanisms

## 🛠️ Development

The system is built with a clean modular architecture:

- **`modules/chat_manager/`** - Handles all Flipside AI automation
- **`modules/twitter_manager/`** - Handles all Twitter functionality
- **`modules/shared/`** - Common utilities and components
  - **`prompt_selector.py`** - 🆕 Prompt selection and tracking system

Each module is self-contained and can be easily extended or modified.

## 📞 Support

For issues or questions:
1. Check the logs in the `logs/` directory for detailed error information
2. Use `--debug` flag for verbose output
3. Check prompt usage with `--stats`
4. Review the workflow configuration in `.github/workflows/`

---

**🎯 Single Entry Point**: `python main_workflow.py --help` for all options!

**🎲 Smart Prompt Selection**: Never run the same analysis twice with intelligent usage tracking!