"""
Flipside Chat Automation Manager

Handles the core automation logic for Flipside AI chat interactions.
"""

import os
import time
import re
import logging
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

from modules.shared.authentication import StealthAuthenticator
from modules.shared.logger import AutomationLogger
from modules.shared.text_utils import is_placeholder_twitter_text


class FlipsideChatManager:
    """Manages Flipside AI chat automation workflow."""
    
    def __init__(self, use_stealth_auth: bool = True):  # Default to True for automated login
        self.driver: Optional[webdriver.Chrome] = None
        self.authenticator: Optional[StealthAuthenticator] = None
        self.logger: AutomationLogger = AutomationLogger()
        self.use_stealth_auth = use_stealth_auth
        self.extracted_twitter_text: str = ""  # Store Twitter text extracted after conclusion marker
        
        # Setup directories
        os.makedirs("screenshots", exist_ok=True)
        os.makedirs("logs", exist_ok=True)
        os.makedirs("prompts", exist_ok=True)
        
        # Recent prompts file path
        self.recent_prompts_file = Path("prompts/recent_prompts.json")
    
    def initialize(self) -> bool:
        """Initialize the automation environment."""
        try:
            self.logger.log_info("🚀 Initializing Flipside chat automation")
            
            if self.use_stealth_auth:
                self.logger.log_info("🤖 Setting up stealth Chrome driver")
                self.authenticator = StealthAuthenticator(self.logger)
                if not self.authenticator.setup_driver():
                    self.logger.log_error("❌ Failed to setup stealth driver")
                    return False
                self.driver = self.authenticator.driver
                self.logger.log_success("✅ ✅ Stealth Chrome driver setup complete")
            else:
                self.logger.log_info("🤖 Setting up regular Chrome driver")
                self.driver = self._setup_standard_driver()
                if not self.driver:
                    self.logger.log_error("❌ Failed to setup regular driver")
                    return False
                self.logger.log_success("✅ ✅ Regular Chrome driver setup complete")
            
            self.logger.log_success("✅ ✅ Automation environment initialized")
            return True
            
        except Exception as e:
            self.logger.log_error(f"Initialization failed: {e}")
            return False
    
    def authenticate(self) -> bool:
        """Authenticate with Flipside."""
        try:
            self.logger.log_info("🔐 Starting authentication")
            
            if self.use_stealth_auth and self.authenticator:
                self.logger.log_info("🔐 Starting stealth login process")
                success = self.authenticator.login()
                if success:
                    self.logger.log_success("✅ Stealth authentication successful")
                    return True
                else:
                    self.logger.log_error("❌ Stealth authentication failed")
                    return False
            else:
                # For regular driver, we'll skip authentication for now
                # This assumes the user is already logged in or will log in manually
                self.logger.log_info("ℹ️ Using regular driver - skipping automatic authentication")
                self.logger.log_info("ℹ️ Please ensure you are logged into Flipside in the browser")
                return True
                
        except Exception as e:
            self.logger.log_error(f"Authentication failed: {e}")
            return False
    
    def navigate_to_chat(self) -> bool:
        """Navigate to the Flipside chat page."""
        try:
            self.logger.log_info("🧭 Navigating to chat page")
            
            # First check if we're already on a chat page
            current_url = self.driver.current_url if self.driver else ""
            if '/chat/' in current_url:
                self.logger.log_info(f"✅ Already on chat page: {current_url}")
                # Verify we can find chat input elements
                try:
                    chat_input_indicators = [
                        "textarea[placeholder*='Ask']",
                        "textarea[placeholder*='message']",
                        "textarea",
                        "input[placeholder*='message']"
                    ]
                    for indicator in chat_input_indicators:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, indicator)
                        for elem in elements:
                            if elem.is_displayed() and elem.is_enabled():
                                self.logger.log_info(f"✅ Verified chat input is available: {indicator}")
                                return True
                except:
                    pass
                # If we're on chat page but can't find input, continue to navigation logic
                self.logger.log_info("⚠️ On chat page but input not found, refreshing...")
            
            # Try different chat URLs
            chat_urls = [
                "https://flipsidecrypto.xyz/chat/",
                "https://app.flipsidecrypto.xyz/chat/",
                "https://flipsidecrypto.xyz/chat",
                "https://app.flipsidecrypto.xyz/chat"
            ]
            
            navigation_successful = False
            for chat_url in chat_urls:
                try:
                    self.logger.log_info(f"🌐 Trying chat URL: {chat_url}")
                    self.driver.get(chat_url)
                    time.sleep(5)
                    
                    # Check if we're on a chat page (not login page)
                    current_url = self.driver.current_url
                    page_title = self.driver.title
                    
                    self.logger.log_info(f"📍 Current URL: {current_url}")
                    self.logger.log_info(f"📄 Page title: {page_title}")
                    
                    # Check if we're not on login page and page has loaded
                    if "login" not in current_url.lower() and "signin" not in current_url.lower():
                        # Look for chat-specific elements
                        chat_indicators = [
                            "textarea",
                            "input[placeholder*='message']",
                            "input[placeholder*='ask']",
                            "[data-testid*='chat']",
                            ".chat",
                            ".message"
                        ]
                        
                        chat_found = False
                        for indicator in chat_indicators:
                            try:
                                elements = self.driver.find_elements(By.CSS_SELECTOR, indicator)
                                if elements:
                                    chat_found = True
                                    self.logger.log_info(f"✅ Found chat indicator: {indicator}")
                                    break
                            except:
                                continue
                        
                        if chat_found or "chat" in current_url.lower():
                            self.logger.log_info(f"✅ Successfully navigated to chat page: {current_url}")
                            navigation_successful = True
                            break
                        else:
                            self.logger.log_info(f"❌ No chat elements found at {current_url}")
                    else:
                        self.logger.log_info(f"❌ Still on login page: {current_url}")
                        
                except Exception as e:
                    self.logger.log_warning(f"Failed to navigate to {chat_url}: {e}")
                    continue
            
            if not navigation_successful:
                self.logger.log_error("❌ Could not navigate to chat page")
                return False
            
            # Wait for page to fully load
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Take screenshot
            screenshot_path = f"screenshots/chat_page_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            self.driver.save_screenshot(screenshot_path)
            self.logger.log_info(f"📸 Screenshot saved: {screenshot_path}")
            
            self.logger.log_success("✅ Successfully navigated to chat page")
            return True
            
        except Exception as e:
            self.logger.log_error(f"Navigation failed: {e}")
            return False
    
    def _load_recent_prompts(self) -> List[Dict[str, str]]:
        """Load recent prompts from JSON file."""
        try:
            if self.recent_prompts_file.exists():
                with open(self.recent_prompts_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Handle both old format (list of strings) and new format (list of objects)
                    if data and isinstance(data[0], str):
                        # Convert old format to new format
                        return [{"condensed_prompt": p, "used_at": datetime.now().isoformat()} for p in data]
                    return data
            else:
                # Create empty file
                with open(self.recent_prompts_file, 'w', encoding='utf-8') as f:
                    json.dump([], f, indent=2)
                return []
        except Exception as e:
            self.logger.log_warning(f"Failed to load recent prompts: {e}")
            return []
    
    def _save_recent_prompt(self, condensed_prompt: str) -> bool:
        """Save a new condensed prompt to the recent prompts file, maintaining max 32 entries."""
        try:
            if not condensed_prompt or not condensed_prompt.strip():
                self.logger.log_warning("Cannot save empty condensed prompt")
                return False
            
            # Load existing prompts
            recent_prompts = self._load_recent_prompts()
            
            # Remove any duplicate of this prompt (if it exists)
            recent_prompts = [p for p in recent_prompts if p.get("condensed_prompt") != condensed_prompt]
            
            # Add new prompt with timestamp
            new_entry = {
                "condensed_prompt": condensed_prompt.strip(),
                "used_at": datetime.now().isoformat()
            }
            recent_prompts.append(new_entry)
            
            # Keep only last 32 entries (FIFO)
            if len(recent_prompts) > 32:
                recent_prompts = recent_prompts[-32:]
            
            # Save to file
            with open(self.recent_prompts_file, 'w', encoding='utf-8') as f:
                json.dump(recent_prompts, f, indent=2, ensure_ascii=False)
            
            self.logger.log_success(f"✅ Saved condensed prompt: {condensed_prompt}")
            return True
        except Exception as e:
            self.logger.log_error(f"Failed to save recent prompt: {e}")
            return False
    
    def _format_recent_prompts_for_prompt(self) -> str:
        """Format recent prompts as a string for injection into the prompt template."""
        try:
            recent_prompts = self._load_recent_prompts()
            
            # Extract just the condensed_prompt strings
            prompt_strings = [p.get("condensed_prompt", "") for p in recent_prompts if p.get("condensed_prompt")]
            
            # Format as JSON array string
            if prompt_strings:
                formatted = json.dumps(prompt_strings, ensure_ascii=False)
                return formatted
            else:
                return "[]"
        except Exception as e:
            self.logger.log_warning(f"Failed to format recent prompts: {e}")
            return "[]"
    
    def _get_analysis_prompt_template(self) -> str:
        """Get the static analysis phase prompt template (Phase 1)."""
        return """<role>
Crypto analyst at Flipside creating data-driven Twitter content.
</role>

<recent_prompts>
LAST_32_ANALYSES: {recent_prompts}
</recent_prompts>

<topic_selection>
Check <recent_prompts>, query 2-3 topics to find strongest data + narrative, choose ONE:

GROWTH (1-3):
1. fastest_growing_contract: Largest tx/event volume growth (7d) - why gaining traction, user segmentation
2. emerging_protocol: Crossed 10K+ weekly users first time (30d) - retention, quality score progression
3. chain_momentum: Largest quality user % increase (14d) - compare prior period, identify drivers

DECLINE (4-6):
4. dex_volume_decline: Largest volume drop (90d) - patterns, user segments, migration analysis
5. protocol_churn: Losing quality users (30d) - where migrating, retention cohorts
6. nft_decline: Sharpest volume drops (60d) - holder behavior, floor price correlation

COMPARATIVE (7-9):
7. chain_fee_comparison: Gas fees across chains (30d) - correlate with activity, user preferences
8. defi_protocol_battle: 2-3 competing protocols - user overlap, loyalty, volume shifts
9. l2_competition: ETH L2s (90d) - costs, speed, growth, quality user segmentation

BEHAVIOR (10-12):
10. whale_activity: High-value movements (14d) - protocols attracting/losing, patterns
11. new_user_onboarding: Best retention (day 7→30) - score progression, sticky products
12. cross_chain_migration: Users moving chains (30d) - patterns, destinations, segments

SHOWCASE (13-15):
13. multi_chain_demo: Same metric across 5+ chains
14. ai_agent_collaboration: Multiple agents working together
15. advanced_query_feature: New capabilities demonstration

SELECTION CRITERIA:
- Different from last 10 topic_id+chain combos, last 32 subjects
- Clean data with dramatic changes (>50% growth/decline ideal)
- Clear narrative (easy to explain WHY it's happening)
- ≥10 data points for timeseries
</topic_selection>

<data_sources>
PRIMARY TABLES:
- datascience_public.{{chain}}.protocol_stats: day_, protocol, n_users, n_quality_users, swap_volume_usd
- datascience_public.{{chain}}.chain_stats: day_, n_active_addresses, n_transactions, gas_used
- datascience_public.{{chain}}.address_labels: address, label, category, protocol
- datascience_public.{{chain}}.fact_event_logs: block_timestamp, contract_address, event_name

SECONDARY: Expert agents, custom SQL, web search for context
</data_sources>

<data_quality_validation>
MANDATORY SQL FILTERS (add to EVERY date query):
WHERE day_ <= CURRENT_DATE AND day_ >= CURRENT_DATE - INTERVAL '[N] days' AND [metric] > 0 ORDER BY day_ DESC

RED FLAGS - REJECT DATA IF:
✗ Future dates (> today)
✗ Dates before chain launch (ETH < 2015)
✗ Negative values (users, volume)
✗ Extreme outliers (1000x normal without reason)
✗ All zeros/NULLs in key metrics
✗ Gaps > 7 days in daily data
✗ Duplicate dates in results

POST-QUERY CHECKLIST (run after EVERY query):
☐ Rows returned: [N]
☐ Latest date: [date] ≤ today?
☐ Date range: [start] to [end] - covers expected period?
☐ No future dates present?
☐ Values reasonable? No extreme outliers?
☐ ≥10 data points for timeseries?
☐ Calculations correct? (%, changes, aggregations)

IF BAD DATA:
1. Re-query with WHERE day_ <= CURRENT_DATE
2. Try different protocol/chain with cleaner data
3. Choose different topic entirely

NEVER proceed with bad data
</data_quality_validation>

<query_strategy>
SCAN → DEEP DIVE → VALIDATE

1. SCAN (2-3 topics quickly):
- Broad aggregation to find interesting patterns
- Look for large changes, dramatic trends
- Check data quality immediately

2. DEEP DIVE (selected topic):
- Daily timeseries: SELECT day_, metrics WHERE day_ <= CURRENT_DATE ORDER BY day_ ASC
- User segmentation: quality users vs. total users
- Volume/activity patterns
- Calculate percentage changes (verify denominators non-zero)

3. VALIDATE:
- Count data points, verify date ranges
- Spot-check values against query results
- Confirm calculations (growth %, changes)
- Ensure narrative is supported by data
</query_strategy>

<execution>
1. CHECK RECENT: Review <recent_prompts>, note recent topics/chains/subjects
2. SCAN: Query 2-3 topics, verify data quality
3. SELECT: Choose topic with strongest data, best narrative, different from recent
4. ANALYZE: Deep dive queries with filters
5. VALIDATE: Run post-query checklist on all results
6. FINDINGS: Document what/why/metrics - complete ALL analysis, queries, and documentation
7. FINAL STEP - CHECKPOINT: ONLY after ALL analysis is 100% complete, output THIS_IS_THE_VALIDATION_CHECKPOINT as the ABSOLUTE LAST LINE (plain text, NOT a header/markdown heading)

CRITICAL: THIS_IS_THE_VALIDATION_CHECKPOINT must be the very last thing you output. Do not output anything after it.
</execution>

<rules>
MUST:
✓ Check recent prompts before selecting
✓ Add WHERE day_ <= CURRENT_DATE to all date queries
✓ Validate every query (run checklist)
✓ Select topic different from recent analyses
✓ Ensure ≥10 data points for timeseries
✓ Calculate % changes with non-zero denominators
✓ Complete ALL analysis, queries, findings, and documentation BEFORE outputting checkpoint
✓ Output THIS_IS_THE_VALIDATION_CHECKPOINT as the ABSOLUTE LAST LINE (plain text paragraph, NOT a header/markdown heading)
✓ Do NOT output anything after THIS_IS_THE_VALIDATION_CHECKPOINT

NEVER:
✗ Use data with future dates
✗ Proceed with <10 points without re-querying
✗ Repeat topic_id+chain from last 10
✗ Repeat subject from last 32
✗ Skip validation checklist
✗ Accept bad data (re-query or change topics)
✗ Format THIS_IS_THE_VALIDATION_CHECKPOINT as a header (h1, h2, h3, ##, ###, etc.)
✗ Output THIS_IS_THE_VALIDATION_CHECKPOINT before completing all analysis
✗ Output anything after THIS_IS_THE_VALIDATION_CHECKPOINT
</rules>"""

    def _get_artifact_prompt_template(self) -> str:
        """Get the static artifact generation phase prompt template (Phase 2)."""
        return """<artifact_protocol>
CRITICAL: generate_artifact() needs explicit instructions in your response.

BEFORE calling, write this declaration:
Creating visualization:
- Data: [N] rows, [start_date] to [end_date]
- Fields: [list key fields from query]
- Chart: [type], X=[field with N points], Y=[metrics]
- Chain: [specific chain/protocol analyzed]
- Colors: #8B5CF6, #EC4899, #06B6D4, #F59E0B, #EF4444, #10B981, #6366F1, #F97316
- Size: 1200x675px
- CRITICAL VALUES FROM QUERY: [list 5-7 specific data points with exact dates and values that MUST appear in artifact]

PRE-GENERATION CHECKLIST:
☐ Data validated: [N] rows, dates [start] to [end], all ≤ today
☐ No NULLs/gaps/zeros/future dates in critical fields
☐ ≥10 data points for timeseries
☐ Declaration written with exact specifications
☐ Critical values from query listed above (these will be verified against artifact output)

AFTER generate_artifact() RETURNS:
1. MANDATORY: Examine the artifact HTML/data that was returned in the function results
2. Extract and verify:
   - Look for the data table/array embedded in the artifact
   - Check if dates match your query results
   - Verify specific values for critical dates (check at least 5 points)
   - Look for any summary text and verify numbers match your query
   - Confirm title/protocol name is correct

POST-GENERATION VERIFICATION CHECKLIST (YOU MUST COMPLETE):
☐ Artifact HTML examined: [Yes/No]
☐ Data table/array found in artifact: [Yes/No]
☐ Critical value check 1: [date] should be [value] → artifact shows [actual value] → [PASS/FAIL]
☐ Critical value check 2: [date] should be [value] → artifact shows [actual value] → [PASS/FAIL]
☐ Critical value check 3: [date] should be [value] → artifact shows [actual value] → [PASS/FAIL]
☐ Critical value check 4: [date] should be [value] → artifact shows [actual value] → [PASS/FAIL]
☐ Critical value check 5: [date] should be [value] → artifact shows [actual value] → [PASS/FAIL]
☐ Date range matches: Expected [start] to [end] → artifact shows [actual range] → [PASS/FAIL]
☐ Point count matches: Expected [N] → artifact has [actual N] → [PASS/FAIL]
☐ Protocol/chain name correct: Expected [name] → artifact shows [actual name] → [PASS/FAIL]
☐ Summary text numbers verified: [list key numbers and whether they match]

VERIFICATION DECISION:
If ANY checks FAIL:
- State clearly what failed
- Regenerate artifact from scratch with corrected instructions
- Re-verify all checks
- Repeat until ALL checks PASS

If ALL checks PASS:
- State: "All verification checks passed"
- Proceed to output requirements

NEVER:
✗ Skip examining the artifact HTML/data
✗ Skip any verification check
✗ Proceed with failed checks
✗ Use update_artifact (always regenerate from scratch)
✗ Claim verification passed without showing actual vs expected values
</artifact_protocol>

<output_requirements>
ONLY after ALL verification checks pass, END response with these THREE elements in exact order (plain text, NO code blocks):

1. TWITTER_TEXT_OUTPUT:
[Topic]:
- [Metric <50 chars]
- [Metric <50 chars]
- [Metric <50 chars]
(Max 260 chars total)

2. CONDENSED_PROMPT_OUTPUT:
{{topic_id}}:{{chain}}:{{subject}}
(Format: 1-15, chain name, 2-4 words, max 50 chars, underscores)

3. THIS_CONCLUDES_THE_ANALYSIS
</output_requirements>

<execution>
1. Write pre-artifact declaration with specifications AND critical values from query
2. Call generate_artifact() ONCE
3. EXAMINE the returned artifact HTML/data structure
4. EXTRACT actual values from the artifact data
5. COMPARE actual vs expected for each critical value check
6. DOCUMENT each check as PASS or FAIL with actual values shown
7. If ANY check fails: Regenerate from scratch and repeat verification
8. If ALL checks pass: State "All verification checks passed"
9. ONLY then: Output TWITTER_TEXT_OUTPUT (plain text)
10. Output CONDENSED_PROMPT_OUTPUT (plain text)
11. Output THIS_CONCLUDES_THE_ANALYSIS
</execution>

<rules>
MUST:
✓ List critical values from your query before generating
✓ Examine the artifact return data after generation
✓ Extract actual values from artifact and compare to expected
✓ Complete ALL verification checks with actual values shown
✓ Regenerate if any check fails (never use update_artifact)
✓ Show your verification work (expected vs actual for each check)
✓ Only proceed to final outputs after stating all checks passed

NEVER:
✗ Generate artifact without listing critical values first
✗ Skip examining the artifact data
✗ Skip any verification check in the checklist
✗ Proceed with failed verification checks
✗ Claim checks passed without showing actual vs expected comparison
✗ Use update_artifact for fixes (always regenerate)
✗ Output final three elements before verification passes
</rules>
"""

    def _inject_recent_prompts_into_template(self, template: str, recent_prompts_list: str) -> str:
        """Inject recent prompts into a custom template.
        
        Replaces {recent_prompts} placeholder with the formatted recent prompts JSON array.
        """
        try:
            # Replace {recent_prompts} placeholder with actual recent prompts list
            if "{recent_prompts}" in template:
                template = template.replace("{recent_prompts}", recent_prompts_list)
                self.logger.log_info(f"✅ Injected recent_prompts into template: {len(recent_prompts_list)} chars")
                return template
            else:
                self.logger.log_warning("⚠️ No {recent_prompts} placeholder found in template")
                return template
        except Exception as e:
            self.logger.log_error(f"❌ Failed to inject recent prompts: {e}")
            return template
    
    def submit_prompt(self, prompt: str = "", phase: int = 1) -> bool:
        """Submit a prompt to the chat.
        
        Args:
            prompt: Original prompt parameter (kept for backward compatibility, currently unused)
            phase: Which phase to use - 1 for analysis phase, 2 for artifact generation phase
        """
        try:
            # Load recent prompts and format for injection
            recent_prompts_list = self._format_recent_prompts_for_prompt()
            self.logger.log_debug(f"📋 Recent prompts formatted: {recent_prompts_list[:200]}..." if len(recent_prompts_list) > 200 else f"📋 Recent prompts formatted: {recent_prompts_list}")
            
            # Determine which template to use
            if phase == 1:
                # Phase 1: Analysis prompt with recent_prompts injection
                template = self._get_analysis_prompt_template()
                self.logger.log_debug(f"📋 Template before injection contains '{{recent_prompts}}': {'{recent_prompts}' in template}")
                full_prompt = self._inject_recent_prompts_into_template(template, recent_prompts_list)
                self.logger.log_debug(f"📋 Template after injection contains '{{recent_prompts}}': {'{recent_prompts}' in full_prompt}")
                self.logger.log_info(f"📝 Using Phase 1 (Analysis) prompt template with recent_prompts injection")
            elif phase == 2:
                # Phase 2: Artifact generation prompt (no recent_prompts needed)
                full_prompt = self._get_artifact_prompt_template()
                self.logger.log_info(f"📝 Using Phase 2 (Artifact Generation) prompt template")
            else:
                raise ValueError(f"Invalid phase: {phase}. Must be 1 or 2.")
            
            
            # Log the full prompt length and verify rules are included
            self.logger.log_info(f"📝 Submitting prompt to chat")
            self.logger.log_info(f"📏 Full prompt length: {len(full_prompt)} characters")
            
            # Save prompt to file for debugging
            try:
                os.makedirs("logs", exist_ok=True)
                prompt_debug_file = f"logs/prompt_sent_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                with open(prompt_debug_file, 'w', encoding='utf-8') as f:
                    f.write(full_prompt)
                self.logger.log_info(f"📄 Full prompt saved to: {prompt_debug_file}")
            except Exception as e:
                self.logger.log_debug(f"Could not save prompt debug file: {e}")
            
            self.logger.log_debug(f"📋 Prompt preview (first 500 chars): {full_prompt[:500]}")
            
            # Phase-specific verification
            if phase == 1:
                # Phase 1 should have topic_selection and validation checkpoint
                if "topic_selection" in full_prompt and "THIS_IS_THE_VALIDATION_CHECKPOINT" in full_prompt:
                    self.logger.log_info("✅ Phase 1 prompt template verified (contains topic_selection, THIS_IS_THE_VALIDATION_CHECKPOINT)")
                else:
                    self.logger.log_warning("⚠️ Phase 1 prompt template verification failed!")
                    self.logger.log_warning(f"   topic_selection: {'topic_selection' in full_prompt}")
                    self.logger.log_warning(f"   THIS_IS_THE_VALIDATION_CHECKPOINT: {'THIS_IS_THE_VALIDATION_CHECKPOINT' in full_prompt}")
                # Verify recent prompts were injected
                if "{recent_prompts}" in full_prompt:
                    self.logger.log_warning("⚠️ Recent prompts were NOT injected - still contains {recent_prompts} placeholder!")
                elif "LAST_32_ANALYSES:" in full_prompt and recent_prompts_list != "[]":
                    self.logger.log_info(f"✅ Recent prompts verified: {recent_prompts_list[:100]}...")
            elif phase == 2:
                # Phase 2 should have artifact protocol and output requirements
                if "TWITTER_TEXT_OUTPUT" in full_prompt and "CONDENSED_PROMPT_OUTPUT" in full_prompt and "THIS_CONCLUDES_THE_ANALYSIS" in full_prompt:
                    self.logger.log_info("✅ Phase 2 prompt template verified (contains TWITTER_TEXT_OUTPUT, CONDENSED_PROMPT_OUTPUT, THIS_CONCLUDES_THE_ANALYSIS)")
                else:
                    self.logger.log_warning("⚠️ Phase 2 prompt template verification failed!")
                    self.logger.log_warning(f"   TWITTER_TEXT_OUTPUT: {'TWITTER_TEXT_OUTPUT' in full_prompt}")
                    self.logger.log_warning(f"   CONDENSED_PROMPT_OUTPUT: {'CONDENSED_PROMPT_OUTPUT' in full_prompt}")
                    self.logger.log_warning(f"   THIS_CONCLUDES_THE_ANALYSIS: {'THIS_CONCLUDES_THE_ANALYSIS' in full_prompt}")
            
            # Wait for page to fully load and chat interface to render
            self.logger.log_info("⏳ Waiting for chat interface to load...")
            time.sleep(5)
            
            # Wait for chat input to appear with explicit wait
            chat_input = None
            max_wait_attempts = 10
            for attempt in range(max_wait_attempts):
                try:
                    # Try comprehensive selectors including contenteditable divs
                    chat_selectors = [
                        "[data-lexical-editor='true']",  # Lexical editor - highest priority
                        "[contenteditable='true'][role='textbox']",  # Contenteditable with textbox role
                        "div[contenteditable='true'][data-lexical-editor='true']",  # Lexical div
                        "textarea[placeholder*='Ask']",
                        "textarea[placeholder*='ask']",
                        "textarea[placeholder*='Message']",
                        "textarea[placeholder*='message']",
                        "textarea[data-testid='chat-input']",
                        "textarea[data-testid='message-input']",
                        "textarea[data-testid='input']",
                        "textarea",
                        "input[type='text'][placeholder*='Ask']",
                        "input[type='text'][placeholder*='message']",
                        "input[placeholder*='Ask']",
                        "input[placeholder*='message']",
                        "div[contenteditable='true']",
                        "div[contenteditable='']",
                        "[contenteditable='true']",
                        "[contenteditable='']",
                        "[role='textbox']",
                        "div[role='textbox']"
                    ]
                    
                    # Also try finding by JavaScript - target Lexical editor specifically
                    try:
                        # Look for Lexical editor (React-based rich text editor)
                        contenteditable_elements = self.driver.execute_script("""
                            // First, try to find the Lexical editor by data attribute
                            const lexicalEditor = document.querySelector('[data-lexical-editor="true"]');
                            if (lexicalEditor) {
                                return [lexicalEditor];
                            }
                            
                            // Fallback: Find contenteditable that has the placeholder as sibling/parent structure
                            const placeholder = Array.from(document.querySelectorAll('div.pointer-events-none.select-none, div.select-none.pointer-events-none')).find(
                                el => el.textContent && el.textContent.trim().length > 0
                            );
                            
                            if (placeholder) {
                                // Find the parent contenteditable div (Lexical editor is usually sibling or parent)
                                let parent = placeholder.parentElement;
                                while (parent && parent !== document.body) {
                                    if (parent.contentEditable === 'true' || 
                                        parent.getAttribute('contenteditable') === 'true' || 
                                        parent.getAttribute('role') === 'textbox' ||
                                        parent.getAttribute('data-lexical-editor') === 'true') {
                                        return [parent];
                                    }
                                    parent = parent.parentElement;
                                }
                            }
                            
                            // Final fallback: Find all contenteditable elements with role="textbox"
                            const allContentEditable = Array.from(document.querySelectorAll('[contenteditable="true"][role="textbox"], [data-lexical-editor="true"]'));
                            
                            // Filter for visible, interactive elements
                            const visible = allContentEditable.filter(el => {
                                const style = window.getComputedStyle(el);
                                const rect = el.getBoundingClientRect();
                                return style.display !== 'none' && 
                                       style.visibility !== 'hidden' && 
                                       rect.height > 0 && 
                                       rect.width > 0 &&
                                       !el.classList.contains('pointer-events-none') &&
                                       !el.classList.contains('select-none');
                            });
                            
                            return visible;
                        """)
                        
                        if contenteditable_elements and len(contenteditable_elements) > 0:
                            # Use the first candidate (most likely the chat input)
                            elem = contenteditable_elements[0]
                            # Store element reference in window and find it via Selenium
                            try:
                                # Store the element reference
                                self.driver.execute_script("window.__chatInputElement = arguments[0];", elem)
                                
                                # Get element attributes to find it via Selenium
                                tag = self.driver.execute_script("return arguments[0].tagName.toLowerCase();", elem)
                                classes = self.driver.execute_script("return arguments[0].className;", elem) or ""
                                
                                # Try finding by CSS selector using classes
                                if classes:
                                    # Use the first class that doesn't contain 'pointer-events' or 'select'
                                    class_list = [c for c in classes.split() if 'pointer' not in c.lower() and 'select' not in c.lower()]
                                    if class_list:
                                        # Try finding by class
                                        for class_name in class_list[:3]:  # Try first 3 classes
                                            try:
                                                elements = self.driver.find_elements(By.CSS_SELECTOR, f"{tag}.{class_name}")
                                                for el in elements:
                                                    if el.is_displayed():
                                                        # Verify it's contenteditable
                                                        if el.get_attribute("contenteditable"):
                                                            chat_input = el
                                                            self.logger.log_info(f"✅ Found chat input via class selector: {class_name}")
                                                            break
                                                if chat_input:
                                                    break
                                            except:
                                                continue
                                
                                # If still not found, try finding all contenteditable divs and pick the right one
                                if not chat_input:
                                    all_contenteditable = self.driver.find_elements(By.CSS_SELECTOR, "[contenteditable='true'], [contenteditable='']")
                                    for el in all_contenteditable:
                                        if el.is_displayed():
                                            # Check if it has the placeholder child
                                            try:
                                                placeholder = el.find_elements(By.CSS_SELECTOR, ".pointer-events-none, .select-none")
                                                if placeholder or el.size['height'] > 50:
                                                    chat_input = el
                                                    self.logger.log_info("✅ Found chat input via contenteditable selector")
                                                    break
                                            except:
                                                pass
                                
                                if chat_input:
                                    break
                            except Exception as e:
                                self.logger.log_debug(f"Failed to find element via attributes: {e}")
                                pass
                    except Exception as js_error:
                        self.logger.log_debug(f"JavaScript search failed: {js_error}")
                    
                    for selector in chat_selectors:
                        try:
                            elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                            for element in elements:
                                if element and element.is_displayed() and element.is_enabled():
                                    # Check if it's actually a chat input (not hidden/file input)
                                    tag = element.tag_name.lower()
                                    inp_type = element.get_attribute("type") or ""
                                    if tag == "textarea" or (tag == "input" and inp_type in ["text", ""]):
                                        chat_input = element
                                        self.logger.log_info(f"✅ Found chat input with selector: {selector}")
                                        break
                            if chat_input:
                                break
                        except:
                            continue
                    
                    if chat_input:
                        break
                        
                    if attempt < max_wait_attempts - 1:
                        self.logger.log_info(f"⏳ Chat input not found yet, waiting... (attempt {attempt + 1}/{max_wait_attempts})")
                        time.sleep(2)
                except Exception as e:
                    self.logger.log_warning(f"Error searching for chat input: {e}")
                    time.sleep(2)
            
            # If chat_input wasn't found, debug and return error
            if not chat_input:
                # Debug: List all input and textarea elements
                try:
                    all_inputs = self.driver.find_elements(By.TAG_NAME, "input")
                    all_textareas = self.driver.find_elements(By.TAG_NAME, "textarea")
                    self.logger.log_info(f"🔍 Found {len(all_inputs)} input elements and {len(all_textareas)} textarea elements")
                    
                    for i, elem in enumerate(all_inputs + all_textareas):
                        try:
                            elem_type = elem.get_attribute("type") or elem.tag_name
                            elem_placeholder = elem.get_attribute("placeholder") or "unknown"
                            elem_id = elem.get_attribute("id") or "unknown"
                            elem_class = elem.get_attribute("class") or "unknown"
                            elem_data_testid = elem.get_attribute("data-testid") or "unknown"
                            is_displayed = elem.is_displayed()
                            is_enabled = elem.is_enabled()
                            self.logger.log_info(f"   Element {i}: {elem_type}, placeholder='{elem_placeholder}', id='{elem_id}', class='{elem_class}', data-testid='{elem_data_testid}', displayed={is_displayed}, enabled={is_enabled}")
                        except:
                            pass
                except Exception as e:
                    self.logger.log_warning(f"Could not enumerate elements: {e}")
                
                # Take screenshot for debugging
                self.driver.save_screenshot("screenshots/chat_page_before_input.png")
                self.logger.log_info("📸 Chat page screenshot saved for debugging")
                
                self.logger.log_error("❌ Chat input not found after waiting")
                return False
            
            # Clear and type prompt
            self.logger.log_info("⌨️ Typing prompt into chat input")
            
            # Check if it's a contenteditable div or regular input/textarea
            tag_name = chat_input.tag_name.lower() if hasattr(chat_input, 'tag_name') else ""
            is_contenteditable = chat_input.get_attribute("contenteditable") if hasattr(chat_input, 'get_attribute') else None
            
            if tag_name == "div" or is_contenteditable:
                # Use JavaScript to set content for contenteditable divs
                self.logger.log_info("📝 Using JavaScript to set content (contenteditable div)")
                try:
                    # First, click to focus the element
                    self.driver.execute_script("arguments[0].focus();", chat_input)
                    self.driver.execute_script("arguments[0].click();", chat_input)
                    time.sleep(0.5)
                    
                    # Clear any existing content
                    self.driver.execute_script("arguments[0].innerHTML = '';", chat_input)
                    self.driver.execute_script("arguments[0].innerText = '';", chat_input)
                    self.driver.execute_script("arguments[0].textContent = '';", chat_input)
                    time.sleep(0.3)
                    
                    # Set the new content using JavaScript - optimized for Lexical editor
                    self.logger.log_info(f"📝 Setting full prompt ({len(full_prompt)} chars) via JavaScript...")
                    
                    # Use a comprehensive JavaScript approach optimized for Lexical editor
                    actual_content = self.driver.execute_script("""
                        const el = arguments[0];
                        const text = arguments[1];
                        
                        // Focus the element first
                        el.focus();
                        el.click();
                        
                        // Clear any existing content
                        // For Lexical, we need to select all and delete
                        const selection = window.getSelection();
                        const range = document.createRange();
                        range.selectNodeContents(el);
                        selection.removeAllRanges();
                        selection.addRange(range);
                        
                        // Delete existing content
                        document.execCommand('delete', false, null);
                        
                        // Clear innerHTML/textContent
                        el.innerHTML = '';
                        el.innerText = '';
                        el.textContent = '';
                        
                        // For Lexical editor, we need to insert text properly
                        // Try using execCommand insertText first (works with Lexical)
                        if (document.execCommand('insertText', false, text)) {
                            // Success! Now dispatch events
                            el.dispatchEvent(new Event('input', { bubbles: true, cancelable: true }));
                            el.dispatchEvent(new Event('change', { bubbles: true, cancelable: true }));
                        } else {
                            // Fallback: Direct text setting
                            el.textContent = text;
                            el.innerText = text;
                            
                            // Create a text node
                            const textNode = document.createTextNode(text);
                            el.appendChild(textNode);
                            
                            // Dispatch all necessary events for Lexical
                            el.dispatchEvent(new Event('input', { bubbles: true, cancelable: true }));
                            el.dispatchEvent(new Event('change', { bubbles: true, cancelable: true }));
                            el.dispatchEvent(new Event('keyup', { bubbles: true, cancelable: true }));
                            el.dispatchEvent(new Event('keydown', { bubbles: true, cancelable: true }));
                            
                            // React/Lexical specific events
                            const inputEvent = new Event('input', { bubbles: true, cancelable: true });
                            Object.defineProperty(inputEvent, 'target', { value: el, enumerable: true });
                            el.dispatchEvent(inputEvent);
                        }
                        
                        // Also update the hidden input if it exists (often used by forms)
                        const hiddenInput = el.closest('form')?.querySelector('input[type="hidden"][name="content"]');
                        if (hiddenInput) {
                            hiddenInput.value = text;
                        }
                        
                        // Return the actual content to verify
                        return el.textContent || el.innerText || '';
                    """, chat_input, full_prompt)
                    
                    # Note: Lexical editor may store content in a different DOM structure
                    # The verification might not read the actual content correctly, but the submission works
                    # We've already set the full_prompt via execCommand or direct setting, so trust it was set
                    self.logger.log_info(f"✅ Content inserted into Lexical editor ({len(full_prompt)} chars)")
                    self.logger.log_info("✅ Full prompt with rules has been set and will be submitted")
                    
                    time.sleep(1)
                    self.logger.log_info("✅ Content set via JavaScript")
                except Exception as js_error:
                    self.logger.log_warning(f"JavaScript input failed, trying send_keys: {js_error}")
                    try:
                        chat_input.click()
                        time.sleep(0.5)
                        # Clear first
                        chat_input.send_keys(Keys.CONTROL + "a")
                        time.sleep(0.2)
                        chat_input.send_keys(full_prompt)
                    except Exception as send_error:
                        self.logger.log_error(f"Both JavaScript and send_keys failed: {send_error}")
                        raise
            else:
                # Regular input/textarea
                try:
                    chat_input.clear()
                except:
                    pass
                time.sleep(0.5)
                chat_input.click()
                time.sleep(0.5)
                chat_input.send_keys(full_prompt)
            
            time.sleep(2)
            
            # Submit using JavaScript to avoid stale element issues
            self.logger.log_info("📤 Submitting prompt")
            try:
                # Use JavaScript to submit - more reliable for contenteditable divs
                self.driver.execute_script("""
                    // Find the active contenteditable input
                    const inputs = Array.from(document.querySelectorAll('[contenteditable="true"], [contenteditable=""]'));
                    const activeInput = inputs.find(el => {
                        const style = window.getComputedStyle(el);
                        return style.display !== 'none' && 
                               style.visibility !== 'hidden' && 
                               el.offsetHeight > 0 && 
                               el.offsetWidth > 0 &&
                               !el.classList.contains('pointer-events-none');
                    });
                    
                    if (activeInput) {
                        // Focus the input first
                        activeInput.focus();
                        
                        // Dispatch Enter key events
                        const enterEvent = new KeyboardEvent('keydown', {
                            key: 'Enter',
                            code: 'Enter',
                            keyCode: 13,
                            which: 13,
                            bubbles: true,
                            cancelable: true
                        });
                        activeInput.dispatchEvent(enterEvent);
                        
                        // Also try keypress and keyup
                        activeInput.dispatchEvent(new KeyboardEvent('keypress', {
                            key: 'Enter',
                            code: 'Enter',
                            keyCode: 13,
                            which: 13,
                            bubbles: true,
                            cancelable: true
                        }));
                        
                        activeInput.dispatchEvent(new KeyboardEvent('keyup', {
                            key: 'Enter',
                            code: 'Enter',
                            keyCode: 13,
                            which: 13,
                            bubbles: true,
                            cancelable: true
                        }));
                    }
                """)
                time.sleep(1)
                
                # Fallback: try send_keys only for regular inputs/textarea (not contenteditable)
                if tag_name != "div" and not is_contenteditable:
                    try:
                        if chat_input and hasattr(chat_input, 'send_keys'):
                            chat_input.send_keys("\n")
                    except Exception as send_error:
                        self.logger.log_debug(f"Send_keys fallback failed: {send_error}")
                    
            except Exception as submit_error:
                self.logger.log_error(f"❌ Prompt submission failed: {submit_error}")
                raise
            time.sleep(2)
            
            self.logger.log_success("✅ Prompt submitted successfully")
            return True
            
        except Exception as e:
            self.logger.log_error(f"Prompt submission failed: {e}")
            return False
    
    def _is_user_message(self, element) -> bool:
        """Check if an element is part of a user message (not assistant response)."""
        try:
            # Use JavaScript to traverse up the DOM tree and check for data-message-role="user"
            script = """
            var element = arguments[0];
            var current = element;
            var maxDepth = 10;
            var depth = 0;
            
            while (current && depth < maxDepth) {
                var role = current.getAttribute('data-message-role');
                if (role === 'user') {
                    return true;
                }
                // Also check if element is inside a container with data-message-role="user"
                var parent = current.parentElement;
                if (!parent) break;
                current = parent;
                depth++;
            }
            return false;
            """
            is_user = self.driver.execute_script(script, element)
            return bool(is_user)
        except Exception as e:
            # If JavaScript check fails, fallback to checking the element directly
            try:
                role = element.get_attribute("data-message-role")
                if role == "user":
                    return True
            except:
                pass
            return False
    
    def _extract_twitter_text_after_conclusion(self) -> str:
        """Extract Twitter text right after conclusion marker is found.
        
        The Twitter text is formatted like:
        TWITTER_TEXT:
        
        XXXXXXX
        
        THIS_CONCLUDES_THE_ANALYSIS
        """
        try:
            self.logger.log_info("🔍 Extracting Twitter text from page content...")
            
            # Get the page text content
            try:
                page_text = self.driver.find_element(By.TAG_NAME, "body").text
            except:
                # Fallback: try to get text from the main content area
                try:
                    page_text = self.driver.find_element(By.CSS_SELECTOR, "main, .main, .content, .chat-content").text
                except:
                    self.logger.log_warning("⚠️ Could not get page text")
                    return ""
            
            # Look for the pattern: TWITTER_TEXT: ... THIS_CONCLUDES_THE_ANALYSIS
            lines = page_text.split('\n')
            twitter_content = ""
            found_twitter_text_marker = False
            collecting_content = False
            
            for i, line in enumerate(lines):
                line_stripped = line.strip()
                
                # Look for TWITTER_TEXT: marker
                if "TWITTER_TEXT:" in line_stripped:
                    found_twitter_text_marker = True
                    collecting_content = True
                    # Extract content after "TWITTER_TEXT:"
                    twitter_part = line_stripped.split("TWITTER_TEXT:")[-1].strip()
                    if twitter_part:
                        twitter_content += twitter_part + "\n"
                    continue
                
                # If we're collecting content and haven't hit the conclusion marker yet
                if collecting_content and found_twitter_text_marker:
                    # Stop at conclusion marker
                    if ("THIS_CONCLUDES_THE_ANALYSIS" in line_stripped or 
                        "**THIS_CONCLUDES_THE_ANALYSIS**" in line_stripped):
                        break
                    
                    # Skip empty lines at the start
                    if not twitter_content and not line_stripped:
                        continue
                    
                    # Collect the content (skip markdown headers and formatting)
                    if line_stripped and not line_stripped.startswith("**") and not line_stripped.startswith("##"):
                        # Preserve bullet points
                        if line_stripped.startswith(("•", "-", "*", "◦", "▪", "▫")):
                            twitter_content += line_stripped + "\n"
                        else:
                            twitter_content += line_stripped + " "
            
            if twitter_content.strip():
                # Clean up the Twitter text
                clean_twitter_text = twitter_content.strip()
                
                # Remove any remaining "TWITTER_TEXT:" prefix
                if clean_twitter_text.startswith("TWITTER_TEXT:"):
                    clean_twitter_text = clean_twitter_text[12:].strip()
                
                # Remove emoji
                clean_twitter_text = re.sub(r'[\ud83c-\udbff\udc00-\udfff]', '', clean_twitter_text).strip()
                
                # Normalize bullet points
                lines = clean_twitter_text.split('\n')
                normalized_lines = []
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    # Normalize bullet points to use "• "
                    if line.startswith(("-", "*")):
                        line = "• " + line[1:].strip()
                    elif line.startswith(("◦", "▪", "▫")):
                        line = "• " + line[1:].strip()
                    elif line.startswith("•") and not line.startswith("• "):
                        line = "• " + line[1:].strip()
                    normalized_lines.append(line)
                
                clean_twitter_text = '\n'.join(normalized_lines)
                
                if is_placeholder_twitter_text(clean_twitter_text):
                    self.logger.log_warning("⚠️ Extracted Twitter text matches prompt template, retrying...")
                else:
                    self.logger.log_success(f"✅ Extracted Twitter text: {len(clean_twitter_text)} characters")
                    return clean_twitter_text
            
            # Fallback: Try to find Twitter text using XPath selectors
            self.logger.log_info("🔍 Trying XPath selectors for Twitter text...")
            twitter_selectors = [
                "//div[contains(text(), 'TWITTER_TEXT:') and not(ancestor::*[@data-message-role='user'])]",
                "//span[contains(text(), 'TWITTER_TEXT:') and not(ancestor::*[@data-message-role='user'])]",
                "//p[contains(text(), 'TWITTER_TEXT:') and not(ancestor::*[@data-message-role='user'])]",
            ]
            
            for selector in twitter_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    for element in elements:
                        if self._is_user_message(element):
                            continue
                        if element.is_displayed() and element.text.strip():
                            text_content = element.text.strip()
                            if "TWITTER_TEXT:" in text_content:
                                # Extract content between TWITTER_TEXT: and THIS_CONCLUDES_THE_ANALYSIS
                                lines = text_content.split('\n')
                                twitter_content = ""
                                collecting = False
                                
                                for line in lines:
                                    if "TWITTER_TEXT:" in line:
                                        collecting = True
                                        twitter_part = line.split("TWITTER_TEXT:")[-1].strip()
                                        if twitter_part:
                                            twitter_content += twitter_part + "\n"
                                    elif collecting:
                                        if "THIS_CONCLUDES_THE_ANALYSIS" in line:
                                            break
                                        if line.strip() and not line.strip().startswith("**") and not line.strip().startswith("##"):
                                            if line.strip().startswith(("•", "-", "*")):
                                                twitter_content += line.strip() + "\n"
                                            else:
                                                twitter_content += line.strip() + " "
                                
                                if twitter_content.strip():
                                    clean_twitter_text = twitter_content.strip()
                                    if clean_twitter_text.startswith("TWITTER_TEXT:"):
                                        clean_twitter_text = clean_twitter_text[12:].strip()
                                    clean_twitter_text = re.sub(r'[\ud83c-\udbff\udc00-\udfff]', '', clean_twitter_text).strip()
                                    if is_placeholder_twitter_text(clean_twitter_text):
                                        self.logger.log_warning("⚠️ XPath Twitter text matches prompt template, continuing search...")
                                    else:
                                        self.logger.log_success(f"✅ Extracted Twitter text via XPath: {len(clean_twitter_text)} characters")
                                        return clean_twitter_text
                except Exception as e:
                    self.logger.log_debug(f"XPath selector {selector} failed: {e}")
                    continue
            
            self.logger.log_warning("⚠️ Twitter text not found")
            return ""
            
        except Exception as e:
            self.logger.log_error(f"Twitter text extraction failed: {e}")
            return ""
    
    def wait_for_response(self, timeout: int = 600) -> bool:
        """Wait for complete AI response including charts and visualizations."""
        try:
            self.logger.log_info(f"⏳ Waiting for complete AI response (timeout: {timeout}s)")
            
            start_time = time.time()
            response_complete = False
            capture_after_3min = False
            response_started = False
            chat_input_was_disabled = False
            
            while time.time() - start_time < timeout:
                try:
                    # Look for the new analysis conclusion marker (excluding user messages)
                    conclusion_found = False
                    conclusion_selectors = [
                        "//div[contains(text(), 'THIS_CONCLUDES_THE_ANALYSIS') and not(ancestor::*[@data-message-role='user'])]",
                        "//div[contains(text(), '**THIS_CONCLUDES_THE_ANALYSIS**') and not(ancestor::*[@data-message-role='user'])]",
                        "//span[contains(text(), 'THIS_CONCLUDES_THE_ANALYSIS') and not(ancestor::*[@data-message-role='user'])]",
                        "//p[contains(text(), 'THIS_CONCLUDES_THE_ANALYSIS') and not(ancestor::*[@data-message-role='user'])]"
                    ]
                    
                    for selector in conclusion_selectors:
                        try:
                            elements = self.driver.find_elements(By.XPATH, selector)
                            for element in elements:
                                if element.is_displayed() and element.text.strip():
                                    # Check if this is a user message - if so, skip it
                                    if self._is_user_message(element):
                                        self.logger.log_debug("Skipping conclusion marker in user message")
                                        continue
                                    conclusion_found = True
                                    self.logger.log_success("Analysis conclusion marker found!")
                                    break
                            if conclusion_found:
                                break
                        except:
                            continue
                    
                    # Look for Twitter text output (indicates response started) - excluding user messages
                    twitter_found = False
                    twitter_selectors = [
                        "//div[contains(text(), 'TWITTER_TEXT:') and not(ancestor::*[@data-message-role='user'])]",
                        "//div[contains(text(), 'Add a quick 260 character summary') and not(ancestor::*[@data-message-role='user'])]",
                        "[data-testid='twitter-text']:not([data-message-role='user']), [data-testid='twitter-text']:not(:has([data-message-role='user']))",
                        ".twitter-text:not([data-message-role='user'])",
                        ".twitter-output:not([data-message-role='user'])"
                    ]
                    
                    for selector in twitter_selectors:
                        try:
                            if selector.startswith('//'):
                                elements = self.driver.find_elements(By.XPATH, selector)
                            else:
                                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                            for element in elements:
                                if element.is_displayed() and element.text.strip():
                                    # Check if this is a user message - if so, skip it
                                    if self._is_user_message(element):
                                        self.logger.log_debug("Skipping Twitter text in user message")
                                        continue
                                    twitter_found = True
                                    self.logger.log_success("Twitter text output found")
                                    break
                            if twitter_found:
                                break
                        except:
                            continue
                    
                    # Look for charts/visualizations on the right panel
                    chart_selectors = [
                        ".chart-container",
                        ".visualization-panel",
                        ".report-panel",
                        "[data-testid='chart']",
                        "canvas",
                        "svg",
                        ".highcharts-container"
                    ]
                    
                    charts_found = False
                    for selector in chart_selectors:
                        try:
                            elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                            for element in elements:
                                if element.is_displayed() and element.size['width'] > 100 and element.size['height'] > 100:
                                    charts_found = True
                                    self.logger.log_success("Charts/visualizations found")
                                    break
                            if charts_found:
                                break
                        except:
                            continue
                    
                    # Check if we need to click "View Report" button to show visuals
                    self._click_view_report_buttons()
                    
                    # Check if we should capture results after 3 minutes
                    elapsed = int(time.time() - start_time)
                    if elapsed >= 180 and not capture_after_3min:  # 3 minutes
                        self.logger.log_info("3 minutes elapsed - will capture results regardless of completion")
                        capture_after_3min = True
                    
                    # Check if chat input is editable again (indicates response is complete)
                    chat_input_editable = False
                    try:
                        chat_input = self._find_chat_input()
                        if chat_input and chat_input.is_displayed() and chat_input.is_enabled():
                            chat_input_editable = True
                    except Exception as e:
                        # Handle stale element reference
                        if "stale element" in str(e).lower():
                            continue
                    
                    # Response is complete if we found the conclusion marker
                    if conclusion_found:
                        self.logger.log_success("Analysis conclusion marker found - response complete!")
                        # Extract Twitter text right after conclusion marker is found
                        self.logger.log_info("🐦 Extracting Twitter text right after conclusion marker...")
                        self.extracted_twitter_text = self._extract_twitter_text_after_conclusion()
                        if self.extracted_twitter_text:
                            self.logger.log_success(f"✅ Twitter text extracted: {len(self.extracted_twitter_text)} characters")
                        else:
                            self.logger.log_warning("⚠️ Twitter text not found after conclusion marker")
                        response_complete = True
                        break
                    # Response is complete if chat input is editable again
                    elif chat_input_editable and (twitter_found or charts_found):
                        self.logger.log_success("Chat input is editable - response complete!")
                        response_complete = True
                        break
                    # Fallback: Response is complete if we have both Twitter text and charts
                    elif twitter_found and charts_found:
                        self.logger.log_success("Complete response received with charts")
                        response_complete = True
                        break
                    elif twitter_found:
                        # We have text but waiting for charts
                        self.logger.log_info(f"Text received, waiting for charts... ({elapsed}s elapsed)")
                        time.sleep(5)
                    else:
                        # Still waiting for any response
                        self.logger.log_info(f"Waiting for response... ({elapsed}s elapsed)")
                        time.sleep(5)
                        
                except Exception as e:
                    self.logger.log_warning(f"Error checking for response: {e}")
                    time.sleep(5)
            
            # If we exit the while loop due to timeout
            if not response_complete:
                self.logger.log_warning(f"Complete response not received within {timeout} seconds")
                if capture_after_3min:
                    self.logger.log_info("Proceeding with partial results capture")
                return False
            
            return True
            
        except Exception as e:
            self.logger.log_error(f"Failed to wait for complete response: {e}")
            return False
    
    def wait_for_checkpoint(self, timeout: int = 600) -> bool:
        """Wait for validation checkpoint marker: THIS_IS_THE_VALIDATION_CHECKPOINT."""
        try:
            self.logger.log_info(f"⏳ Waiting for validation checkpoint (timeout: {timeout}s)")
            
            start_time = time.time()
            checkpoint_found = False
            
            while time.time() - start_time < timeout:
                try:
                    # Look for the validation checkpoint marker (excluding user messages)
                    # Include headers (h1, h2, h3) in case AI outputs it as a header
                    checkpoint_selectors = [
                        "//div[contains(text(), 'THIS_IS_THE_VALIDATION_CHECKPOINT') and not(ancestor::*[@data-message-role='user'])]",
                        "//div[contains(text(), '**THIS_IS_THE_VALIDATION_CHECKPOINT**') and not(ancestor::*[@data-message-role='user'])]",
                        "//span[contains(text(), 'THIS_IS_THE_VALIDATION_CHECKPOINT') and not(ancestor::*[@data-message-role='user'])]",
                        "//p[contains(text(), 'THIS_IS_THE_VALIDATION_CHECKPOINT') and not(ancestor::*[@data-message-role='user'])]",
                        "//h1[contains(text(), 'THIS_IS_THE_VALIDATION_CHECKPOINT') and not(ancestor::*[@data-message-role='user'])]",
                        "//h2[contains(text(), 'THIS_IS_THE_VALIDATION_CHECKPOINT') and not(ancestor::*[@data-message-role='user'])]",
                        "//h3[contains(text(), 'THIS_IS_THE_VALIDATION_CHECKPOINT') and not(ancestor::*[@data-message-role='user'])]",
                        "//h4[contains(text(), 'THIS_IS_THE_VALIDATION_CHECKPOINT') and not(ancestor::*[@data-message-role='user'])]"
                    ]
                    
                    for selector in checkpoint_selectors:
                        try:
                            elements = self.driver.find_elements(By.XPATH, selector)
                            for element in elements:
                                if element.is_displayed() and element.text.strip():
                                    # Check if this is a user message - if so, skip it
                                    if self._is_user_message(element):
                                        self.logger.log_debug("Skipping checkpoint marker in user message")
                                        continue
                                    checkpoint_found = True
                                    self.logger.log_success("✅ Validation checkpoint marker found!")
                                    break
                            if checkpoint_found:
                                break
                        except:
                            continue
                    
                    if checkpoint_found:
                        break
                    
                    # Check elapsed time
                    elapsed = int(time.time() - start_time)
                    self.logger.log_info(f"Waiting for checkpoint... ({elapsed}s elapsed)")
                    time.sleep(5)
                        
                except Exception as e:
                    self.logger.log_warning(f"Error checking for checkpoint: {e}")
                    time.sleep(5)
            
            if not checkpoint_found:
                self.logger.log_warning(f"Validation checkpoint not found within {timeout} seconds")
                return False
            
            return True
            
        except Exception as e:
            self.logger.log_error(f"Failed to wait for checkpoint: {e}")
            return False
    
    def extract_data(self) -> Dict[str, Any]:
        """Extract all data from the chat response with comprehensive capture."""
        try:
            self.logger.log_info("📊 Extracting chat data")
            
            # Use the chat data extractor for better extraction
            # DO NOT call extract_shareable_link() - it clicks share buttons!
            from modules.chat_manager.chat_data_extractor import ChatDataExtractor
            extractor = ChatDataExtractor()
            
            # Pass the existing driver to avoid creating a new session
            extractor.driver = self.driver
            extractor.authenticator = self.authenticator
            
            # Extract data using the specialized extractor (will use existing driver)
            # Use current URL directly - extractor will handle artifact extraction
            # Pass pre-extracted Twitter text to avoid duplicate extraction
            extraction_result = extractor.extract_from_chat_url(
                self.driver.current_url, 
                pre_extracted_twitter_text=self.extracted_twitter_text
            )
            
            if extraction_result["success"]:
                # Add artifact screenshot if available
                artifact_screenshot_path = extraction_result.get("artifact_screenshot", "")
                
                # Use pre-extracted Twitter text if available (extracted right after conclusion marker)
                twitter_text = self.extracted_twitter_text if self.extracted_twitter_text else extraction_result["twitter_text"]
                if twitter_text and is_placeholder_twitter_text(twitter_text):
                    self.logger.log_warning("⚠️ Twitter text matches prompt template, triggering fallback extraction")
                    twitter_text = ""
                if not twitter_text:
                    self.logger.log_warning("⚠️ Twitter text empty after specialized extractor, attempting fallback from page")
                    twitter_text = self._extract_twitter_text_after_conclusion()
                    if twitter_text:
                        self.logger.log_success(f"✅ Recovered Twitter text via fallback: {len(twitter_text)} characters")
                    else:
                        self.logger.log_warning("⚠️ Fallback Twitter text recovery failed")
                
                results = {
                    "timestamp": datetime.now().isoformat(),
                    "chat_url": self.driver.current_url,
                    "artifact_url": extraction_result.get("artifact_url", ""),
                    "response_text": extraction_result["response_text"],
                    "twitter_text": twitter_text,
                    "artifacts": [],
                    "screenshots": extraction_result.get("screenshots", []),
                    "artifact_screenshot": artifact_screenshot_path,  # Preserve for fallback
                    "response_metadata": {},
                    "condensed_prompt": extraction_result.get("condensed_prompt", "")
                }
                
                # Add artifact screenshot to artifacts list if available
                if artifact_screenshot_path and artifact_screenshot_path.strip() and os.path.exists(artifact_screenshot_path):
                    artifact_info = {
                        "type": "analysis_artifact",
                        "index": 1,
                        "screenshot": artifact_screenshot_path,
                        "selector": "artifact_page",
                        "tag_name": "page"
                    }
                    results["artifacts"].append(artifact_info)
                    if artifact_screenshot_path not in results["screenshots"]:
                        results["screenshots"].append(artifact_screenshot_path)
                    self.logger.log_info(f"✅ Added artifact screenshot to results: {artifact_screenshot_path}")
                    self.logger.log_info(f"📊 Results now contain {len(results['artifacts'])} artifacts")
                else:
                    self.logger.log_warning(f"⚠️ Artifact screenshot not found or invalid: {artifact_screenshot_path}")
                
                if results["twitter_text"] and is_placeholder_twitter_text(results["twitter_text"]):
                    self.logger.log_warning("⚠️ Final Twitter text still matches prompt template, clearing value")
                    results["twitter_text"] = ""
                
                # Save condensed prompt if extracted
                condensed_prompt = results.get("condensed_prompt", "")
                if condensed_prompt and condensed_prompt.strip():
                    self._save_recent_prompt(condensed_prompt)
                    self.logger.log_info(f"✅ Saved condensed prompt to recent prompts: {condensed_prompt}")
                else:
                    self.logger.log_warning("⚠️ No condensed prompt found in extraction results")
                
                self.logger.log_success(f"✅ Data extracted using specialized extractor: {len(results['twitter_text'])} chars Twitter, {len(results['response_text'])} chars response")
                return results
            
            # Fallback to original extraction if specialized extractor fails
            self.logger.log_warning("⚠️ Specialized extractor failed, using fallback extraction")
            
            # Use pre-extracted Twitter text if available
            twitter_text = self.extracted_twitter_text if self.extracted_twitter_text else ""
            
            results = {
                "timestamp": datetime.now().isoformat(),
                "chat_url": self.driver.current_url,
                "response_text": "",
                "twitter_text": twitter_text,
                "artifacts": [],
                "screenshots": [],
                "response_metadata": {},
                "condensed_prompt": ""
            }
            
            if not results["twitter_text"]:
                self.logger.log_warning("⚠️ Fallback extractor missing Twitter text, attempting page scrape")
                recovered_text = self._extract_twitter_text_after_conclusion()
                if recovered_text:
                    results["twitter_text"] = recovered_text
                    self.logger.log_success(f"✅ Recovered Twitter text during fallback path: {len(recovered_text)} characters")
            
            # First try to use the copy button to get the full response
            copy_button_found = self._try_copy_response()
            if copy_button_found:
                # Try to get text from clipboard
                try:
                    from selenium.webdriver.common.keys import Keys
                    # Use Ctrl+A to select all, then Ctrl+C to copy
                    self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.CONTROL + "a")
                    time.sleep(0.5)
                    self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.CONTROL + "c")
                    time.sleep(0.5)
                except:
                    pass
            
            # Extract Twitter text output with new format (excluding user messages)
            twitter_selectors = [
                "//div[contains(text(), 'TWITTER_TEXT:') and not(ancestor::*[@data-message-role='user'])]",
                "//div[contains(text(), 'Add a quick 260 character summary') and not(ancestor::*[@data-message-role='user'])]",
                "//div[contains(text(), 'TWITTER_TEXT') and not(ancestor::*[@data-message-role='user'])]",
                "//div[contains(text(), '**TWITTER_TEXT**') and not(ancestor::*[@data-message-role='user'])]"
            ]
            
            for selector in twitter_selectors:
                try:
                    if selector.startswith('//'):
                        elements = self.driver.find_elements(By.XPATH, selector)
                    else:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for i, element in enumerate(elements):
                        # Skip user messages - only process assistant responses
                        if self._is_user_message(element):
                            continue
                            
                        if element.is_displayed() and element.text.strip():
                            text_content = element.text.strip()
                            
                            # Look for new Twitter text format: "TWITTER_TEXT: [content]"
                            if "TWITTER_TEXT:" in text_content:
                                # Extract content after "TWITTER_TEXT:"
                                lines = text_content.split('\n')
                                twitter_content = ""
                                
                                for line in lines:
                                    if "TWITTER_TEXT:" in line:
                                        # Extract everything after "TWITTER_TEXT:"
                                        twitter_part = line.split("TWITTER_TEXT:")[1].strip()
                                        if twitter_part:
                                            twitter_content += twitter_part + " "
                                    elif twitter_content and line.strip():
                                        # Continue collecting until we hit a section break
                                        if (line.startswith("**THIS_CONCLUDES_THE_ANALYSIS**") or
                                            line.startswith("THIS_CONCLUDES_THE_ANALYSIS") or
                                            line.startswith("HTML_CHART") or 
                                            line.startswith("**HTML_CHART**") or
                                            line.startswith("View Report") or
                                            line.startswith("Based on my comprehensive analysis")):
                                            break
                                        # Skip empty lines and section headers
                                        if line.strip() and not line.startswith("**") and not line.startswith("##"):
                                            twitter_content += line.strip() + " "
                                
                                if twitter_content.strip():
                                    clean_twitter_text = twitter_content.strip()
                                    if is_placeholder_twitter_text(clean_twitter_text):
                                        self.logger.log_warning("⚠️ New-format Twitter text matches prompt template, continuing search...")
                                        continue
                                    results["twitter_text"] = clean_twitter_text
                                    results["response_text"] = clean_twitter_text
                                    self.logger.log_success(f"Extracted Twitter text: {len(results['twitter_text'])} characters")
                                    break
                            
                            # Look for old TWITTER_TEXT format as fallback
                            elif "TWITTER_TEXT" in text_content or "**TWITTER_TEXT**" in text_content:
                                # Extract just the Twitter content part
                                lines = text_content.split('\n')
                                twitter_content = ""
                                in_twitter_section = False
                                
                                for line in lines:
                                    if "TWITTER_TEXT" in line or "**TWITTER_TEXT**" in line:
                                        in_twitter_section = True
                                        continue
                                    elif in_twitter_section and line.strip():
                                        # Stop at conclusion marker or other sections
                                        if (line.startswith("**THIS_CONCLUDES_THE_ANALYSIS**") or
                                            line.startswith("THIS_CONCLUDES_THE_ANALYSIS") or
                                            line.startswith("HTML_CHART") or 
                                            line.startswith("**HTML_CHART**") or
                                            line.startswith("View Report") or
                                            line.startswith("Based on my comprehensive analysis")):
                                            break
                                        # Skip empty lines and section headers
                                        if line.strip() and not line.startswith("**") and not line.startswith("##"):
                                            twitter_content += line.strip() + " "
                                
                                if twitter_content.strip():
                                    clean_twitter_text = twitter_content.strip()
                                    if is_placeholder_twitter_text(clean_twitter_text):
                                        self.logger.log_warning("⚠️ Old-format Twitter text matches prompt template, continuing search...")
                                        continue
                                    results["twitter_text"] = clean_twitter_text
                                    results["response_text"] = clean_twitter_text
                                    self.logger.log_success(f"Extracted Twitter text: {len(results['twitter_text'])} characters")
                                    break
                            
                            elif not results["response_text"] and len(text_content) > 50:
                                # Fallback to any substantial text content that looks like a response
                                if ("analysis" in text_content.lower() or 
                                    "stablecoin" in text_content.lower() or
                                    "market" in text_content.lower() or
                                    "data" in text_content.lower()):
                                    results["response_text"] = text_content
                                    self.logger.log_success(f"Extracted response text: {len(results['response_text'])} characters")
                                    break
                    if results["response_text"]:
                        break
                except Exception as e:
                    self.logger.log_warning(f"Error checking Twitter selector {selector}: {e}")
                    continue
            
            # Look for the right panel with charts/visualizations
            right_panel_selectors = [
                ".right-panel",
                ".visualization-panel",
                ".report-panel",
                ".chart-panel",
                "[data-testid='right-panel']",
                ".dashboard-panel"
            ]
            
            right_panel = None
            for selector in right_panel_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed() and element.size['width'] > 200:
                            right_panel = element
                            self.logger.log_success(f"Found right panel: {selector}")
                            break
                    if right_panel:
                        break
                except:
                    continue
            
            # If no specific right panel found, look for chart containers
            if not right_panel:
                chart_container_selectors = [
                    ".chart-container",
                    ".highcharts-container",
                    ".visualization-container",
                    "[data-testid='chart-container']"
                ]
                
                for selector in chart_container_selectors:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for element in elements:
                            if element.is_displayed() and element.size['width'] > 200:
                                right_panel = element
                                self.logger.log_success(f"Found chart container: {selector}")
                                break
                        if right_panel:
                            break
                    except:
                        continue
            
            # Take screenshot of the right panel (charts area)
            if right_panel:
                try:
                    # Scroll to make sure the panel is visible
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", right_panel)
                    time.sleep(2)
                    
                    # Take screenshot of the right panel
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    panel_screenshot = f"screenshots/charts_panel_{timestamp}.png"
                    right_panel.screenshot(panel_screenshot)
                    
                    if os.path.exists(panel_screenshot):
                        results["screenshots"].append(panel_screenshot)
                        self.logger.log_info(f"📸 Charts panel screenshot saved: {panel_screenshot}")
                        
                        # Add as artifact
                        artifact_info = {
                            "type": "charts_panel",
                            "index": 1,
                            "screenshot": panel_screenshot,
                            "selector": "right_panel",
                            "tag_name": right_panel.tag_name
                        }
                        results["artifacts"].append(artifact_info)
                        
                except Exception as e:
                    self.logger.log_warning(f"Failed to screenshot right panel: {e}")
            
            # Also look for individual charts and analysis artifacts within the panel
            artifact_selectors = [
                "canvas",
                "svg",
                ".highcharts-container",
                "[class*='chart']",
                "[class*='graph']",
                ".analysis-artifact",
                ".artifact-container",
                ".visualization-container",
                ".report-container",
                ".chart-container",
                ".graph-container",
                "[data-testid*='chart']",
                "[data-testid*='artifact']",
                "[data-testid*='visualization']"
            ]
            
            for selector in artifact_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for i, element in enumerate(elements):
                        if element.is_displayed() and element.size['width'] > 100 and element.size['height'] > 100:
                            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                            artifact_screenshot = f"screenshots/artifact_{len(results['artifacts'])+1}_{timestamp}.png"
                            
                            try:
                                element.screenshot(artifact_screenshot)
                                if os.path.exists(artifact_screenshot):
                                    artifact_info = {
                                        "type": "analysis_artifact",
                                        "index": len(results["artifacts"]) + 1,
                                        "screenshot": artifact_screenshot,
                                        "selector": selector,
                                        "tag_name": element.tag_name
                                    }
                                    results["artifacts"].append(artifact_info)
                                    results["screenshots"].append(artifact_screenshot)
                                    self.logger.log_info(f"📸 Analysis artifact {len(results['artifacts'])} screenshot saved: {artifact_screenshot}")
                            except Exception as e:
                                self.logger.log_warning(f"Failed to screenshot artifact: {e}")
                                continue
                except:
                    continue
            
            # Check if analysis conclusion marker was found (excluding user messages)
            conclusion_found = False
            try:
                conclusion_selectors = [
                    "//div[contains(text(), 'THIS_CONCLUDES_THE_ANALYSIS') and not(ancestor::*[@data-message-role='user'])]",
                    "//div[contains(text(), '**THIS_CONCLUDES_THE_ANALYSIS**') and not(ancestor::*[@data-message-role='user'])]",
                    "//span[contains(text(), 'THIS_CONCLUDES_THE_ANALYSIS') and not(ancestor::*[@data-message-role='user'])]",
                    "//p[contains(text(), 'THIS_CONCLUDES_THE_ANALYSIS') and not(ancestor::*[@data-message-role='user'])]"
                ]
                
                for selector in conclusion_selectors:
                    try:
                        elements = self.driver.find_elements(By.XPATH, selector)
                        for element in elements:
                            if element.is_displayed() and element.text.strip() and not self._is_user_message(element):
                                conclusion_found = True
                                break
                        if conclusion_found:
                            break
                    except:
                        continue
            except:
                pass
            
            # Create response metadata
            if results["twitter_text"] and is_placeholder_twitter_text(results["twitter_text"]):
                self.logger.log_warning("⚠️ Final fallback Twitter text matches prompt template, clearing value")
                results["twitter_text"] = ""
            
            results["response_metadata"] = {
                "word_count": len(results["response_text"].split()) if results["response_text"] else 0,
                "has_charts": any("chart" in a["type"] for a in results["artifacts"]),
                "has_tables": any("table" in a["type"] for a in results["artifacts"]),
                "has_code": "code" in results["response_text"].lower() if results["response_text"] else False,
                "analysis_type": "market_analysis",
                "conclusion_marker_found": conclusion_found,
                "twitter_text_format": "new" if "TWITTER_TEXT:" in results.get("response_text", "") else "old"
            }
            
            self.logger.log_success(f"✅ Data extracted: {len(results['response_text'])} chars, {len(results['artifacts'])} artifacts")
            return results
            
        except Exception as e:
            self.logger.log_error(f"Data extraction failed: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "chat_url": self.driver.current_url if self.driver else "",
                "response_text": "",
                "twitter_text": "",
                "artifacts": [],
                "screenshots": [],
                "response_metadata": {"error": str(e)}
            }
    
    def capture_final_screenshot(self) -> str:
        """Capture final screenshot of the chat."""
        try:
            screenshot_path = f"screenshots/final_state_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            self.driver.save_screenshot(screenshot_path)
            self.logger.log_info(f"📸 Final screenshot saved: {screenshot_path}")
            return screenshot_path
        except Exception as e:
            self.logger.log_error(f"Failed to capture final screenshot: {e}")
            return ""
    
    def run_analysis(self, prompt: str = "", prompt2: Optional[str] = None, response_timeout: int = 600) -> Dict[str, Any]:
        """Run the complete analysis workflow with comprehensive features.
        
        Args:
            prompt: Kept for backward compatibility (unused - static prompts are used instead)
            prompt2: When None, uses single-phase workflow (backward compatible).
                     When provided (any value), uses two-phase workflow with static prompts.
            response_timeout: Timeout in seconds for each phase
            
        Returns:
            Dictionary with success status, data, and any errors
        """
        results = {
            "success": False,
            "error": None,
            "timestamp": datetime.now().isoformat(),
            "data": {}
        }
        
        try:
            # Reset transient data from previous runs
            self.extracted_twitter_text = ""
            # Step 1: Initialization
            self.logger.log_info("🚀 Starting Flipside AI Analysis Workflow")
            # Always use two-phase workflow with static prompts
            self.logger.log_info("📋 Two-phase workflow: Analysis → Artifact Generation (using static prompts)")
            self.logger.log_info("=" * 60)
            
            if not self.initialize():
                raise Exception("Failed to initialize automation environment")
            
            # Step 2: Authentication
            self.logger.log_info("🔐 Starting authentication")
            if not self.authenticate():
                raise Exception("Authentication failed")
            self.logger.log_success("✅ Authentication successful")
            
            # Step 3: Navigation
            self.logger.log_info("🧭 Navigating to chat page")
            if not self.navigate_to_chat():
                raise Exception("Failed to navigate to chat page")
            self.logger.log_success("✅ Successfully navigated to chat page")
            
            # Step 4: Submit First Prompt (Phase 1)
            self.logger.log_info(f"📝 Phase 1: Submitting analysis prompt")
            if not self.submit_prompt(phase=1):
                raise Exception("Failed to submit first prompt")
            self.logger.log_success("✅ Phase 1 prompt submitted successfully")
            
            # Step 5: Wait for Validation Checkpoint (Phase 1)
            self.logger.log_info(f"⏳ Phase 1: Waiting for validation checkpoint (timeout: {response_timeout}s)")
            checkpoint_found = self.wait_for_checkpoint(response_timeout)
            if not checkpoint_found:
                self.logger.log_warning("⚠️ Validation checkpoint timeout, but continuing to Phase 2...")
            else:
                self.logger.log_success("✅ Phase 1: Validation checkpoint reached")
                # Wait 30 seconds after checkpoint before submitting Phase 2
                self.logger.log_info("⏳ Waiting 30 seconds after checkpoint before Phase 2...")
                time.sleep(30)
                self.logger.log_info("✅ Wait complete, proceeding to Phase 2")
            
            # Step 6: Submit Second Prompt (Phase 2)
            self.logger.log_info(f"📝 Phase 2: Submitting artifact generation prompt")
            if not self.submit_prompt(phase=2):
                raise Exception("Failed to submit second prompt")
            self.logger.log_success("✅ Phase 2 prompt submitted successfully")
            
            # Step 7: Wait for Final Response (Phase 2)
            self.logger.log_info(f"⏳ Phase 2: Waiting for final AI response (timeout: {response_timeout}s)")
            response_complete = self.wait_for_response(response_timeout)
            
            if not response_complete:
                self.logger.log_warning("⚠️ Response timeout, but continuing with data capture...")
            else:
                self.logger.log_success("✅ AI response completed")
            
            # Step 6: Extract Data
            self.logger.log_info("📊 Extracting analysis data")
            results["data"] = self.extract_data()
            
            # Step 7: Capture Published Artifact Screenshot (handled by ChatDataExtractor)
            # The artifact screenshot is captured by the ChatDataExtractor during data extraction
            # No need to duplicate this logic here
            
            # Step 8: Final Screenshot
            self.logger.log_info("📸 Capturing final screenshot")
            try:
                final_screenshot = self.capture_final_screenshot()
                if final_screenshot:
                    results["data"]["screenshots"].append(final_screenshot)
                    self.logger.log_success(f"✅ Final screenshot: {final_screenshot}")
            except Exception as screenshot_error:
                self.logger.log_warning(f"Failed to capture final screenshot: {screenshot_error}")
            
            # Mark as successful
            results["success"] = True
            
            # Log summary
            response_length = len(results["data"].get("response_text", ""))
            twitter_length = len(results["data"].get("twitter_text", ""))
            artifacts_count = len(results["data"].get("artifacts", []))
            screenshots_count = len(results["data"].get("screenshots", []))
            
            self.logger.log_success("🎉 Analysis workflow completed successfully!")
            self.logger.log_info(f"📊 Results Summary:")
            self.logger.log_info(f"   📝 Response text: {response_length} characters")
            self.logger.log_info(f"   🐦 Twitter text: {twitter_length} characters")
            self.logger.log_info(f"   📈 Artifacts: {artifacts_count}")
            self.logger.log_info(f"   📸 Screenshots: {screenshots_count}")
            self.logger.log_info(f"   🔗 Chat URL: {results['data'].get('chat_url', 'N/A')}")
            
        except Exception as e:
            error_msg = f"Analysis failed: {e}"
            self.logger.log_error(error_msg)
            results["error"] = error_msg
            
            # Capture error screenshot
            if self.driver:
                try:
                    error_screenshot = f"screenshots/error_state_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                    self.driver.save_screenshot(error_screenshot)
                    self.logger.log_info(f"📸 Error screenshot saved: {error_screenshot}")
                except Exception as screenshot_error:
                    self.logger.log_error(f"Failed to capture error screenshot: {screenshot_error}")
        
        finally:
            # Cleanup
            self.logger.log_info("🧹 Cleaning up resources")
            self.cleanup()
            self.logger.log_info("🧹 Cleanup completed")
        
        return results
    
    def cleanup(self):
        """Clean up resources."""
        try:
            if self.authenticator:
                self.authenticator.cleanup()
            elif self.driver:
                self.driver.quit()
            self.logger.log_info("🧹 Cleanup completed")
        except Exception as e:
            self.logger.log_error(f"Cleanup error: {e}")
    
    def _setup_standard_driver(self) -> Optional[webdriver.Chrome]:
        """Setup standard Chrome driver with comprehensive options."""
        try:
            self.logger.log_info("Configuring Chrome WebDriver options")
            chrome_options = Options()
            
            # Headless mode for GitHub Actions
            headless_mode = os.getenv('CHROME_HEADLESS', 'false').lower() == 'true'
            if headless_mode:
                chrome_options.add_argument('--headless')
                self.logger.log_info("Headless mode enabled")
            else:
                self.logger.log_info("Headless mode disabled (visible browser)")
            
            # Window size for consistent screenshots
            window_size = os.getenv('CHROME_WINDOW_SIZE', '1920,1080')
            chrome_options.add_argument(f'--window-size={window_size}')
            self.logger.log_info(f"Window size set to: {window_size}")
            
            # Performance and stability options
            # Note: JavaScript must be enabled for modern web apps and login forms
            stability_options = [
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--disable-extensions',
                '--disable-plugins',
                '--disable-images',
                '--disable-web-security',
                '--allow-running-insecure-content'
            ]
            
            for option in stability_options:
                chrome_options.add_argument(option)
            
            self.logger.log_info("Applied stability options")
            
            # User agent
            user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            chrome_options.add_argument(f'--user-agent={user_agent}')
            
            # Logging - enable verbose logging
            chrome_options.add_argument('--enable-logging')
            chrome_options.add_argument('--log-level=0')
            chrome_options.add_argument('--v=1')
            chrome_options.add_argument('--enable-logging=stderr')
            
            # Set up ChromeDriver
            self.logger.log_info("Installing ChromeDriver")
            service = Service(ChromeDriverManager().install())
            
            # Create driver
            self.logger.log_info("Initializing Chrome WebDriver")
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.implicitly_wait(10)
            
            self.logger.log_success("Chrome WebDriver initialized successfully")
            return driver
            
        except Exception as e:
            self.logger.log_error(f"Failed to setup Chrome WebDriver: {e}")
            return None
    
    def _standard_authentication(self) -> bool:
        """Standard authentication fallback."""
        # This would implement cookie-based authentication
        # For now, return True as placeholder
        self.logger.log_info("Using standard authentication (placeholder)")
        return True
    
    def _find_chat_input(self):
        """Find the chat input element."""
        try:
            chat_selectors = [
                "textarea[placeholder*='Ask FlipsideAI']",
                "textarea[placeholder*='message']",
                "textarea[data-testid='chat-input']",
                "textarea"
            ]
            
            for selector in chat_selectors:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if element and element.is_displayed():
                        return element
                except NoSuchElementException:
                    continue
            
            return None
        except Exception:
            return None
    
    def _click_view_report_buttons(self):
        """Click View Report buttons to show visuals."""
        try:
            view_report_selectors = [
                "//button[contains(text(), 'View Report')]",
                "//button[contains(text(), 'view report')]",
                "//a[contains(text(), 'View Report')]",
                "//a[contains(text(), 'view report')]",
                "[data-testid='view-report']",
                "[data-testid='View Report']",
                "[data-testid='view_report']",
                ".view-report-button",
                ".artifact-link",
                ".report-link",
                "button[class*='view']",
                "button[class*='report']",
                "a[class*='view']",
                "a[class*='report']",
                "a[href*='report']",
                "a[href*='view']"
            ]
            
            for selector in view_report_selectors:
                try:
                    if selector.startswith('//'):
                        elements = self.driver.find_elements(By.XPATH, selector)
                    else:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            element_text = element.text.lower().strip()
                            element_href = (element.get_attribute('href') or '').lower()
                            
                            if ('view report' in element_text or 
                                'view' in element_text or 
                                'report' in element_text or
                                'view' in element_href or
                                'report' in element_href or
                                'view' in selector.lower() or
                                'report' in selector.lower()):
                                self.logger.log_info(f"Clicking 'View Report' button: {selector} - Text: '{element_text}'")
                                try:
                                    self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                                    time.sleep(1)
                                    element.click()
                                    time.sleep(8)  # Wait longer for report to load
                                    self.logger.log_success("View Report button clicked - visuals should now be visible")
                                    break
                                except Exception as e:
                                    self.logger.log_warning(f"Failed to click View Report button: {e}")
                                    continue
                except Exception as e:
                    self.logger.log_warning(f"Error checking View Report selector {selector}: {e}")
                    continue
        except Exception as e:
            self.logger.log_warning(f"Error in _click_view_report_buttons: {e}")
    
    def close_artifact_view(self) -> bool:
        """Close the artifact view by clicking the X button to reveal the share button."""
        try:
            self.logger.log_info("Looking for artifact view close button...")
            
            close_selectors = [
                "button[aria-label*='Close']",
                "button[title*='Close']",
                "button[aria-label*='close']",
                "button[title*='close']",
                "[data-testid*='close']",
                "[data-testid*='Close']",
                "//button[contains(text(), '×')]",
                "//button[contains(text(), '✕')]",
                "//button[contains(text(), 'X')]",
                "//button[contains(text(), 'close')]",
                "//button[contains(text(), 'Close')]",
                ".close-button",
                ".artifact-close",
                ".view-close",
                ".modal-close",
                ".panel-close",
                ".header-close",
                ".toolbar-close",
                ".header button",
                ".toolbar button",
                ".modal-header button",
                ".panel-header button",
                "button"
            ]
            
            close_button = None
            for selector in close_selectors:
                try:
                    if selector.startswith('//'):
                        elements = self.driver.find_elements(By.XPATH, selector)
                    else:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for i, element in enumerate(elements):
                        if element.is_displayed() and element.is_enabled():
                            location = element.location
                            size = self.driver.get_window_size()
                            element_text = element.text.lower().strip()
                            element_title = (element.get_attribute('title') or '').lower()
                            element_aria_label = (element.get_attribute('aria-label') or '').lower()
                            element_class = (element.get_attribute('class') or '').lower()
                            
                            # Check if it's in the upper right area
                            if location['x'] > size['width'] * 0.5 and location['y'] < size['height'] * 0.4:
                                if ('close' in element_text or 
                                    'close' in element_title or
                                    'close' in element_aria_label or
                                    'close' in element_class or
                                    '×' in element_text or
                                    '✕' in element_text or
                                    'x' in element_text or
                                    'close' in selector.lower()):
                                    close_button = element
                                    self.logger.log_success(f"Found artifact close button: {selector} - Element {i}")
                                    break
                                elif location['x'] > size['width'] * 0.8 and location['y'] < size['height'] * 0.2:
                                    close_button = element
                                    self.logger.log_success(f"Found potential close button by position: {selector} - Element {i}")
                                    break
                    if close_button:
                        break
                except Exception as e:
                    self.logger.log_warning(f"Error checking close selector {selector}: {e}")
                    continue
            
            if close_button:
                try:
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", close_button)
                    time.sleep(1)
                    close_button.click()
                    time.sleep(3)
                    self.logger.log_success("Artifact view closed successfully")
                    return True
                except Exception as e:
                    self.logger.log_warning(f"Failed to click close button: {e}")
                    return False
            else:
                self.logger.log_info("No artifact view found or already closed")
                return True
                
        except Exception as e:
            self.logger.log_warning(f"Failed to close artifact view: {e}")
            return True
    
    def extract_shareable_link(self) -> str:
        """Extract the shareable link by clicking Share -> Public -> Copy URL."""
        try:
            self.logger.log_info("Extracting shareable link...")
            
            # First, try to close any open artifact view to reveal the share button
            self.close_artifact_view()
            
            share_selectors = [
                "button[aria-label*='Share']",
                "button[title*='Share']",
                "button[data-testid*='share']",
                "button[data-testid*='Share']",
                "//button[contains(text(), 'Share')]",
                "//button[contains(text(), 'share')]",
                ".share-button",
                "button[class*='share']",
                "button[class*='Share']",
                "button svg[data-testid*='share']",
                "button svg[data-testid*='Share']",
                ".header button",
                ".chat-header button",
                ".top-bar button",
                ".toolbar button",
                ".action-button",
                "button[class*='icon']",
                "button[role='button']",
                "button",
                "[role='button']"
            ]
            
            share_button = None
            for selector in share_selectors:
                try:
                    if selector.startswith('//'):
                        elements = self.driver.find_elements(By.XPATH, selector)
                    else:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for i, element in enumerate(elements):
                        if element.is_displayed() and element.is_enabled():
                            location = element.location
                            size = self.driver.get_window_size()
                            element_text = element.text.lower().strip()
                            element_title = (element.get_attribute('title') or '').lower()
                            element_aria_label = (element.get_attribute('aria-label') or '').lower()
                            element_class = (element.get_attribute('class') or '').lower()
                            element_data_testid = (element.get_attribute('data-testid') or '').lower()
                            
                            # Check if it's in the upper right area
                            if location['x'] > size['width'] * 0.3 and location['y'] < size['height'] * 0.5:
                                if ('share' in element_text or 
                                    'share' in element_title or 
                                    'share' in element_aria_label or
                                    'share' in element_class or
                                    'share' in element_data_testid or
                                    'share' in selector.lower()):
                                    share_button = element
                                    self.logger.log_success(f"Found Share button: {selector} - Element {i}")
                                    break
                                elif location['x'] > size['width'] * 0.7 and location['y'] < size['height'] * 0.3:
                                    if (element.size['width'] < 100 and element.size['height'] < 100) or 'icon' in element_class:
                                        share_button = element
                                        self.logger.log_success(f"Found potential Share button by position and size: {selector} - Element {i}")
                                        break
                    if share_button:
                        break
                except Exception as e:
                    self.logger.log_warning(f"Error checking selector {selector}: {e}")
                    continue
            
            if not share_button:
                self.logger.log_warning("Share button not found")
                self._capture_warning_screenshot("share_button_not_found")
                return ""
            
            # Click Share button
            share_button.click()
            time.sleep(3)
            
            # Look for Public option in modal
            public_selectors = [
                "input[type='radio'][value='public']",
                "input[type='radio']",
                "label:contains('Public')",
                "[data-testid='public-option']",
                ".public-option",
                "input[name*='public']"
            ]
            
            public_option = None
            for selector in public_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed():
                            element_text = element.text.lower()
                            element_value = element.get_attribute("value", "").lower()
                            if 'public' in element_text or 'public' in element_value:
                                public_option = element
                                self.logger.log_success(f"Found Public option: {selector}")
                                break
                    if public_option:
                        break
                except:
                    continue
            
            if public_option:
                if public_option.get_attribute("type") == "radio" and not public_option.is_selected():
                    public_option.click()
                    time.sleep(2)
                    self.logger.log_success("Selected Public option")
                elif public_option.get_attribute("type") == "radio" and public_option.is_selected():
                    self.logger.log_info("Public option already selected")
            else:
                self.logger.log_warning("Public option not found, trying to proceed anyway")
            
            # Look for URL input field or copy button
            url_selectors = [
                "input[readonly]",
                "input[value*='flipsidecrypto.xyz']",
                ".share-url-input",
                "[data-testid='share-url']",
                "input[type='text']",
                ".url-input",
                ".link-input"
            ]
            
            url_input = None
            for selector in url_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed() and element.get_attribute("value"):
                            url_value = element.get_attribute("value")
                            if 'flipsidecrypto.xyz' in url_value:
                                url_input = element
                                self.logger.log_success(f"Found URL input: {selector}")
                                break
                    if url_input:
                        break
                except:
                    continue
            
            if url_input:
                shareable_url = url_input.get_attribute("value")
                # Always ensure it's in the shared format
                if '/shared/chats/' not in shareable_url:
                    if '/chat/' in shareable_url:
                        chat_id = shareable_url.split('/chat/')[-1]
                        shareable_url = f"https://flipsidecrypto.xyz/chat/shared/chats/{chat_id}"
                        self.logger.log_info(f"Converted to shared format: {shareable_url}")
                    else:
                        current_url = self.driver.current_url
                        if '/chat/' in current_url:
                            chat_id = current_url.split('/chat/')[-1]
                            shareable_url = f"https://flipsidecrypto.xyz/chat/shared/chats/{chat_id}"
                            self.logger.log_info(f"Constructed from current URL: {shareable_url}")
                
                self.logger.log_success(f"Extracted shareable URL: {shareable_url}")
                
                # Close the modal
                try:
                    self.driver.find_element(By.TAG_NAME, "body").click()
                    time.sleep(1)
                except:
                    pass
                
                return shareable_url
            else:
                self.logger.log_warning("URL input field not found")
                self._capture_warning_screenshot("url_input_not_found")
                # Always construct URL from current page URL in shared format
                current_url = self.driver.current_url
                if '/chat/' in current_url:
                    chat_id = current_url.split('/chat/')[-1]
                    constructed_url = f"https://flipsidecrypto.xyz/chat/shared/chats/{chat_id}"
                    self.logger.log_info(f"Constructed shareable URL: {constructed_url}")
                    return constructed_url
                return ""
                
        except Exception as e:
            self.logger.log_error(f"Failed to extract shareable link: {e}")
            return ""
    
    def _try_copy_response(self) -> bool:
        """Try to find and click the copy button to get the full response."""
        try:
            self.logger.log_info("Looking for copy button...")
            
            copy_selectors = [
                "button[aria-label*='Copy']",
                "button[title*='Copy']",
                "button[data-testid*='copy']",
                "button[data-testid*='Copy']",
                "//button[contains(text(), 'Copy')]",
                "//button[contains(text(), 'copy')]",
                ".copy-button",
                "button[class*='copy']",
                "button[class*='Copy']",
                "button svg[data-testid*='copy']",
                "button svg[data-testid*='Copy']",
                "//button[contains(@class, 'action-button') and contains(text(), 'Copy')]",
                "//button[contains(@class, 'action-button') and contains(text(), 'copy')]",
                "//button[contains(@class, 'icon') and contains(text(), 'Copy')]",
                "//button[contains(@class, 'icon') and contains(text(), 'copy')]",
                "button[class*='action']",
                ".message-actions button",
                ".response-actions button",
                ".chat-actions button"
            ]
            
            copy_button = None
            for selector in copy_selectors:
                try:
                    if selector.startswith('//'):
                        elements = self.driver.find_elements(By.XPATH, selector)
                    else:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for i, element in enumerate(elements):
                        if element.is_displayed() and element.is_enabled():
                            element_text = element.text.lower().strip()
                            element_title = (element.get_attribute('title') or '').lower()
                            element_aria_label = (element.get_attribute('aria-label') or '').lower()
                            element_class = (element.get_attribute('class') or '').lower()
                            element_data_testid = (element.get_attribute('data-testid') or '').lower()
                            
                            if ('copy' in element_text or 
                                'copy' in element_title or 
                                'copy' in element_aria_label or
                                'copy' in element_class or
                                'copy' in element_data_testid or
                                'copy' in selector.lower()):
                                copy_button = element
                                self.logger.log_success(f"Found copy button: {selector} - Element {i}")
                                break
                    if copy_button:
                        break
                except Exception as e:
                    self.logger.log_warning(f"Error checking copy selector {selector}: {e}")
                    continue
            
            if copy_button:
                try:
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", copy_button)
                    time.sleep(1)
                    copy_button.click()
                    time.sleep(2)
                    self.logger.log_success("Copy button clicked")
                    return True
                except Exception as e:
                    self.logger.log_warning(f"Failed to click copy button: {e}")
                    return False
            else:
                self.logger.log_info("Copy button not found")
                return False
                
        except Exception as e:
            self.logger.log_warning(f"Failed to use copy button: {e}")
            return False
    
    def _capture_warning_screenshot(self, warning_type: str):
        """Capture a screenshot when a warning or error occurs."""
        try:
            if self.driver:
                screenshot_path = f"screenshots/warning_{warning_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                self.driver.save_screenshot(screenshot_path)
                self.logger.log_info(f"📸 Warning screenshot saved: {screenshot_path}")
        except Exception as e:
            self.logger.log_warning(f"Failed to capture warning screenshot: {e}")
    
    def capture_published_artifact_screenshot(self) -> Optional[str]:
        """DEPRECATED: Artifact screenshot capture is now handled by ChatDataExtractor.
        
        This method is kept for backward compatibility but does nothing.
        The artifact screenshot is captured during data extraction via ChatDataExtractor.
        """
        self.logger.log_info("ℹ️ Artifact screenshot capture is handled by ChatDataExtractor during data extraction")
        return None
