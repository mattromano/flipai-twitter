#!/usr/bin/env python3
"""
Test Chat Data Extraction

Simple script to test extracting Twitter text and artifacts from a chat URL.
"""

import json
from modules.chat_manager.chat_data_extractor import ChatDataExtractor
from modules.shared.logger import AutomationLogger


def main():
    """Test the chat data extraction."""
    logger = AutomationLogger()
    
    # Test with the recent chat URL (shared format)
    chat_url = "https://flipsidecrypto.xyz/chat/shared/chats/0c1044a0-cbc2-44d1-8642-12f1ccb8ebe2"
    
    logger.log_info("🚀 Starting chat data extraction test")
    logger.log_info(f"📋 Chat URL: {chat_url}")
    
    # Create extractor and run extraction
    extractor = ChatDataExtractor()
    results = extractor.extract_from_chat_url(chat_url)
    
    # Display results
    logger.log_info("📊 Extraction Results:")
    logger.log_info(f"   Success: {results['success']}")
    logger.log_info(f"   Twitter Text Length: {len(results['twitter_text'])}")
    logger.log_info(f"   Response Text Length: {len(results['response_text'])}")
    logger.log_info(f"   Artifact Screenshot: {results['artifact_screenshot']}")
    logger.log_info(f"   Screenshots: {len(results['screenshots'])}")
    
    if results['error']:
        logger.log_error(f"   Error: {results['error']}")
    
    # Save results to file
    output_file = f"logs/chat_extraction_test_{results['timestamp'].replace(':', '-')}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.log_info(f"💾 Results saved to: {output_file}")
    
    # Display Twitter text if found
    if results['twitter_text']:
        logger.log_info("🐦 Twitter Text:")
        logger.log_info(f"   {results['twitter_text']}")
    else:
        logger.log_warning("⚠️ No Twitter text found")
    
    # Display response text preview
    if results['response_text']:
        preview = results['response_text'][:200] + "..." if len(results['response_text']) > 200 else results['response_text']
        logger.log_info("📝 Response Text Preview:")
        logger.log_info(f"   {preview}")
    else:
        logger.log_warning("⚠️ No response text found")


if __name__ == "__main__":
    main()
