"""
API Verification & Quick Start Script

Verify that the API setup is complete and functional.
Run this script to test the API without needing curl.

Usage:
    python verify_api.py
"""

import requests
import json
from pathlib import Path
import sys

# Configuration
BASE_URL = "http://localhost:8000"
API_KEY = "test-key-123"

# Color codes for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_header(text):
    """Print formatted header"""
    print(f"\n{Colors.BLUE}{'='*60}")
    print(f"{text}")
    print(f"{'='*60}{Colors.RESET}\n")

def print_success(text):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")

def print_error(text):
    """Print error message"""
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")

def print_info(text):
    """Print info message"""
    print(f"{Colors.YELLOW}ℹ {text}{Colors.RESET}")

def verify_api_running():
    """Verify API is running"""
    print_header("1. Checking if API is running")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print_success(f"API is running at {BASE_URL}")
        return True
    except requests.exceptions.ConnectionError:
        print_error(f"Cannot connect to API at {BASE_URL}")
        print_info("Start the API with: uvicorn src.api:app --reload --port 8000")
        return False
    except Exception as e:
        print_error(f"Error checking API: {str(e)}")
        return False

def check_health():
    """Check API health"""
    print_header("2. Health Check")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print_success("Health check passed")
            print(f"  Status: {data.get('status')}")
            print(f"  Timestamp: {data.get('timestamp')}")
            print(f"  Version: {data.get('version')}")
            return True
        else:
            print_error(f"Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error during health check: {str(e)}")
        return False

def check_authentication():
    """Check API authentication"""
    print_header("3. Authentication Check")
    
    # Test without API key
    print_info("Testing without API key...")
    try:
        response = requests.get(f"{BASE_URL}/strategies")
        if response.status_code == 401:
            print_success("API correctly requires X-API-Key header")
        else:
            print_error(f"Expected 401, got {response.status_code}")
    except Exception as e:
        print_error(f"Error: {str(e)}")
    
    # Test with API key
    print_info("Testing with valid API key...")
    try:
        response = requests.get(
            f"{BASE_URL}/strategies",
            headers={"X-API-Key": API_KEY}
        )
        if response.status_code == 200:
            print_success("API key authentication working")
            return True
        else:
            print_error(f"Authentication failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def check_strategies():
    """Check available strategies"""
    print_header("4. Available Strategies")
    try:
        response = requests.get(
            f"{BASE_URL}/strategies",
            headers={"X-API-Key": API_KEY}
        )
        if response.status_code == 200:
            data = response.json()
            print_success("Strategies retrieved successfully")
            for strategy in data.get('strategies', []):
                desc = data['descriptions'].get(strategy, 'No description')
                print(f"  • {strategy}: {desc}")
            return True
        else:
            print_error(f"Failed to get strategies: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def check_configuration_files():
    """Check if configuration files exist"""
    print_header("5. Configuration Files")
    
    files = [
        ("API", "src/api.py"),
        ("Logger Config", "src/logger_config.py"),
        ("Monitoring", "src/monitoring.py"),
        ("Environment Example", ".env.example"),
        ("Nginx Config", "config/nginx.conf"),
        ("Dockerfile", "Dockerfile"),
        ("Docker Compose", "docker-compose.yml"),
        ("Deployment Guide", "DEPLOYMENT.md"),
    ]
    
    base_path = Path(__file__).parent
    all_exist = True
    
    for name, filepath in files:
        full_path = base_path / filepath
        if full_path.exists():
            print_success(f"{name}: {filepath}")
        else:
            print_error(f"{name}: {filepath} (NOT FOUND)")
            all_exist = False
    
    return all_exist

def check_requirements():
    """Check if required packages are installed"""
    print_header("6. Required Packages")
    
    packages = [
        "fastapi",
        "uvicorn",
        "pydantic",
        "python-multipart",
        "slowapi",
        "python-dotenv",
    ]
    
    all_installed = True
    for package in packages:
        try:
            __import__(package.replace("-", "_"))
            print_success(f"{package} is installed")
        except ImportError:
            print_error(f"{package} is NOT installed")
            all_installed = False
    
    if not all_installed:
        print_info("Install missing packages with: pip install -r requirements.txt")
    
    return all_installed

def main():
    """Run all verification checks"""
    print(f"\n{Colors.BLUE}")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║     Advanced RAG API - Setup Verification Script          ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(f"{Colors.RESET}")
    
    # Run checks
    checks = [
        ("Configuration Files", check_configuration_files),
        ("Required Packages", check_requirements),
        ("API Running", verify_api_running),
        ("Health Check", check_health),
        ("Authentication", check_authentication),
        ("Available Strategies", check_strategies),
    ]
    
    results = {}
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print_error(f"Error in {name}: {str(e)}")
            results[name] = False
    
    # Summary
    print_header("Summary")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"Checks passed: {passed}/{total}\n")
    
    for name, result in results.items():
        status = f"{Colors.GREEN}PASS{Colors.RESET}" if result else f"{Colors.RED}FAIL{Colors.RESET}"
        print(f"  [{status}] {name}")
    
    # Next steps
    if passed == total:
        print_header("✓ Setup Complete!")
        print("Your API is ready to use! Here are some next steps:")
        print("\n1. Test the API with curl:")
        print("   curl http://localhost:8000/health")
        print("\n2. View interactive documentation:")
        print(f"   {BASE_URL}/docs")
        print("\n3. Try a query:")
        print("   curl -X POST http://localhost:8000/query \\")
        print("     -H 'X-API-Key: test-key-123' \\")
        print("     -H 'Content-Type: application/json' \\")
        print("     -d '{\"query\": \"What is machine learning?\"}'")
        print("\n4. View monitoring:")
        print("   tail -f logs/app.log")
    else:
        print_header("⚠ Setup Incomplete")
        print("Please fix the failing checks above before using the API.")
        sys.exit(1)

if __name__ == "__main__":
    main()
