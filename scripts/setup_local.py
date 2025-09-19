#!/usr/bin/env python3
"""
Local Development Environment Setup Script

Creates and configures a Python virtual environment for local development
of the Flipside Chat Automation project.
"""

import subprocess
import sys
import os
import platform
from pathlib import Path


def run_command(command, description, check=True, timeout=60):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        if isinstance(command, list):
            # For list commands, don't use shell=True
            result = subprocess.run(command, check=check, capture_output=True, text=True, timeout=timeout)
        else:
            # For string commands, use shell=True
            result = subprocess.run(command, shell=True, check=check, capture_output=True, text=True, timeout=timeout)
        
        if result.stdout:
            print(f"✅ {description} completed")
        return result
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} timed out after {timeout} seconds")
        if check:
            sys.exit(1)
        return None
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        if check:
            sys.exit(1)
        return e


def setup_local_environment():
    """Set up local development environment with virtual environment."""
    print("🚀 Setting up Flipside Chat Automation local development environment")
    print("=" * 70)
    
    # Check Python version
    python_version = sys.version_info
    if python_version < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro} detected")
    
    # Create virtual environment
    print("\n📦 Creating virtual environment...")
    venv_path = Path("venv")
    if venv_path.exists():
        print("⚠️ Virtual environment already exists. Removing...")
        import shutil
        shutil.rmtree(venv_path)
    
    # Try creating virtual environment with timeout
    result = run_command([sys.executable, "-m", "venv", "venv"], "Creating virtual environment", timeout=120)
    
    if result is None or result.returncode != 0:
        print("⚠️ Standard venv creation failed, trying alternative method...")
        # Try with --clear flag
        result = run_command([sys.executable, "-m", "venv", "--clear", "venv"], "Creating virtual environment (alternative)", timeout=120)
        
        if result is None or result.returncode != 0:
            print("❌ Virtual environment creation failed. Please try manually:")
            print(f"   {sys.executable} -m venv venv")
            print("   Then run this script again.")
            sys.exit(1)
    
    # Determine activation script and pip path
    if platform.system() == "Windows":
        activate_script = "venv\\Scripts\\activate"
        pip_path = "venv\\Scripts\\pip"
        python_path = "venv\\Scripts\\python"
    else:  # Unix/Linux/macOS
        activate_script = "venv/bin/activate"
        pip_path = "venv/bin/pip"
        python_path = "venv/bin/python"
    
    # Upgrade pip
    run_command([pip_path, "install", "--upgrade", "pip"], "Upgrading pip")
    
    # Install dependencies
    if Path("requirements.txt").exists():
        run_command([pip_path, "install", "-r", "requirements.txt"], "Installing dependencies")
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
            run_command([pip_path, "install", dep], f"Installing {dep}")
    
    # Create .env file if it doesn't exist
    env_file = Path(".env")
    env_example = Path(".env.example")
    if not env_file.exists() and env_example.exists():
        print("\n📝 Creating .env file from template...")
        with open(env_example, 'r') as f:
            env_content = f.read()
        with open(env_file, 'w') as f:
            f.write(env_content)
        print("✅ .env file created from .env.example")
        print("⚠️ Please edit .env file with your actual values")
    
    # Create necessary directories
    directories = ["screenshots", "logs", "artifacts"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"📁 Created directory: {directory}")
    
    # Test installation
    print("\n🧪 Testing installation...")
    test_result = run_command([python_path, "-c", "import selenium; print('Selenium version:', selenium.__version__)"], 
                             "Testing Selenium import", check=False)
    if test_result.returncode == 0:
        print("✅ Installation test passed")
    else:
        print("⚠️ Installation test failed, but setup may still be successful")
    
    # Print completion message
    print("\n" + "=" * 70)
    print("🎉 Setup complete!")
    print(f"\nTo activate the virtual environment:")
    if platform.system() == "Windows":
        print(f"  {activate_script}")
    else:
        print(f"  source {activate_script}")
    
    print(f"\nTo run the automation:")
    print(f"  {python_path} src/chat_automation.py")
    
    print(f"\nTo install in development mode:")
    print(f"  {pip_path} install -e .")
    
    print(f"\nNext steps:")
    print("1. Activate the virtual environment")
    print("2. Edit .env file with your Flipside cookies")
    print("3. Run the automation script")
    
    return True


if __name__ == "__main__":
    try:
        setup_local_environment()
    except KeyboardInterrupt:
        print("\n⚠️ Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)
