#!/usr/bin/env python3
"""
Simple Setup Script - Alternative to setup_local.py

A simplified version that creates the virtual environment step by step
with better error handling and user feedback.
"""

import subprocess
import sys
import os
import platform
from pathlib import Path


def print_step(step, description):
    """Print a step with formatting."""
    print(f"\n{'='*50}")
    print(f"Step {step}: {description}")
    print('='*50)


def run_simple_command(command, description):
    """Run a simple command with basic error handling."""
    print(f"🔄 {description}...")
    print(f"Running: {' '.join(command) if isinstance(command, list) else command}")
    
    try:
        if isinstance(command, list):
            result = subprocess.run(command, check=True, text=True)
        else:
            result = subprocess.run(command, shell=True, check=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with exit code {e.returncode}")
        return False
    except Exception as e:
        print(f"❌ {description} failed with error: {e}")
        return False


def main():
    """Simple setup process."""
    print("🚀 Simple Flipside Chat Automation Setup")
    print("This is a simplified setup process with step-by-step feedback")
    
    # Step 1: Check Python version
    print_step(1, "Checking Python Version")
    python_version = sys.version_info
    print(f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    print("✅ Python version is compatible")
    
    # Step 2: Remove existing venv if it exists
    print_step(2, "Cleaning Up Existing Virtual Environment")
    venv_path = Path("venv")
    if venv_path.exists():
        print("⚠️ Existing virtual environment found, removing...")
        import shutil
        try:
            shutil.rmtree(venv_path)
            print("✅ Existing virtual environment removed")
        except Exception as e:
            print(f"❌ Failed to remove existing venv: {e}")
            print("Please manually delete the 'venv' folder and try again")
            sys.exit(1)
    else:
        print("✅ No existing virtual environment found")
    
    # Step 3: Create virtual environment
    print_step(3, "Creating Virtual Environment")
    print("This may take a few minutes...")
    
    success = run_simple_command([sys.executable, "-m", "venv", "venv"], "Creating virtual environment")
    
    if not success:
        print("\n⚠️ Virtual environment creation failed. Trying alternative approach...")
        print("Attempting to create venv with verbose output...")
        
        # Try with verbose output to see what's happening
        try:
            result = subprocess.run([sys.executable, "-m", "venv", "venv"], 
                                  capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                print("✅ Virtual environment created successfully (alternative method)")
            else:
                print(f"❌ Alternative method also failed:")
                print(f"stdout: {result.stdout}")
                print(f"stderr: {result.stderr}")
                print("\n🔧 Manual setup instructions:")
                print("1. Run: python -m venv venv")
                print("2. Activate: source venv/bin/activate (macOS/Linux) or venv\\Scripts\\activate (Windows)")
                print("3. Install: pip install -r requirements.txt")
                sys.exit(1)
        except subprocess.TimeoutExpired:
            print("❌ Virtual environment creation timed out")
            print("This might be due to system permissions or antivirus software")
            print("\n🔧 Manual setup instructions:")
            print("1. Run: python -m venv venv")
            print("2. Activate: source venv/bin/activate (macOS/Linux) or venv\\Scripts\\activate (Windows)")
            print("3. Install: pip install -r requirements.txt")
            sys.exit(1)
    
    # Step 4: Determine paths
    print_step(4, "Setting Up Paths")
    if platform.system() == "Windows":
        pip_path = "venv\\Scripts\\pip"
        python_path = "venv\\Scripts\\python"
        activate_cmd = "venv\\Scripts\\activate"
    else:
        pip_path = "venv/bin/pip"
        python_path = "venv/bin/python"
        activate_cmd = "source venv/bin/activate"
    
    print(f"Pip path: {pip_path}")
    print(f"Python path: {python_path}")
    print(f"Activate command: {activate_cmd}")
    
    # Step 5: Upgrade pip
    print_step(5, "Upgrading pip")
    success = run_simple_command([pip_path, "install", "--upgrade", "pip"], "Upgrading pip")
    if not success:
        print("⚠️ Pip upgrade failed, but continuing...")
    
    # Step 6: Install dependencies
    print_step(6, "Installing Dependencies")
    if Path("requirements.txt").exists():
        success = run_simple_command([pip_path, "install", "-r", "requirements.txt"], "Installing dependencies")
        if not success:
            print("⚠️ Some dependencies may not have installed correctly")
    else:
        print("⚠️ requirements.txt not found, installing basic dependencies...")
        basic_deps = [
            "selenium>=4.15.0",
            "webdriver-manager>=4.0.0", 
            "python-dotenv>=1.0.0",
            "requests>=2.31.0",
            "pillow>=10.0.0"
        ]
        for dep in basic_deps:
            run_simple_command([pip_path, "install", dep], f"Installing {dep}")
    
    # Step 7: Create directories
    print_step(7, "Creating Directories")
    directories = ["screenshots", "logs", "artifacts"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    # Step 8: Create .env file
    print_step(8, "Setting Up Environment File")
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists() and env_example.exists():
        print("📝 Creating .env file from template...")
        with open(env_example, 'r') as f:
            env_content = f.read()
        with open(env_file, 'w') as f:
            f.write(env_content)
        print("✅ .env file created from .env.example")
        print("⚠️ Please edit .env file with your actual values")
    elif env_file.exists():
        print("✅ .env file already exists")
    else:
        print("⚠️ No .env.example found, creating basic .env file...")
        basic_env = """# Flipside Chat Automation Environment Variables
FLIPSIDE_COOKIES=your_base64_encoded_cookies_here
DEBUG_MODE=false
ANALYSIS_TIMEOUT=60
CHROME_HEADLESS=true
CHROME_WINDOW_SIZE=1920,1080
"""
        with open(env_file, 'w') as f:
            f.write(basic_env)
        print("✅ Basic .env file created")
    
    # Step 9: Test installation
    print_step(9, "Testing Installation")
    test_commands = [
        ([python_path, "-c", "import selenium; print('Selenium version:', selenium.__version__)"], "Testing Selenium"),
        ([python_path, "-c", "import webdriver_manager; print('WebDriver Manager: OK')"], "Testing WebDriver Manager"),
        ([python_path, "-c", "import dotenv; print('Python-dotenv: OK')"], "Testing Python-dotenv"),
    ]
    
    for command, description in test_commands:
        run_simple_command(command, description)
    
    # Final instructions
    print("\n" + "="*60)
    print("🎉 SETUP COMPLETE!")
    print("="*60)
    print(f"\nTo activate the virtual environment:")
    print(f"  {activate_cmd}")
    print(f"\nTo run the automation:")
    print(f"  {python_path} src/chat_automation.py")
    print(f"\nNext steps:")
    print("1. Activate the virtual environment")
    print("2. Edit .env file with your Flipside cookies")
    print("3. Run the automation script")
    print("\nFor help, check the README.md file")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️ Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed with unexpected error: {e}")
        sys.exit(1)
