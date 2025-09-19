#!/usr/bin/env python3
"""
Stop the Twitter clone frontend server.
"""

import subprocess
import sys

def main():
    """Stop the Twitter clone frontend server."""
    
    print("🛑 Stopping Twitter Clone Frontend...")
    
    try:
        # Find and kill the process
        result = subprocess.run(
            ["pkill", "-f", "twitter_clone_frontend.py"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Twitter clone server stopped")
        else:
            print("ℹ️  No running Twitter clone server found")
            
    except Exception as e:
        print(f"❌ Error stopping server: {e}")

if __name__ == "__main__":
    main()
