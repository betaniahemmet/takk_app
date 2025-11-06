#!/usr/bin/env python3
"""Quick verification that the app works after our fixes."""

import sys
from pathlib import Path

import requests

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

print("Testing TAKK App...")
print("-" * 50)

BASE_URL = "http://localhost:5000"

tests = [
    ("Health Check", f"{BASE_URL}/health"),
    ("API Levels", f"{BASE_URL}/api/levels"),
    ("API Signs", f"{BASE_URL}/api/signs"),
    ("API Scores", f"{BASE_URL}/api/scores"),
    ("API Distractors", f"{BASE_URL}/api/distractors"),
]

passed = 0
failed = 0

for name, url in tests:
    try:
        response = requests.get(url, timeout=2)
        if response.status_code == 200:
            print(f"{name}: OK")
            passed += 1
        else:
            print(f"{name}: HTTP {response.status_code}")
            failed += 1
    except requests.exceptions.ConnectionError:
        print(f"{name}: Server not running")
        print("\n Start the server first: python run.py")
        sys.exit(1)
    except Exception as e:
        print(f"{name}: {e}")
        failed += 1

print("-" * 50)
print(f"Results: {passed} passed, {failed} failed")

if failed == 0:
    print("🎉 All endpoints working!")
    sys.exit(0)
else:
    print("Some endpoints failed")
    sys.exit(1)
