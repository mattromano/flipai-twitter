# 🚀 Flipside AI + Twitter Automation - New Structure

## 📁 Repository Structure

```
flipai-twitter/
├── main_workflow.py              # 🎯 MAIN ENTRY POINT - Single script to rule them all
├── modules/                      # 📦 Modular components
│   ├── chat_manager/            # 💬 Flipside AI chat automation
│   │   ├── __init__.py
│   │   ├── flipside_automation.py    # Core chat automation logic
│   │   ├── data_extractor.py         # Text data extraction
│   │   └── artifact_capture.py       # Chart/visualization capture
│   ├── twitter_manager/         # 🐦 Twitter functionality
│   │   ├── __init__.py
│   │   ├── twitter_poster.py         # Twitter API posting
│   │   └── tweet_preview.py          # Tweet preview generation
│   └── shared/                  # 🔧 Shared utilities
│       ├── __init__.py
│       ├── logger.py                 # Centralized logging
│       └── authentication.py         # Stealth authentication
├── logs/                        # 📝 Analysis and Twitter logs
├── screenshots/                 # 📸 Screenshots
├── tweet_previews/              # 🐦 Tweet preview files
└── twitter_clone/               # 🌐 Twitter clone frontend
```

## 🎯 Main Workflow Script

**`main_workflow.py`** is the single entry point for all automation tasks.

### Usage Examples:

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

## 📦 Module Breakdown

### 1. Chat Manager (`modules/chat_manager/`)

**Purpose**: Handles all Flipside AI chat automation

**Components**:
- **`flipside_automation.py`**: Core automation logic
  - Initialization and WebDriver setup
  - Authentication (stealth + fallback)
  - Navigation and prompt submission
  - Response waiting and monitoring
  - Data extraction orchestration

- **`data_extractor.py`**: Text data extraction
  - Response text extraction
  - Twitter text parsing
  - Sidebar content filtering
  - Summary generation

- **`artifact_capture.py`**: Chart/visualization capture
  - Multi-selector artifact detection
  - Chart library support (Highcharts, Plotly, D3, etc.)
  - Screenshot capture for artifacts

### 2. Twitter Manager (`modules/twitter_manager/`)

**Purpose**: Handles all Twitter-related functionality

**Components**:
- **`twitter_poster.py`**: Twitter API integration
  - API client setup (v1.1 + v2)
  - Tweet posting with media
  - Rate limit handling
  - Post logging

- **`tweet_preview.py`**: Tweet preview generation
  - Preview creation from analysis data
  - HTML/Markdown/JSON output
  - Character count validation
  - Local testing support

### 3. Shared (`modules/shared/`)

**Purpose**: Common utilities used across modules

**Components**:
- **`logger.py`**: Centralized logging
  - File and console logging
  - Structured log messages
  - Daily log rotation

- **`authentication.py`**: Stealth authentication
  - Undetected Chrome driver setup
  - Anti-detection techniques
  - Credential management

## 🔄 Workflow Flow

### Analysis Only Mode:
1. **Initialize** → Setup WebDriver and authentication
2. **Authenticate** → Login to Flipside (stealth or standard)
3. **Navigate** → Go to chat page
4. **Submit** → Send prompt to AI
5. **Wait** → Monitor for response completion
6. **Extract** → Capture text data and artifacts
7. **Save** → Store results to files

### Full Workflow Mode:
1. **Analysis** → Complete analysis workflow above
2. **Preview** → Generate tweet preview
3. **Post** → Send to Twitter API (if enabled)
4. **Log** → Record all activities

## 🎨 Key Features

### ✅ **Clean Architecture**
- Single entry point (`main_workflow.py`)
- Modular design with clear separation
- Shared utilities to avoid duplication
- Easy to maintain and extend

### ✅ **Robust Automation**
- Stealth authentication with fallback
- Enhanced artifact detection
- Configurable timeouts
- Comprehensive error handling

### ✅ **Twitter Integration**
- Full API integration (v1.1 + v2)
- Tweet preview generation
- Character count validation
- Post logging and tracking

### ✅ **Local Testing**
- Tweet preview system
- Twitter clone frontend
- No API dependency for testing
- Multiple output formats

## 🚀 Getting Started

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Setup Environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

3. **Run Analysis**:
   ```bash
   python main_workflow.py --prompt "Your analysis prompt"
   ```

4. **View Results**:
   - Check `logs/` for analysis results
   - Check `tweet_previews/` for tweet previews
   - Check `screenshots/` for visual captures

## 🔧 Configuration

### Environment Variables:
- `FLIPSIDE_EMAIL` - Flipside login email
- `FLIPSIDE_PASSWORD` - Flipside login password
- `TWITTER_API_KEY` - Twitter API key
- `TWITTER_API_SECRET` - Twitter API secret
- `TWITTER_ACCESS_TOKEN` - Twitter access token
- `TWITTER_ACCESS_TOKEN_SECRET` - Twitter access token secret
- `TWITTER_BEARER_TOKEN` - Twitter bearer token

### Command Line Options:
- `--prompt` - Analysis prompt (required)
- `--analysis-only` - Run analysis only
- `--no-twitter` - Skip Twitter posting
- `--timeout` - Response timeout in seconds
- `--debug` - Enable debug mode

## 🎉 Benefits of New Structure

1. **🎯 Single Entry Point**: One script to run everything
2. **📦 Modular Design**: Easy to maintain and extend
3. **🔄 Reusable Components**: Shared utilities across modules
4. **🧪 Easy Testing**: Preview system for local testing
5. **📝 Better Logging**: Centralized and structured logging
6. **🛡️ Error Handling**: Comprehensive error management
7. **⚡ Performance**: Optimized for speed and reliability

This new structure eliminates the scattered scripts and provides a clean, maintainable codebase with a single entry point for all automation tasks! 🚀
