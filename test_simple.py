#!/usr/bin/env python3
"""Simple test of the agent without OpenAI API."""
import os
import sys
from pathlib import Path
from datetime import datetime

# Mock the OpenAI client for testing
class MockChoice:
    def __init__(self, content):
        self.message = type('obj', (object,), {'content': content})()

class MockResponse:
    def __init__(self, content):
        self.choices = [MockChoice(content)]

class MockOpenAI:
    def __init__(self, api_key=None):
        self.chat = self
        self.completions = self
    
    def create(self, **kwargs):
        # Simple mock response that discovers files
        step_responses = [
            "I'll start by discovering available data files.\n\n<tool>list_data_files(folder=\"data\")</tool>",
            "I found 3 CSV files. Let me load the sales data.\n\n<tool>load_csv(path=\"data/sales.csv\", name=\"sales\")</tool>",
            "Now let me examine the table structure.\n\n<tool>examine_table(name=\"sales\")</tool>",
            "## Final Analysis\n\nI've successfully loaded and examined the sales data. The analysis is complete."
        ]
        
        # Track which step we're on based on message count
        msg_count = len(kwargs.get('messages', []))
        response_idx = min((msg_count - 1) // 2, len(step_responses) - 1)
        
        return MockResponse(step_responses[response_idx])

# Replace OpenAI import in agent_core
import agent_core
agent_core.OpenAI = MockOpenAI

from agent_core import Agent, AgentConfig, AgentIO, ToolRegistry
from events import RunLogger

# Test basic functionality
print("Testing agent core components...")

# Create run directory
run_dir = Path("runs") / "test_simple"
run_dir.mkdir(parents=True, exist_ok=True)

# Initialize logger
logger = RunLogger(run_dir)
print(f"✓ Logger initialized: {run_dir}")

# Create config and registry
config = AgentConfig(max_steps=4, api_key="mock-key")
registry = ToolRegistry()
print("✓ Config and registry created")

# Create agent
try:
    agent = Agent(config, registry, AgentIO())
    print("✓ Agent created successfully")
except Exception as e:
    print(f"✗ Agent creation failed: {e}")
    sys.exit(1)

# Test step execution
try:
    state = {"goal": "Test the agent"}
    result = agent.run_step(state)
    print(f"✓ Step executed: {result.step_number}")
    print(f"  Tool calls: {len(result.tool_traces)}")
except Exception as e:
    print(f"✗ Step execution failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n✅ All basic tests passed!")
print(f"   Events file: {run_dir / 'events.jsonl'}")

# Show first few events
events = logger.get_events()
print(f"   Events logged: {len(events)}")
for i, event in enumerate(events[:3], 1):
    print(f"   {i}. {event['type']}")