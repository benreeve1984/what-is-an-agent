#!/usr/bin/env python3
"""Demo script for browser mode - starts agent with Flask UI."""
import os
import sys
import time
import subprocess
import signal

print("=" * 60)
print("AGENT BROWSER MODE DEMO")
print("=" * 60)
print()

# Check API key
if not os.getenv("OPENAI_API_KEY"):
    print("❌ Error: OPENAI_API_KEY not set")
    print("   Please set: export OPENAI_API_KEY='your-key-here'")
    sys.exit(1)

print("Starting agent in browser mode...")
print("This will:")
print("1. Launch Flask server on http://127.0.0.1:5000")
print("2. Open your browser to the agent UI")
print("3. Let you control step execution via browser")
print()
print("Press Ctrl+C to stop the demo")
print("-" * 60)

# Simple goal for demo
goal = "Discover available data files, load the sales data, and create a simple visualization of total revenue by region."

try:
    # Start the agent with browser flag
    process = subprocess.Popen(
        ["python", "agent.py", "--browser", "--max-steps", "5", "--goal", goal],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    
    # Show output
    for line in process.stdout:
        print(line, end="")
        if "Opening browser" in line:
            print("\n✅ Browser should have opened!")
            print("   Use the 'Run next step' button to advance the agent")
            print("   Watch the prompt and traces update in real-time")
            print()
    
    # Wait for process
    process.wait()
    
except KeyboardInterrupt:
    print("\n\n⚠️ Stopping demo...")
    process.terminate()
    time.sleep(1)
    if process.poll() is None:
        process.kill()
    print("✅ Demo stopped")
except Exception as e:
    print(f"\n❌ Error: {e}")
    if 'process' in locals():
        process.terminate()

print("\n" + "=" * 60)
print("Demo complete!")