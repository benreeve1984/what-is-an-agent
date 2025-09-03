#!/usr/bin/env python3
"""Demo script that runs the agent in CLI mode with auto-advancing steps."""
import os
import sys
import time
import subprocess
from pathlib import Path

print("=" * 60)
print("AGENT CLI DEMO - Auto-advancing through 3 steps")
print("=" * 60)
print()

# Check API key
if not os.getenv("OPENAI_API_KEY"):
    print("❌ Error: OPENAI_API_KEY not set")
    print("   Please set: export OPENAI_API_KEY='your-key-here'")
    sys.exit(1)

# Simple goal for quick demo
goal = "List available data files and load the sales.csv file into memory. Then examine its structure."

# Create a Python script that auto-advances
auto_script = '''
import sys
import time

# Simulate user pressing Enter 3 times
for i in range(3):
    time.sleep(1)
    print()
    sys.stdout.flush()
'''

# Write auto-advance script
with open("auto_advance.py", "w") as f:
    f.write(auto_script)

try:
    # Run the agent with auto-advance
    process = subprocess.Popen(
        ["python", "agent.py", "--max-steps", "3", "--goal", goal],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    
    # Auto-advance through steps
    for i in range(3):
        time.sleep(0.5)  # Short delay
        process.stdin.write("\n")
        process.stdin.flush()
        print(f"  [Auto-advanced step {i+1}]")
    
    # Wait for completion and get output
    output, _ = process.communicate(timeout=30)
    
    print("\n" + "=" * 60)
    print("AGENT OUTPUT:")
    print("=" * 60)
    print(output)
    
finally:
    # Clean up
    if Path("auto_advance.py").exists():
        os.remove("auto_advance.py")

print("\n✅ Demo complete!")

# Show events from the latest run
runs_dir = Path("runs")
if runs_dir.exists():
    # Get most recent run
    runs = sorted(runs_dir.glob("*"), key=lambda p: p.stat().st_mtime)
    if runs:
        latest = runs[-1]
        events_file = latest / "events.jsonl"
        if events_file.exists():
            print(f"\n📄 Events logged to: {events_file}")
            print("\nFirst 10 lines of events:")
            with open(events_file) as f:
                for i, line in enumerate(f):
                    if i >= 10:
                        break
                    event = eval(line)  # Simple parse for demo
                    print(f"  {i+1}. {event.get('type', 'unknown')}")