#!/usr/bin/env python3
"""
Virtual Environment Activation Helper

Provides helper functions and commands for working with the virtual environment
in the Flipside Chat Automation project.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


def get_venv_paths():
    """Get virtual environment paths based on the operating system."""
    if platform.system() == "Windows":
        return {
            "activate": "venv\\Scripts\\activate",
            "python": "venv\\Scripts\\python",
            "pip": "venv\\Scripts\\pip",
            "activate_cmd": "venv\\Scripts\\activate"
        }
    else:  # Unix/Linux/macOS
        return {
            "activate": "venv/bin/activate",
            "python": "venv/bin/python", 
            "pip": "venv/bin/pip",
            "activate_cmd": "source venv/bin/activate"
        }


def check_venv_exists():
    """Check if virtual environment exists."""
    venv_path = Path("venv")
    return venv_path.exists()


def run_in_venv(command, description="Running command"):
    """Run a command within the virtual environment."""
    if not check_venv_exists():
        print("❌ Virtual environment not found. Run setup_local.py first.")
        return False
    
    paths = get_venv_paths()
    
    if isinstance(command, str):
        # For shell commands, use the activate script
        full_command = f"{paths['activate_cmd']} && {command}"
    else:
        # For list commands, use the python/pip paths directly
        full_command = [paths[command[0]]] + command[1:]
    
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(full_command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False


def install_dependencies():
    """Install project dependencies in the virtual environment."""
    return run_in_venv("pip install -r requirements.txt", "Installing dependencies")


def run_automation():
    """Run the main automation script."""
    return run_in_venv("python src/chat_automation.py", "Running Flipside chat automation")


def run_tests():
    """Run any available tests."""
    return run_in_venv("python -m pytest tests/", "Running tests")


def check_installation():
    """Check if all required packages are installed."""
    required_packages = [
        "selenium",
        "webdriver_manager", 
        "python-dotenv",
        "requests",
        "pillow"
    ]
    
    print("🔍 Checking package installation...")
    all_installed = True
    
    for package in required_packages:
        try:
            result = subprocess.run(
                [get_venv_paths()["python"], "-c", f"import {package}; print(f'{package}: OK')"],
                capture_output=True, text=True, check=True
            )
            print(f"✅ {result.stdout.strip()}")
        except subprocess.CalledProcessError:
            print(f"❌ {package}: Not installed")
            all_installed = False
    
    return all_installed


def show_venv_info():
    """Show virtual environment information."""
    if not check_venv_exists():
        print("❌ Virtual environment not found")
        return
    
    paths = get_venv_paths()
    print("📋 Virtual Environment Information")
    print("=" * 40)
    print(f"Activate command: {paths['activate_cmd']}")
    print(f"Python path: {paths['python']}")
    print(f"Pip path: {paths['pip']}")
    
    # Check Python version in venv
    try:
        result = subprocess.run(
            [paths["python"], "--version"],
            capture_output=True, text=True, check=True
        )
        print(f"Python version: {result.stdout.strip()}")
    except subprocess.CalledProcessError:
        print("Python version: Unable to determine")
    
    # Check if packages are installed
    print(f"\nPackage status:")
    check_installation()


def main():
    """Main function for command-line usage."""
    if len(sys.argv) < 2:
        print("Usage: python activate_venv.py <command>")
        print("\nAvailable commands:")
        print("  info        - Show virtual environment information")
        print("  install     - Install dependencies")
        print("  run         - Run the automation script")
        print("  test        - Run tests")
        print("  check       - Check package installation")
        print("  setup       - Run local setup")
        return
    
    command = sys.argv[1].lower()
    
    if command == "info":
        show_venv_info()
    elif command == "install":
        install_dependencies()
    elif command == "run":
        run_automation()
    elif command == "test":
        run_tests()
    elif command == "check":
        check_installation()
    elif command == "setup":
        # Import and run setup
        try:
            from setup_local import setup_local_environment
            setup_local_environment()
        except ImportError:
            print("❌ setup_local.py not found")
    else:
        print(f"❌ Unknown command: {command}")
        print("Run without arguments to see available commands")


if __name__ == "__main__":
    main()
