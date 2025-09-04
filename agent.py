#!/usr/bin/env python3
"""CLI runner for the agent with step gating."""
import os
import sys
import argparse
import threading
import webbrowser
from datetime import datetime
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

from agent_core import Agent, AgentConfig, AgentIO, ToolRegistry, StepResult
from events import RunLogger

# Load environment variables from .env file
load_dotenv()


class LoggingAgentIO(AgentIO):
    """AgentIO implementation that logs to RunLogger."""
    
    def __init__(self, logger: RunLogger):
        self.logger = logger
    
    def on_step_start(self, step: int):
        self.logger.step_started(step)
    
    def on_tool_call(self, tool_name: str, params: dict):
        self.logger.tool_call(tool_name, params)
    
    def on_tool_result(self, tool_name: str, result):
        ok = not (isinstance(result, dict) and "error" in result)
        self.logger.tool_result(tool_name, result, ok)
    
    def on_model_request(self, prompt: str):
        self.logger.model_request(prompt)
    
    def on_model_request_with_sections(self, prompt: str, sections: dict, token_counts: dict = None):
        """Handle model request with prompt sections for visualization."""
        self.logger.model_request(prompt, sections, token_counts)
    
    def on_model_result(self, assistant_text: str):
        self.logger.model_result(assistant_text)
    
    def on_step_end(self, step: int, result: StepResult):
        self.logger.step_completed(step)


def create_run_directory(run_id: Optional[str] = None) -> Path:
    """Create a run directory with timestamp."""
    if run_id:
        run_dir = Path("runs") / run_id
    else:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        run_dir = Path("runs") / timestamp
    
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def cli_gate():
    """CLI gate that waits for user to press Enter."""
    input("\nPress ⏎ to run next step... ")


def create_server_gate():
    """Create a server gate using threading.Event with compression support."""
    event = threading.Event()
    compression_requested = threading.Event()
    
    def gate():
        event.clear()
        print("\nWaiting for browser 'Run next step' button... ", end="", flush=True)
        event.wait()
        print("✓")
    
    return gate, event, compression_requested


def run_agent_cli(args):
    """Run the agent in CLI or browser mode."""
    # Create run directory
    run_dir = create_run_directory(args.run_id)
    print(f"📁 Run directory: {run_dir}")
    
    # Initialize logger
    logger = RunLogger(run_dir)
    
    # Create agent configuration
    config = AgentConfig(
        max_steps=args.max_steps or 20,
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # Create registry and agent
    registry = ToolRegistry()
    io = LoggingAgentIO(logger)
    agent = Agent(config, registry, io)
    
    # Define the task
    goal = args.goal or """Analyze daily sales patterns throughout the week. 
Find which days perform best and worst, identify any anomalies or unusual patterns, 
and provide visualizations to support your findings. 
Consider factors like day-of-week effects and any outliers in the data, e.g. public holidays, big sale events.
Provide 3-5 specific insights with quantified impacts."""
    
    print(f"\n📋 Task: {goal}")
    print("\n" + "=" * 60 + "\n")
    
    # Set up gating
    if args.browser:
        # Browser mode - start Flask server
        gate, gate_event, compression_event = create_server_gate()
        
        # Import and start Flask app in thread
        from app import create_app
        app = create_app(run_dir, gate_event, compression_event, agent)
        
        def run_flask():
            app.run(host='127.0.0.1', port=5001, debug=False, use_reloader=False)
        
        flask_thread = threading.Thread(target=run_flask, daemon=True)
        flask_thread.start()
        
        # Open browser
        import time
        time.sleep(1)  # Give Flask a moment to start
        url = f"http://127.0.0.1:5001/run/{run_dir.name}"
        print(f"🌐 Opening browser: {url}")
        webbrowser.open(url)
    else:
        # CLI mode
        gate = cli_gate
    
    # Run the agent
    try:
        state = {"goal": goal}
        if args.browser:
            # Pass compression event for browser mode
            final_answer, results = agent.run_loop_with_compression(state, gate, compression_event)
        else:
            final_answer, results = agent.run_loop(state, gate)
        
        print("\n" + "=" * 60)
        print("✅ ANALYSIS COMPLETE")
        print("=" * 60)
        print("\n### Final Report:\n")
        print(final_answer)
        
        # Log completion
        logger.run_completed()
        
        # Show summary
        events = logger.get_events()
        tool_calls = sum(1 for e in events if e["type"] == "tool_call")
        errors = sum(1 for e in events if e["type"] == "tool_result" and not e.get("ok", True))
        
        print(f"\n📊 Execution Summary:")
        print(f"   Total steps: {len(results)}")
        print(f"   Tool calls: {tool_calls}")
        print(f"   Errors encountered: {errors}")
        print(f"   Events logged: {len(events)}")
        
        # List created files
        workings_dir = Path("workings")
        if workings_dir.exists():
            files = list(workings_dir.glob("*"))
            if files:
                print(f"\n📁 Files created in workings folder:")
                for file in files:
                    size = file.stat().st_size / 1024
                    print(f"   - {file.name}: {size:.1f} KB")
        
        print(f"\n📄 Full trace saved to: {run_dir / 'events.jsonl'}")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Agent interrupted by user")
        logger.log_event({"type": "run_interrupted", "ts": logger._timestamp()})
    except Exception as e:
        print(f"\n❌ Agent failed: {e}")
        logger.log_event({"type": "run_error", "error": str(e), "ts": logger._timestamp()})
        import traceback
        traceback.print_exc()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run the financial analyst agent")
    parser.add_argument("--run-id", help="Optional run ID (default: timestamp)")
    parser.add_argument("--max-steps", type=int, help="Maximum number of steps (default: 20)")
    parser.add_argument("--browser", action="store_true", help="Launch Flask server and open browser")
    parser.add_argument("--goal", help="Custom goal for the agent")
    
    args = parser.parse_args()
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not found")
        print("   Please set it in one of these ways:")
        print("   1. Create a .env file with: OPENAI_API_KEY=your-key-here")
        print("   2. Or export it: export OPENAI_API_KEY='your-key-here'")
        sys.exit(1)
    
    run_agent_cli(args)


if __name__ == "__main__":
    main()