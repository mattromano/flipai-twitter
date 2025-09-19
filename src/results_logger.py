#!/usr/bin/env python3
"""
Results logging utility for Flipside Chat Automation.
Handles structured logging of analysis results, responses, and metadata.
"""

import json
import os
import logging
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path


class ResultsLogger:
    """Handles logging of analysis results with structured data."""
    
    def __init__(self, log_dir: str = "logs"):
        """
        Initialize the results logger.
        
        Args:
            log_dir: Directory to store log files
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Setup logger
        self.logger = logging.getLogger(__name__)
        
    def log_analysis_result(self, result_data: Dict[str, Any]) -> str:
        """
        Log a complete analysis result to structured files.
        
        Args:
            result_data: Dictionary containing analysis results
            
        Returns:
            Path to the log file created
        """
        try:
            timestamp = datetime.now()
            date_str = timestamp.strftime("%Y%m%d")
            time_str = timestamp.strftime("%H%M%S")
            
            # Create log filename
            log_filename = f"analysis_{date_str}_{time_str}.json"
            log_path = self.log_dir / log_filename
            
            # Prepare structured log data
            log_entry = {
                "timestamp": timestamp.isoformat(),
                "date": date_str,
                "time": time_str,
                "success": result_data.get("success", False),
                "error": result_data.get("error"),
                "data": result_data.get("data", {})
            }
            
            # Add response analysis if available
            if "data" in result_data and "response_text" in result_data["data"]:
                response_text = result_data["data"]["response_text"]
                log_entry["response_summary"] = {
                    "length": len(response_text),
                    "word_count": len(response_text.split()) if response_text else 0,
                    "preview": response_text[:200] + "..." if len(response_text) > 200 else response_text
                }
            
            # Add artifact summary
            if "data" in result_data and "artifacts" in result_data["data"]:
                artifacts = result_data["data"]["artifacts"]
                log_entry["artifact_summary"] = {
                    "total_artifacts": len(artifacts),
                    "artifact_types": {}
                }
                
                for artifact in artifacts:
                    artifact_type = artifact.get("type", "unknown")
                    if artifact_type not in log_entry["artifact_summary"]["artifact_types"]:
                        log_entry["artifact_summary"]["artifact_types"][artifact_type] = 0
                    log_entry["artifact_summary"]["artifact_types"][artifact_type] += 1
            
            # Write to JSON file
            with open(log_path, 'w', encoding='utf-8') as f:
                json.dump(log_entry, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Analysis result logged to: {log_path}")
            
            # Also append to daily summary log
            self._append_to_daily_summary(log_entry, date_str)
            
            return str(log_path)
            
        except Exception as e:
            self.logger.error(f"Error logging analysis result: {e}")
            return ""
    
    def _append_to_daily_summary(self, log_entry: Dict[str, Any], date_str: str) -> None:
        """
        Append result to daily summary log.
        
        Args:
            log_entry: Log entry data
            date_str: Date string (YYYYMMDD)
        """
        try:
            summary_filename = f"daily_summary_{date_str}.jsonl"
            summary_path = self.log_dir / summary_filename
            
            # Create summary entry
            summary_entry = {
                "time": log_entry["time"],
                "success": log_entry["success"],
                "error": log_entry.get("error"),
                "response_length": log_entry.get("response_summary", {}).get("length", 0),
                "word_count": log_entry.get("response_summary", {}).get("word_count", 0),
                "total_artifacts": log_entry.get("artifact_summary", {}).get("total_artifacts", 0),
                "artifact_types": log_entry.get("artifact_summary", {}).get("artifact_types", {})
            }
            
            # Append to daily summary (JSONL format)
            with open(summary_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(summary_entry, ensure_ascii=False) + '\n')
                
        except Exception as e:
            self.logger.error(f"Error appending to daily summary: {e}")
    
    def log_response_only(self, response_text: str, metadata: Dict[str, Any] = None) -> str:
        """
        Log just a response text with metadata.
        
        Args:
            response_text: The response text to log
            metadata: Optional metadata about the response
            
        Returns:
            Path to the log file created
        """
        try:
            timestamp = datetime.now()
            date_str = timestamp.strftime("%Y%m%d")
            time_str = timestamp.strftime("%H%M%S")
            
            # Create response-only log filename
            log_filename = f"response_{date_str}_{time_str}.json"
            log_path = self.log_dir / log_filename
            
            # Prepare response log data
            log_entry = {
                "timestamp": timestamp.isoformat(),
                "date": date_str,
                "time": time_str,
                "type": "response_only",
                "response_text": response_text,
                "metadata": metadata or {},
                "response_stats": {
                    "length": len(response_text),
                    "word_count": len(response_text.split()) if response_text else 0,
                    "line_count": len(response_text.split('\n')) if response_text else 0
                }
            }
            
            # Write to JSON file
            with open(log_path, 'w', encoding='utf-8') as f:
                json.dump(log_entry, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Response logged to: {log_path}")
            return str(log_path)
            
        except Exception as e:
            self.logger.error(f"Error logging response: {e}")
            return ""
    
    def get_daily_summary(self, date_str: str = None) -> Dict[str, Any]:
        """
        Get summary statistics for a specific day.
        
        Args:
            date_str: Date string (YYYYMMDD), defaults to today
            
        Returns:
            Dictionary with daily summary statistics
        """
        try:
            if not date_str:
                date_str = datetime.now().strftime("%Y%m%d")
            
            summary_filename = f"daily_summary_{date_str}.jsonl"
            summary_path = self.log_dir / summary_filename
            
            if not summary_path.exists():
                return {"date": date_str, "total_runs": 0, "successful_runs": 0}
            
            # Read and analyze daily summary
            total_runs = 0
            successful_runs = 0
            total_artifacts = 0
            total_response_length = 0
            artifact_types = {}
            
            with open(summary_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        entry = json.loads(line.strip())
                        total_runs += 1
                        if entry.get("success", False):
                            successful_runs += 1
                        total_artifacts += entry.get("total_artifacts", 0)
                        total_response_length += entry.get("response_length", 0)
                        
                        # Aggregate artifact types
                        for artifact_type, count in entry.get("artifact_types", {}).items():
                            artifact_types[artifact_type] = artifact_types.get(artifact_type, 0) + count
            
            return {
                "date": date_str,
                "total_runs": total_runs,
                "successful_runs": successful_runs,
                "success_rate": (successful_runs / total_runs * 100) if total_runs > 0 else 0,
                "total_artifacts": total_artifacts,
                "avg_response_length": (total_response_length / total_runs) if total_runs > 0 else 0,
                "artifact_types": artifact_types
            }
            
        except Exception as e:
            self.logger.error(f"Error getting daily summary: {e}")
            return {"date": date_str, "error": str(e)}
    
    def list_recent_logs(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        List recent log files with metadata.
        
        Args:
            days: Number of days to look back
            
        Returns:
            List of log file information
        """
        try:
            recent_logs = []
            cutoff_date = datetime.now().timestamp() - (days * 24 * 60 * 60)
            
            for log_file in self.log_dir.glob("analysis_*.json"):
                if log_file.stat().st_mtime > cutoff_date:
                    try:
                        with open(log_file, 'r', encoding='utf-8') as f:
                            log_data = json.load(f)
                        
                        recent_logs.append({
                            "filename": log_file.name,
                            "path": str(log_file),
                            "timestamp": log_data.get("timestamp"),
                            "success": log_data.get("success", False),
                            "response_length": log_data.get("response_summary", {}).get("length", 0),
                            "artifact_count": log_data.get("artifact_summary", {}).get("total_artifacts", 0)
                        })
                    except Exception as e:
                        self.logger.warning(f"Error reading log file {log_file}: {e}")
            
            # Sort by timestamp (newest first)
            recent_logs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            return recent_logs
            
        except Exception as e:
            self.logger.error(f"Error listing recent logs: {e}")
            return []
