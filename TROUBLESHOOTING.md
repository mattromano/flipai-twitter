# 🔧 Troubleshooting Guide

This document tracks issues encountered during the development and testing of the Flipside Chat Automation system.

## 🚨 Current Issues

### Issue #3: Share Button Detection
**Status:** 🔴 ACTIVE  
**Date:** 2025-09-18  
**Description:** Cannot find the Share button to extract the shareable link.

**Symptoms:**
- Automation successfully submits prompts and gets responses
- Share button not found when trying to extract shareable link
- Need to improve selectors for Share button detection

**Current Selectors Tested:**
```css
button:contains('Share')
[data-testid='share']
.share-button
button[title*='Share']
button[aria-label*='Share']
```

**Next Steps:**
1. 🔄 Inspect the actual Share button element in browser
2. 🔄 Add more generic selectors
3. 🔄 Test with non-headless mode to see the actual button

### Issue #4: Response Text and Artifact Detection
**Status:** 🔴 ACTIVE  
**Date:** 2025-09-18  
**Description:** Cannot detect the AI response text and visual artifacts (charts).

**Symptoms:**
- AI responses are generated (evidenced by new chat URLs)
- Cannot extract Twitter text output
- Cannot detect charts/visualizations on the right panel
- Response text length is 0 characters

**Current Selectors Tested:**
```css
[data-testid='twitter-text']
.twitter-text
.twitter-output
div:contains('TWITTER_TEXT')
div:contains('Twitter')
```

**Next Steps:**
1. 🔄 Inspect the actual response elements in browser
2. 🔄 Add more generic selectors for text extraction
3. 🔄 Improve chart detection selectors
4. 🔄 Test with non-headless mode for visual debugging

## ✅ Resolved Issues

### Issue #1: Session Cookie Loading Timeout
**Status:** ✅ RESOLVED  
**Date:** 2025-09-18  
**Description:** The automation gets stuck after loading session cookies, specifically at the "Session cookies loaded and applied" step.

**Symptoms:**
- Automation runs successfully through WebDriver setup
- Session cookies are loaded (21 cookies found)
- Cookies are applied to the browser
- Process hangs indefinitely after cookie application

**Debugging Steps Taken:**
1. ✅ Added enhanced logging with step-by-step progress tracking
2. ✅ Added timeout mechanisms (60 seconds per step)
3. ✅ Created debug script to identify where process hangs
4. ✅ Added screenshot capture for debugging

**Potential Causes:**
1. **Expired Session Cookies:** The stored cookies may have expired
2. **Website Structure Changes:** Flipside may have changed their authentication flow
3. **JavaScript Requirements:** The site may require JavaScript execution for proper loading
4. **Rate Limiting:** The site may be rate-limiting automated requests

**Next Steps:**
1. 🔄 Test with fresh cookie generation
2. 🔄 Disable JavaScript blocking in Chrome options
3. 🔄 Add more detailed element detection logging
4. 🔄 Test with non-headless mode for visual debugging

### Issue #2: Chat Interface Element Detection
**Status:** ✅ RESOLVED  
**Date:** 2025-09-18  
**Description:** Difficulty finding chat input elements on the Flipside chat page.

**Symptoms:**
- Navigation to chat page succeeds
- Cannot locate textarea or input elements for chat
- Multiple selector attempts fail

**Current Selectors Tested:**
```css
textarea[placeholder*='Ask FlipsideAI']
textarea
textarea[placeholder*='message']
textarea[data-testid='chat-input']
.chat-input
[data-testid='chat-interface']
```

**Potential Solutions:**
1. Update selectors based on current website structure
2. Add more generic selectors
3. Use XPath as fallback
4. Wait for dynamic content loading

## 🛠️ Debugging Tools

### Enhanced Logging System
The system now includes comprehensive logging with:
- Step-by-step progress tracking
- Emoji-based status indicators
- Timing information for each step
- Detailed error reporting
- Screenshot capture on errors

### Debug Scripts
- `debug_automation.py` - Step-by-step debugging with screenshots
- `test_robust_automation.py` - Robust automation with timeouts
- `test_enhanced_logging.py` - Logging system demonstration

### Screenshot Debugging
Screenshots are automatically captured at key points:
- `debug_main_page.png` - Main Flipside page
- `debug_chat_page.png` - Chat page after navigation
- `error_state.png` - Error state when automation fails

## 🔍 Manual Testing Steps

### 1. Cookie Validation
```bash
# Check if cookies are valid
python encode_cookies.py
# This will open a browser for manual login and cookie extraction
```

### 2. Element Detection
```bash
# Run debug script to see what elements are found
python debug_automation.py
```

### 3. Robust Automation Test
```bash
# Test with timeouts and better error handling
python test_robust_automation.py
```

## 📊 Performance Metrics

### Current Timeouts
- **WebDriver Setup:** 60 seconds
- **Session Loading:** 60 seconds
- **Navigation:** 60 seconds
- **Prompt Submission:** 60 seconds
- **Response Waiting:** 120 seconds

### Success Rates
- **WebDriver Setup:** 100% ✅
- **Session Loading:** 0% ❌ (hangs after cookie application)
- **Navigation:** Unknown (not reached)
- **Prompt Submission:** Unknown (not reached)
- **Response Waiting:** Unknown (not reached)

## 🎯 Resolution Strategy

### Phase 1: Cookie Issues
1. Generate fresh cookies using `encode_cookies.py`
2. Test cookie validity manually
3. Update cookie storage format if needed

### Phase 2: Element Detection
1. Run debug script to identify current page structure
2. Update selectors based on findings
3. Add fallback selectors

### Phase 3: JavaScript Requirements
1. Test with JavaScript enabled
2. Add proper wait conditions for dynamic content
3. Implement retry logic for element detection

### Phase 4: Rate Limiting
1. Add delays between requests
2. Implement exponential backoff
3. Add user-agent rotation if needed

## 📝 Log Analysis

### Key Log Patterns to Watch
```
✅ Session cookies loaded and applied
# Process should continue here but hangs
```

### Error Patterns
```
❌ Failed to load cookies within 60 seconds
❌ Failed to navigate to chat page within 60 seconds
❌ Element not found: textarea[placeholder*='Ask FlipsideAI']
```

## 🔄 Testing Checklist

Before each test run:
- [ ] Check if cookies are fresh (< 24 hours old)
- [ ] Verify Flipside website is accessible
- [ ] Ensure Chrome WebDriver is up to date
- [ ] Check for any website maintenance messages
- [ ] Verify network connectivity

After each test run:
- [ ] Review automation summary
- [ ] Check screenshot files for visual debugging
- [ ] Analyze log files for error patterns
- [ ] Update this troubleshooting guide with findings

## 📞 Support Resources

### Internal Tools
- Enhanced logging system with step tracking
- Debug scripts with screenshot capture
- Robust automation with timeout handling

### External Resources
- Selenium WebDriver documentation
- Chrome DevTools for element inspection
- Flipside Crypto website for manual testing

---

**Last Updated:** 2025-09-18  
**Next Review:** After resolving current cookie loading issue
