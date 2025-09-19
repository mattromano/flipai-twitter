#!/usr/bin/env python3
"""
Simple script to view analysis results and statistics.
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from src.results_logger import ResultsLogger

def view_results():
    """View recent analysis results."""
    print("📊 Flipside Chat Analysis Results Viewer")
    print("=" * 50)
    
    logger = ResultsLogger()
    
    # Get today's summary
    today = datetime.now().strftime("%Y%m%d")
    summary = logger.get_daily_summary(today)
    
    print(f"\n📅 Today's Summary ({today}):")
    print(f"  Total runs: {summary.get('total_runs', 0)}")
    print(f"  Successful: {summary.get('successful_runs', 0)}")
    print(f"  Success rate: {summary.get('success_rate', 0):.1f}%")
    print(f"  Total artifacts: {summary.get('total_artifacts', 0)}")
    print(f"  Avg response length: {summary.get('avg_response_length', 0):.0f} chars")
    
    if summary.get('artifact_types'):
        print(f"  Artifact types: {summary['artifact_types']}")
    
    # Show recent logs
    print(f"\n📋 Recent Analysis Logs:")
    recent_logs = logger.list_recent_logs(days=3)
    
    if not recent_logs:
        print("  No recent logs found.")
    else:
        for i, log in enumerate(recent_logs[:5]):  # Show last 5
            status = "✅" if log.get('success') else "❌"
            print(f"  {i+1}. {status} {log.get('filename', 'unknown')}")
            print(f"     Response: {log.get('response_length', 0)} chars")
            print(f"     Artifacts: {log.get('artifact_count', 0)}")
            print()
    
    # Show available files
    print(f"\n📁 Available Files:")
    
    # Screenshots
    screenshots_dir = Path("screenshots")
    if screenshots_dir.exists():
        screenshot_files = list(screenshots_dir.glob("*.png"))
        print(f"  Screenshots: {len(screenshot_files)} files")
        for file in screenshot_files[-3:]:  # Show last 3
            print(f"    - {file.name}")
    else:
        print("  Screenshots: No directory found")
    
    # Logs
    logs_dir = Path("logs")
    if logs_dir.exists():
        analysis_logs = list(logs_dir.glob("analysis_*.json"))
        summary_logs = list(logs_dir.glob("daily_summary_*.jsonl"))
        print(f"  Analysis logs: {len(analysis_logs)} files")
        print(f"  Summary logs: {len(summary_logs)} files")
    else:
        print("  Logs: No directory found")
    
    print(f"\n💡 To view detailed results:")
    print(f"  - Check the 'logs/' directory for JSON files")
    print(f"  - Check the 'screenshots/' directory for images")
    print(f"  - Run with DEBUG_MODE=true for verbose output")

if __name__ == "__main__":
    view_results()
