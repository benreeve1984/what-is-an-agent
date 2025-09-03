#!/usr/bin/env python3
"""Acceptance test for the agent system."""
import os
import sys
import json
import time
import threading
import subprocess
from pathlib import Path
from datetime import datetime

print("=" * 60)
print("ACCEPTANCE TESTS")
print("=" * 60)
print()

# Test utilities
def test_module_import():
    """Test that all modules can be imported."""
    print("1. Testing module imports...")
    try:
        import agent_core
        import events
        import tools
        from app import create_app
        print("   ✓ All modules imported successfully")
        return True
    except ImportError as e:
        print(f"   ✗ Import failed: {e}")
        return False

def test_event_logging():
    """Test event logging system."""
    print("\n2. Testing event logging...")
    try:
        from events import RunLogger
        
        # Create test run
        test_dir = Path("runs") / "test_acceptance"
        logger = RunLogger(test_dir)
        
        # Log some events
        logger.step_started(1)
        logger.model_request("Test prompt")
        logger.tool_call("test_tool", {"arg": "value"})
        logger.tool_result("test_tool", {"result": "success"})
        logger.model_result("Test response")
        logger.step_completed(1)
        logger.run_completed()
        
        # Read events
        events = logger.get_events()
        assert len(events) == 8, f"Expected 8 events, got {len(events)}"
        assert events[0]["type"] == "run_started"
        assert events[-1]["type"] == "run_completed"
        
        print(f"   ✓ Logged {len(events)} events successfully")
        return True
    except Exception as e:
        print(f"   ✗ Event logging failed: {e}")
        return False

def test_tools():
    """Test tool functionality."""
    print("\n3. Testing tools...")
    try:
        from tools import list_data_files, load_csv_factory
        
        # Test list_data_files
        result = list_data_files("data")
        assert "csv_files" in result
        assert result["count"] == 3
        print(f"   ✓ Found {result['count']} data files")
        
        # Test load_csv
        tables = {}
        load_csv = load_csv_factory(tables)
        result = load_csv("data/sales.csv", "test_sales")
        assert "loaded_rows" in result
        assert result["loaded_rows"] > 0
        print(f"   ✓ Loaded {result['loaded_rows']} rows from sales.csv")
        
        return True
    except Exception as e:
        print(f"   ✗ Tool test failed: {e}")
        return False

def test_flask_server():
    """Test Flask server startup."""
    print("\n4. Testing Flask server...")
    try:
        from app import create_app
        from pathlib import Path
        import threading
        
        # Create test app
        test_dir = Path("runs") / "test_flask"
        test_dir.mkdir(parents=True, exist_ok=True)
        gate_event = threading.Event()
        
        app = create_app(test_dir, gate_event)
        
        # Test app creation
        assert app is not None
        print("   ✓ Flask app created successfully")
        
        # Test routes exist
        rules = [str(rule) for rule in app.url_map.iter_rules()]
        assert "/run/<run_id>" in str(rules)
        assert "/run/<run_id>/events" in str(rules)
        assert "/run/<run_id>/next" in str(rules)
        print(f"   ✓ All required routes registered")
        
        return True
    except Exception as e:
        print(f"   ✗ Flask test failed: {e}")
        return False

def test_cli_gating():
    """Test CLI mode with automated gating."""
    print("\n5. Testing CLI mode (automated)...")
    
    # Skip if no API key
    if not os.getenv("OPENAI_API_KEY"):
        print("   ⚠ Skipping - OPENAI_API_KEY not set")
        return True
    
    try:
        # Simple test goal
        goal = "List the available data files."
        
        # Run agent with single step
        process = subprocess.Popen(
            ["python", "agent.py", "--max-steps", "1", "--goal", goal],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Send newline to advance
        stdout, stderr = process.communicate(input="\n", timeout=10)
        
        # Check for success indicators
        if "Run directory:" in stdout and "Tool Execution Results:" in stdout:
            print("   ✓ CLI mode executed successfully")
            
            # Check for events file
            runs = sorted(Path("runs").glob("*"), key=lambda p: p.stat().st_mtime)
            if runs:
                latest = runs[-1]
                events_file = latest / "events.jsonl"
                if events_file.exists():
                    with open(events_file) as f:
                        event_count = sum(1 for _ in f)
                    print(f"   ✓ Generated {event_count} events")
            
            return True
        else:
            print(f"   ✗ CLI execution failed")
            if stderr:
                print(f"     Error: {stderr[:200]}")
            return False
            
    except subprocess.TimeoutExpired:
        print("   ✗ CLI test timed out")
        process.kill()
        return False
    except Exception as e:
        print(f"   ✗ CLI test failed: {e}")
        return False

# Run all tests
def main():
    results = []
    
    # Run tests
    results.append(("Module imports", test_module_import()))
    results.append(("Event logging", test_event_logging()))
    results.append(("Tools", test_tools()))
    results.append(("Flask server", test_flask_server()))
    results.append(("CLI mode", test_cli_gating()))
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✅ All acceptance tests passed!")
        
        # Show sample events
        print("\nSample events from latest run:")
        runs_dir = Path("runs")
        if runs_dir.exists():
            runs = sorted(runs_dir.glob("*"), key=lambda p: p.stat().st_mtime)
            if runs:
                latest = runs[-1]
                events_file = latest / "events.jsonl"
                if events_file.exists():
                    print(f"File: {events_file}")
                    with open(events_file) as f:
                        for i, line in enumerate(f):
                            if i >= 20:
                                print("...")
                                break
                            print(line.strip())
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        sys.exit(1)

if __name__ == "__main__":
    main()