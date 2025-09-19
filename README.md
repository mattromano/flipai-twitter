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

2. **Run the Automation**
   ```bash
   python run_automation_with_logging.py
   ```

## 📁 Project Structure

### Core Files
- `run_automation_with_logging.py` - Main automation script
- `src/chat_automation_robust.py` - Core automation logic
- `src/automation_logger.py` - Logging system
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
6. **Output Generation** - Creates Twitter-ready content

## 📊 Performance

- **Total Runtime**: ~5 minutes (optimized from 27+ minutes)
- **Response Timeout**: 2 minutes
- **Result Capture**: ~10 seconds
- **Screenshot Workflow**: ~18 seconds

## 🎯 Key Features

- ✅ **Fast Performance** - Optimized for speed
- ✅ **Robust Error Handling** - Continues on timeouts
- ✅ **Clean Screenshots** - Published artifact views
- ✅ **Twitter Integration** - Ready for posting
- ✅ **Comprehensive Logging** - Full workflow tracking

## 📝 Usage

The automation runs with the default prompt:
> "Give me a full analysis comparing the supply of USDT and USDC across all the top blockchains"

To use a different prompt, edit the `custom_prompt` variable in `run_automation_with_logging.py`.

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