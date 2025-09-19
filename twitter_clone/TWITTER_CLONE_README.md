# 🐦 Twitter Clone Frontend

A beautiful Twitter-like interface to preview and display FlipsideAI generated tweets.

## 🚀 Features

- **📱 Twitter-like UI**: Dark theme with authentic Twitter styling
- **📊 Tweet Previews**: Display all generated tweet previews
- **📏 Character Count**: Real-time character count validation
- **🔗 Direct Links**: Click to view full analysis reports
- **📋 Copy Function**: One-click copy tweet content
- **🔄 Auto-refresh**: Updates every 30 seconds
- **📱 Responsive**: Works on desktop and mobile

## 🎯 Usage

### Start the Frontend
```bash
# Simple start
python start_twitter_clone.py

# Or directly
python twitter_clone_frontend.py

# Custom port
python twitter_clone_frontend.py --port 3000
```

### Access the Interface
- **URL**: http://localhost:8080
- **Auto-opens**: Browser opens automatically
- **Stop**: Press `Ctrl+C` in terminal

## 📊 Tweet Information Displayed

Each tweet shows:
- **👤 User**: AgentFlippy (@AgentFlipp61663)
- **📝 Content**: Full tweet text with formatting
- **📏 Characters**: Current count vs 280 limit
- **⏰ Timestamp**: When analysis was generated
- **✅ Status**: Ready to post or too long
- **🔗 Actions**: Copy, View Analysis, Full Report

## 🎨 Interface Features

### Tweet Cards
- **Hover Effects**: Subtle animations on hover
- **Status Badges**: Green for ready, red for too long
- **Action Buttons**: Copy, view analysis, full report
- **Character Counter**: Color-coded (gray/red)

### Header
- **Logo**: FlipsideAI Tweets branding
- **Stats**: Total tweet count
- **Sticky**: Stays at top when scrolling

### Footer
- **Last Updated**: Timestamp of last refresh
- **Branding**: FlipsideAI Twitter Automation

## 🔧 Technical Details

### Files Generated
- `twitter_clone.html`: Main interface file
- `tweet_previews/`: Source data folder
- Auto-generated from JSON tweet data

### Data Source
Reads from `tweet_previews/*_tweet_*.json` files created by:
```bash
python tweet_preview_generator.py
```

### Auto-refresh
- **Interval**: 30 seconds
- **Behavior**: Reloads page automatically
- **Manual**: Click refresh button

## 🎯 Perfect For

- **👀 Preview Testing**: See how tweets will look
- **📊 Content Review**: Review all generated content
- **🔗 Link Testing**: Verify analysis URLs work
- **📱 Mobile Testing**: Check mobile appearance
- **👥 Team Sharing**: Share with team members

## 🚀 Quick Start

1. **Generate Tweets**:
   ```bash
   python run_full_workflow.py --prompt "Your analysis prompt" --no-twitter
   python tweet_preview_generator.py
   ```

2. **Start Frontend**:
   ```bash
   python start_twitter_clone.py
   ```

3. **View in Browser**: http://localhost:8080

## 🎉 Enjoy Your Twitter Clone!

Perfect for testing and previewing your FlipsideAI generated tweets before posting to the real Twitter! 🚀
