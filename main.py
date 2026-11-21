"""
Azure AI Foundry Suite - Application Launcher
Author: Arnav Sharma | Chandigarh University
Run: python main.py
"""

import uvicorn
import os
import sys
import webbrowser
import threading
import time

# Ensure root directory is on path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.config import settings

def open_browser():
    time.sleep(1.2)
    webbrowser.open(f"http://127.0.0.1:{settings.PORT}")

if __name__ == "__main__":
    print("=" * 75)
    print("  AZURE AI FOUNDRY SUITE (AI-901 ENTERPRISE SOLUTION)")
    print(f"  Author: {settings.AUTHOR} | Institution: {settings.INSTITUTION}")
    print("=" * 75)
    print(f"  Starting web studio on http://127.0.0.1:{settings.PORT}")
    print("  Press Ctrl+C to terminate the server.\n")
    threading.Thread(target=open_browser, daemon=True).start()
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
