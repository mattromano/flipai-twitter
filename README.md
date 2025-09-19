# Flipside AI Twitter Automation

A streamlined automation system that generates DeFi analysis content from Flipside AI and creates Twitter-ready posts with charts.

## 🚀 Quick Start

1. **Setup Environment**
   ```bash
   # Activate virtual environment
   source venv/bin/activate
   
   # Install dependencies (if not already done)
   pip install -r requirements.txt
   ```

2. **Setup Twitter API (Optional)**
   ```bash
   # Configure Twitter API credentials
   python setup_twitter.py
   
   # Test Twitter integration
   python test_twitter_integration.py
   ```

3. **Run the Automation**
   ```bash
   # Analysis only
   python run_automation_with_logging.py
   
   # Full workflow (analysis + Twitter posting)
   python run_full_workflow.py
   
   # With custom prompt
   python run_full_workflow.py --prompt "Your custom analysis prompt"
   ```

## 🔐 Authentication & Login Fallback

The system includes **login fallback** for expired cookies:

- ✅ **Self-Healing**: Automatically detects expired cookies
- ✅ **Manual Login**: Waits for you to log in manually (5 minutes timeout)
- ✅ **Auto-Save**: Saves fresh cookies automatically
- ✅ **Seamless**: Continues automation after login

**When cookies expire:**
1. Browser opens automatically (non-headless)
2. You log in manually with your credentials
3. System detects successful login
4. Fresh cookies are saved automatically
5. Automation continues seamlessly

See [LOGIN_FALLBACK_GUIDE.md](LOGIN_FALLBACK_GUIDE.md) for detailed information.

## 📁 Project Structure

### Core Files
- `run_automation_with_logging.py` - Main automation script
- `run_full_workflow.py` - Complete workflow (analysis + Twitter)
- `twitter_poster.py` - Twitter posting system
- `src/chat_automation_robust.py` - Core automation logic
- `src/automation_logger.py` - Logging system
- `src/twitter_generator.py` - Twitter content generation
- `config/prompts.py` - Analysis prompts

### Generated Outputs
- `charts/` - Published artifact screenshots
- `logs/` - Analysis results and logs
- `screenshots/` - Debug screenshots

### Configuration
- `flipside_cookies.txt` - Authentication cookies
- `requirements.txt` - Python dependencies

## 🔧 How It Works

1. **Authentication** - Loads Flipside cookies for access
2. **Prompt Submission** - Submits analysis request to Flipside AI
3. **Response Processing** - Waits for AI response with charts
4. **Result Capture** - Extracts text and identifies visualizations
5. **Artifact Screenshot** - Publishes and screenshots the clean artifact view
6. **Twitter Generation** - Creates engaging tweet content from analysis
7. **Twitter Posting** - Posts to Twitter with image (optional)

## 📊 Performance

- **Total Runtime**: ~5 minutes (optimized from 27+ minutes)
- **Response Timeout**: 2 minutes
- **Result Capture**: ~10 seconds
- **Screenshot Workflow**: ~18 seconds

## 🎯 Key Features

- ✅ **Fast Performance** - Optimized for speed
- ✅ **Robust Error Handling** - Continues on timeouts
- ✅ **Clean Screenshots** - Published artifact views
- ✅ **Twitter Integration** - Automatic posting with images
- ✅ **Smart Content Generation** - AI-powered tweet creation
- ✅ **Comprehensive Logging** - Full workflow tracking

## 📝 Usage

### Basic Usage
The automation runs with the default prompt:
> "Give me a full analysis comparing the supply of USDT and USDC across all the top blockchains"

### Custom Prompts
```bash
# Use custom prompt
python run_full_workflow.py --prompt "Your custom analysis prompt here"

# Skip Twitter posting
python run_full_workflow.py --no-twitter

# Enable debug mode
python run_full_workflow.py --debug
```

### Twitter Setup
1. Get Twitter API credentials from https://developer.twitter.com/
2. Run setup: `python setup_twitter.py`
3. Test integration: `python test_twitter_integration.py`

## 🔍 Output Files

- `charts/published_artifact_*.png` - Clean artifact screenshots
- `logs/analysis_*.json` - Complete analysis results
- `logs/daily_summary_*.jsonl` - Daily summaries

## 🛠️ Troubleshooting

See `TROUBLESHOOTING.md` for common issues and solutions.

## 📚 Documentation

- `AUTOMATION_FIXES_DOCUMENTATION.md` - Technical fixes and improvements
- `MANUAL_SETUP.md` - Manual setup instructions
- `IMPLEMENTATION_SUMMARY.md` - Implementation details