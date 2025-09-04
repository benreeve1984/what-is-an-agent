"""Event logging system for agent runs."""
import json
import os
import math
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, Optional


class RunLogger:
    """Logs agent run events to JSONL file."""
    
    def __init__(self, run_dir: Path):
        """Initialize logger with run directory."""
        self.run_dir = Path(run_dir)
        self.run_dir.mkdir(parents=True, exist_ok=True)
        
        self.events_file = self.run_dir / "events.jsonl"
        self.run_id = self.run_dir.name
        self.current_step = 0
        
        # Log run started
        self.log_event({
            "type": "run_started",
            "run_id": self.run_id,
            "ts": self._timestamp()
        })
    
    def _timestamp(self) -> int:
        """Get current timestamp in seconds since epoch."""
        return int(datetime.now().timestamp())
    
    def _truncate(self, text: str, max_length: int = 500) -> str:
        """Truncate text for preview fields."""
        if len(text) <= max_length:
            return text
        return text[:max_length] + "..."
    
    def _make_serializable(self, obj):
        """Ensure object is JSON serializable, handling NaN and Infinity."""
        if isinstance(obj, float):
            # Handle NaN and Infinity values
            if math.isnan(obj) or math.isinf(obj):
                return None  # Convert to null in JSON
            return obj
        elif isinstance(obj, (str, int, bool, type(None))):
            return obj
        elif isinstance(obj, dict):
            return {k: self._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [self._make_serializable(v) for v in obj]
        else:
            return str(obj)
    
    def log_event(self, event: Dict[str, Any]):
        """Write event to JSONL file."""
        # Ensure all values are JSON serializable
        event = self._make_serializable(event)
        
        with open(self.events_file, 'a', encoding='utf-8') as f:
            json.dump(event, f, ensure_ascii=False)
            f.write('\n')
    
    def step_started(self, step: int):
        """Log step started event."""
        self.current_step = step
        self.log_event({
            "type": "step_started",
            "step": step,
            "ts": self._timestamp()
        })
    
    def model_request(self, prompt: str, sections: dict = None, token_counts: dict = None):
        """Log model request event with optional sections and token counts."""
        event = {
            "type": "model_request",
            "step": self.current_step,
            "prompt": prompt,
            "ts": self._timestamp()
        }
        
        # Add sections if provided
        if sections:
            event["prompt_sections"] = sections
        
        # Add token counts if provided
        if token_counts:
            event["token_counts"] = token_counts
        
        self.log_event(event)
    
    def tool_call(self, name: str, args: Dict[str, Any]):
        """Log tool call event."""
        self.log_event({
            "type": "tool_call",
            "step": self.current_step,
            "name": name,
            "args": args,
            "ts": self._timestamp()
        })
    
    def tool_result(self, name: str, result: Any, ok: bool = True):
        """Log tool result event."""
        # Create preview
        if isinstance(result, dict):
            if "error" in result:
                ok = False
                result_preview = result.get("error", "Unknown error")
            else:
                # Use _make_serializable to handle NaN values before creating preview
                safe_result = self._make_serializable(result)
                result_preview = json.dumps(safe_result)[:500]
        else:
            result_preview = str(result)[:500]
        
        self.log_event({
            "type": "tool_result",
            "step": self.current_step,
            "name": name,
            "ok": ok,
            "result_preview": self._truncate(result_preview),
            "result": result if isinstance(result, (dict, list)) else str(result),
            "ts": self._timestamp()
        })
    
    def model_result(self, assistant_text: str):
        """Log model result event."""
        self.log_event({
            "type": "model_result",
            "step": self.current_step,
            "assistant_preview": self._truncate(assistant_text),
            "assistant_text": assistant_text,
            "ts": self._timestamp()
        })
    
    def step_completed(self, step: int):
        """Log step completed event."""
        self.log_event({
            "type": "step_completed",
            "step": step,
            "ts": self._timestamp()
        })
    
    def run_completed(self):
        """Log run completed event."""
        self.log_event({
            "type": "run_completed",
            "ts": self._timestamp()
        })
    
    def get_events(self) -> list:
        """Read all events from the JSONL file."""
        events = []
        if self.events_file.exists():
            with open(self.events_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        events.append(json.loads(line))
        return events