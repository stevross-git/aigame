#!/usr/bin/env python3
"""
AI Sims - Setup Test Script
Tests all components to ensure the game will run properly.
"""

import sys
import subprocess
import importlib
import os
from pathlib import Path

def test_python_version():
    """Test Python version compatibility."""
    print("🐍 Testing Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} is too old. Need Python 3.8+")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
    return True

def test_dependencies():
    """Test all Python dependencies."""
    print("\n📦 Testing Python dependencies...")
    
    dependencies = [
        "pygame",
        "numpy", 
        "ollama",
        "requests",
        "chromadb",
        "openai",
        "anthropic",
        "dotenv"
    ]
    
    missing = []
    for dep in dependencies:
        try:
            if dep == "dotenv":
                importlib.import_module("dotenv")
            else:
                importlib.import_module(dep)
            print(f"✅ {dep} - OK")
        except ImportError:
            print(f"❌ {dep} - MISSING")
            missing.append(dep)
    
    if missing:
        print(f"\n❌ Missing dependencies: {', '.join(missing)}")
        print("Run: pip3 install -r requirements.txt")
        return False
    
    return True

def test_ollama():
    """Test Ollama installation and model availability."""
    print("\n🤖 Testing Ollama...")
    
    # Check if ollama command exists
    try:
        result = subprocess.run(["ollama", "--version"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ Ollama installed - {result.stdout.strip()}")
        else:
            print("❌ Ollama not working properly")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("❌ Ollama not found or not responding")
        print("Install with: curl -fsSL https://ollama.com/install.sh | sh")
        return False
    
    # Check if service is running (try to start if not)
    try:
        result = subprocess.run(["ollama", "list"], 
                              capture_output=True, text=True, timeout=15)
        if result.returncode == 0:
            print("✅ Ollama service accessible")
            
            # Check for models
            if "llama2" in result.stdout:
                print("✅ llama2 model available")
            else:
                print("⚠️  llama2 model not found")
                print("Download with: ollama pull llama2")
                return False
        else:
            print("❌ Ollama service not responding")
            print("Start with: ollama serve")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Ollama service timeout")
        return False
    
    return True

def test_directories():
    """Test required directories exist."""
    print("\n📁 Testing directories...")
    
    required_dirs = [
        "src",
        "src/core", 
        "src/entities",
        "src/ai",
        "src/ui",
        "src/world",
        "chroma_db"
    ]
    
    missing = []
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"✅ {dir_path}/ - OK")
        else:
            print(f"❌ {dir_path}/ - MISSING")
            missing.append(dir_path)
    
    if missing:
        print(f"\n❌ Missing directories: {', '.join(missing)}")
        return False
    
    return True

def test_config():
    """Test configuration files."""
    print("\n⚙️ Testing configuration...")
    
    if os.path.exists(".env"):
        print("✅ .env file exists")
    else:
        if os.path.exists(".env.example"):
            print("⚠️  .env missing, but .env.example exists")
            print("Copy with: cp .env.example .env")
        else:
            print("❌ No environment configuration found")
            return False
    
    # Test main game file
    if os.path.exists("main.py"):
        print("✅ main.py exists")
    else:
        print("❌ main.py missing")
        return False
    
    return True

def test_game_imports():
    """Test game module imports."""
    print("\n🎮 Testing game imports...")
    
    try:
        # Add current directory to path for imports
        sys.path.insert(0, os.getcwd())
        
        # Test core imports
        from src.core.constants import SCREEN_WIDTH, SCREEN_HEIGHT
        print("✅ Core constants - OK")
        
        from src.entities.personality import Personality
        print("✅ Personality system - OK")
        
        from src.ai.memory_manager import MemoryManager
        print("✅ Memory manager - OK")
        
        from src.ui.character_creator import CharacterCreator
        print("✅ Character creator - OK")
        
        from src.world.events import EventGenerator
        print("✅ Event system - OK")
        
        print("✅ All game modules importable")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_database():
    """Test database creation."""
    print("\n💾 Testing database setup...")
    
    try:
        from src.ai.memory_manager import MemoryManager
        
        # Test SQLite
        mm = MemoryManager("test_memory.db")
        mm.close()
        
        # Clean up test file
        if os.path.exists("test_memory.db"):
            os.remove("test_memory.db")
        
        print("✅ Database system - OK")
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def run_all_tests():
    """Run all tests and report results."""
    print("🧪 AI Sims - Setup Testing")
    print("=" * 40)
    
    tests = [
        ("Python Version", test_python_version),
        ("Dependencies", test_dependencies), 
        ("Ollama", test_ollama),
        ("Directories", test_directories),
        ("Configuration", test_config),
        ("Game Imports", test_game_imports),
        ("Database", test_database)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} - ERROR: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 TEST SUMMARY")
    print("=" * 40)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20} {status}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("\n🎉 ALL TESTS PASSED!")
        print("🚀 Ready to run: python3 main.py")
        return True
    else:
        print(f"\n⚠️  {len(tests) - passed} tests failed")
        print("❌ Fix issues before running the game")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)