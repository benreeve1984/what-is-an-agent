"""Core agent implementation extracted from the notebook."""
import os
import re
import json
import pandas as pd
import numpy as np
import duckdb
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from dataclasses import dataclass, field, asdict
from typing import Any, Callable, Dict, List, Optional, Tuple
from datetime import datetime
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


# Configuration
MODEL = os.getenv("AGENT_MODEL", "gpt-5-mini")
MAX_AGENT_STEPS = 20


@dataclass
class AgentConfig:
    """Configuration for the agent."""
    model: str = MODEL
    temperature: float = 1.0  # gpt-5-mini only supports default temperature
    max_tokens: int = 4000
    max_steps: int = MAX_AGENT_STEPS
    api_key: Optional[str] = None


@dataclass
class StepResult:
    """Result from a single agent step."""
    step_number: int
    prompt: str
    assistant_text: str
    tool_traces: List[Dict[str, Any]]
    new_state: Dict[str, Any]
    is_complete: bool = False


@dataclass
class Tool:
    """Tool definition."""
    name: str
    description: str
    parameters: List[Dict[str, str]]
    func: Callable
    examples: List[str] = field(default_factory=list)


class ToolRegistry:
    """Manages all available tools for the agent."""
    
    def __init__(self):
        self.tools = {}
    
    def register(self, tool: Tool):
        """Register a new tool."""
        self.tools[tool.name] = tool
    
    def get_instructions(self) -> str:
        """Generate formatted instructions for all tools."""
        instructions = ["Available tools:\n"]
        for tool in self.tools.values():
            params_str = ", ".join([f"{p['name']}: {p['type']}" for p in tool.parameters])
            instructions.append(f"- {tool.name}({params_str}): {tool.description}")
            if tool.examples:
                instructions.append(f"  Example: {tool.examples[0]}")
        return "\n".join(instructions)
    
    def call(self, tool_name: str, **kwargs) -> Any:
        """Execute a tool by name with given parameters."""
        if tool_name not in self.tools:
            raise ValueError(f"Tool '{tool_name}' not found")
        return self.tools[tool_name].func(**kwargs)


def parse_tool_calls(text: str) -> List[Dict[str, Any]]:
    """Parse tool calls from agent's response."""
    tool_calls = []
    
    pattern = r'<tool>(.*?)</tool>'
    matches = re.findall(pattern, text, re.DOTALL)
    
    for match in matches:
        match = match.strip()
        
        call_pattern = r'^(\w+)\s*\((.*)\)$'
        call_match = re.match(call_pattern, match, re.DOTALL)
        
        if not call_match:
            continue
        
        tool_name = call_match.group(1)
        params_str = call_match.group(2).strip()
        
        params = {}
        if params_str:
            param_pattern = r'(\w+)\s*=\s*(?:"([^"\\]*(?:\\.[^"\\]*)*)"|([^,\)]+))'
            param_matches = re.findall(param_pattern, params_str)
            
            for param_name, quoted_value, unquoted_value in param_matches:
                param_value = quoted_value if quoted_value else unquoted_value.strip()
                param_value = param_value.replace('\\"', '"').replace('\\n', '\n')
                
                if param_value.lower() in ['true', 'false']:
                    params[param_name] = param_value.lower() == 'true'
                elif param_value.isdigit():
                    params[param_name] = int(param_value)
                else:
                    try:
                        params[param_name] = float(param_value)
                    except:
                        params[param_name] = param_value
        
        tool_calls.append({
            'name': tool_name,
            'parameters': params
        })
    
    return tool_calls


class ContextManager:
    """Manages the agent's context window and state."""
    
    def __init__(self, tables: Dict[str, pd.DataFrame], max_context_tokens: int = 8000):
        self.max_tokens = max_context_tokens
        self.state_summary = {}
        self.recent_errors = []
        self.current_step = 0
        self.max_steps = MAX_AGENT_STEPS
        self.tables = tables  # Reference to shared TABLES dict
        
    def update_state(self):
        """Update the current state summary."""
        self.state_summary = {
            "tables": {name: {"rows": len(df), "columns": list(df.columns)} 
                      for name, df in self.tables.items()},
            "recent_errors": self.recent_errors[-3:] if self.recent_errors else []
        }
    
    def set_step(self, step: int):
        """Update the current step number."""
        self.current_step = step
    
    def add_error(self, tool_name: str, error: str):
        """Track errors with recovery hints."""
        error_entry = {
            "tool": tool_name,
            "error": error,
            "hint": self._get_error_hint(error)
        }
        self.recent_errors.append(error_entry)
        if len(self.recent_errors) > 5:
            self.recent_errors.pop(0)
    
    def _get_error_hint(self, error: str) -> str:
        """Generate helpful hints based on error type."""
        error_lower = error.lower()
        
        if "not found" in error_lower or "catalog error" in error_lower:
            return "Check available tables with examine_table"
        elif "column" in error_lower or "binder error" in error_lower:
            return "Use examine_table to see correct column names"
        elif "syntax" in error_lower:
            return "Check SQL syntax - ensure proper quotes and formatting"
        elif "permission" in error_lower:
            return "Check file path and permissions"
        return "Review the error message and adjust your approach"
    
    def get_state_context(self) -> str:
        """Generate formatted state summary for the agent."""
        lines = ["### Current State:"]
        
        remaining_steps = self.max_steps - self.current_step
        lines.append(f"\n**Progress: Step {self.current_step}/{self.max_steps}** ({remaining_steps} steps remaining)")
        if remaining_steps <= 5:
            lines.append("⚠️ **Warning**: Only a few steps remaining. Prioritize completing your analysis.")
        
        if self.state_summary.get("tables"):
            lines.append("\n**Available Tables:**")
            for name, info in self.state_summary["tables"].items():
                cols = ", ".join(info["columns"][:5])
                if len(info["columns"]) > 5:
                    cols += f", ... ({len(info['columns'])-5} more)"
                lines.append(f"- `{name}`: {info['rows']} rows | Columns: {cols}")
        else:
            lines.append("\n**No tables loaded yet**")
        
        if self.state_summary.get("recent_errors"):
            lines.append("\n**Recent Errors (with hints):**")
            for err in self.state_summary["recent_errors"]:
                lines.append(f"- {err['tool']}: {err['error']}")
                lines.append(f"  💡 Hint: {err['hint']}")
        
        return "\n".join(lines)
    
    def format_tool_results(self, tool_results: list) -> str:
        """Format tool execution results clearly."""
        formatted = ["### Tool Execution Results:\n"]
        
        success_count = sum(1 for r in tool_results if not "Error" in r)
        error_count = sum(1 for r in tool_results if "Error" in r)
        
        formatted.append(f"✅ Successful: {success_count} | ❌ Failed: {error_count}\n")
        
        for result in tool_results:
            if "Error" in result:
                formatted.append(f"• ❌ {result}")
            else:
                formatted.append(f"• {result}")
        
        return "\n".join(formatted)


class AgentIO:
    """Pluggable I/O hooks for agent events."""
    
    def on_step_start(self, step: int): pass
    def on_tool_call(self, tool_name: str, params: Dict): pass
    def on_tool_result(self, tool_name: str, result: Any): pass
    def on_model_request(self, prompt: str): pass
    def on_model_result(self, assistant_text: str): pass
    def on_step_end(self, step: int, result: StepResult): pass


class Agent:
    """Main agent implementation."""
    
    def __init__(self, config: AgentConfig, registry: ToolRegistry, io: Optional[AgentIO] = None):
        self.config = config
        self.registry = registry
        self.io = io or AgentIO()
        self.tables = {}  # Shared tables dict
        self.context_mgr = ContextManager(self.tables, max_context_tokens=8000)
        
        # Initialize OpenAI client
        api_key = config.api_key or os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("Missing OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key)
        
        # Initialize tools that need access to tables
        self._init_tools()
    
    def _init_tools(self):
        """Initialize built-in tools."""
        from tools import (
            list_data_files, load_csv_factory, examine_table_factory,
            sql_query_factory, analyze_statistics_factory, create_chart_factory
        )
        
        # Register tools
        self.registry.register(Tool(
            name="list_data_files",
            description="List all CSV files in a folder to discover available data",
            parameters=[{"name": "folder", "type": "str"}],
            func=list_data_files,
            examples=['<tool>list_data_files(folder="data")</tool>']
        ))
        
        self.registry.register(Tool(
            name="load_csv",
            description="Load a CSV file into memory as a queryable table",
            parameters=[{"name": "path", "type": "str"}, {"name": "name", "type": "str"}],
            func=load_csv_factory(self.tables),
            examples=['<tool>load_csv(path="data/sales.csv", name="sales")</tool>']
        ))
        
        self.registry.register(Tool(
            name="examine_table",
            description="Examine a table's structure, data types, and sample values",
            parameters=[{"name": "name", "type": "str"}],
            func=examine_table_factory(self.tables),
            examples=['<tool>examine_table(name="sales")</tool>']
        ))
        
        self.registry.register(Tool(
            name="sql_query",
            description="Execute SQL queries on loaded tables using DuckDB",
            parameters=[{"name": "query", "type": "str"}, {"name": "save_as", "type": "str"}],
            func=sql_query_factory(self.tables),
            examples=['<tool>sql_query(query="SELECT * FROM sales LIMIT 5", save_as="sample")</tool>']
        ))
        
        self.registry.register(Tool(
            name="analyze_statistics",
            description="Compute statistical summaries for numeric columns",
            parameters=[{"name": "table", "type": "str"}, {"name": "column", "type": "str"}, {"name": "group_by", "type": "str"}],
            func=analyze_statistics_factory(self.tables),
            examples=['<tool>analyze_statistics(table="sales", column="amount", group_by="region")</tool>']
        ))
        
        self.registry.register(Tool(
            name="create_chart",
            description="Create bar, line, scatter, or histogram charts",
            parameters=[
                {"name": "chart_type", "type": "str"},
                {"name": "table", "type": "str"},
                {"name": "x", "type": "str"},
                {"name": "y", "type": "str"},
                {"name": "title", "type": "str"},
                {"name": "xlabel", "type": "str"},
                {"name": "ylabel", "type": "str"},
                {"name": "color", "type": "str"}
            ],
            func=create_chart_factory(self.tables),
            examples=['<tool>create_chart(chart_type="bar", table="weekly", x="day", y="revenue", title="Revenue by Day")</tool>']
        ))
    
    def compose_prompt(self, state: Dict[str, Any]) -> str:
        """Compose the full prompt for the model."""
        system_prompt = f"""You are a senior financial analyst with expertise in data analysis and visualization.
Your role is to analyze business data, identify patterns, and provide actionable insights.

## Your Approach:
1. First, discover and understand available data
2. Create a clear analysis plan
3. Execute analysis using appropriate tools
4. Visualize findings effectively
5. Provide professional insights

## Tool Usage:
Use XML tags for tool calls: <tool>tool_name(param1="value1", param2="value2")</tool>

{self.registry.get_instructions()}

## Guidelines:
- Start by discovering available data files
- Examine data structure before analysis
- Use SQL for data transformations
- Create clear visualizations
- Provide specific, quantified insights
- Save intermediate results for reproducibility
- Be mindful of your step count and complete your analysis efficiently
"""
        
        # Build conversation from state
        messages = state.get("messages", [])
        if not messages:
            # Initial state
            self.context_mgr.update_state()
            initial_context = self.context_mgr.get_state_context()
            goal = state.get("goal", "Analyze the data")
            full_prompt = f"{system_prompt}\n\nTask: {goal}\n\n{initial_context}"
        else:
            # Construct full conversation
            full_prompt = system_prompt + "\n\n"
            for msg in messages:
                if msg["role"] == "user":
                    full_prompt += f"User: {msg['content']}\n\n"
                elif msg["role"] == "assistant":
                    full_prompt += f"Assistant: {msg['content']}\n\n"
        
        return full_prompt
    
    def run_step(self, state: Dict[str, Any]) -> StepResult:
        """Run a single step of the agent."""
        step_num = state.get("step", 1)
        self.context_mgr.set_step(step_num)
        self.io.on_step_start(step_num)
        
        # Compose prompt
        prompt = self.compose_prompt(state)
        self.io.on_model_request(prompt)
        
        # Get messages for API call
        messages = self._build_messages(state)
        
        # Call the model
        response = self.client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            max_completion_tokens=self.config.max_tokens,
            timeout=120
        )
        
        assistant_text = response.choices[0].message.content
        self.io.on_model_result(assistant_text)
        
        # Parse and execute tool calls
        tool_calls = parse_tool_calls(assistant_text)
        tool_traces = []
        
        if tool_calls:
            for tool_call in tool_calls:
                tool_name = tool_call['name']
                params = tool_call['parameters']
                
                self.io.on_tool_call(tool_name, params)
                
                try:
                    result = self.registry.call(tool_name, **params)
                    tool_traces.append({
                        "tool": tool_name,
                        "params": params,
                        "result": result,
                        "error": None
                    })
                    self.io.on_tool_result(tool_name, result)
                except Exception as e:
                    error_msg = str(e)
                    tool_traces.append({
                        "tool": tool_name,
                        "params": params,
                        "result": None,
                        "error": error_msg
                    })
                    self.context_mgr.add_error(tool_name, error_msg)
                    self.io.on_tool_result(tool_name, {"error": error_msg})
        
        # Update state
        self.context_mgr.update_state()
        
        # Check if complete
        is_complete = any(keyword in assistant_text.lower() 
                         for keyword in ["final", "conclusion", "summary", "insights:"])
        
        # Build new state
        new_messages = state.get("messages", []).copy()
        new_messages.append({"role": "assistant", "content": assistant_text})
        
        if tool_traces:
            # Add tool results to conversation
            tool_results = []
            for trace in tool_traces:
                if trace["error"]:
                    tool_results.append(f"Error in {trace['tool']}: {trace['error']}")
                else:
                    tool_results.append(f"Result of {trace['tool']}: {json.dumps(trace['result'], default=str)}")
            
            formatted_results = self.context_mgr.format_tool_results(tool_results)
            state_context = self.context_mgr.get_state_context()
            
            recovery_hint = ""
            if any(t["error"] for t in tool_traces):
                recovery_hint = "\n\n💡 **Recovery Tip:** Check the state above and use examine_table if needed."
            
            new_messages.append({
                "role": "user",
                "content": f"{formatted_results}\n\n{state_context}{recovery_hint}\n\nContinue with your analysis."
            })
        elif not is_complete:
            # Continue conversation
            state_context = self.context_mgr.get_state_context()
            new_messages.append({
                "role": "user",
                "content": f"{state_context}\n\nPlease continue your analysis using the available tools."
            })
        
        new_state = {
            **state,
            "messages": new_messages,
            "step": step_num + 1
        }
        
        result = StepResult(
            step_number=step_num,
            prompt=prompt,
            assistant_text=assistant_text,
            tool_traces=tool_traces,
            new_state=new_state,
            is_complete=is_complete
        )
        
        self.io.on_step_end(step_num, result)
        return result
    
    def _build_messages(self, state: Dict[str, Any]) -> List[Dict[str, str]]:
        """Build messages for OpenAI API."""
        system_prompt = f"""You are a senior financial analyst with expertise in data analysis and visualization.
Your role is to analyze business data, identify patterns, and provide actionable insights.

## Your Approach:
1. First, discover and understand available data
2. Create a clear analysis plan
3. Execute analysis using appropriate tools
4. Visualize findings effectively
5. Provide professional insights

## Tool Usage:
Use XML tags for tool calls: <tool>tool_name(param1="value1", param2="value2")</tool>

{self.registry.get_instructions()}

## Guidelines:
- Start by discovering available data files
- Examine data structure before analysis
- Use SQL for data transformations
- Create clear visualizations
- Provide specific, quantified insights
- Save intermediate results for reproducibility
- Be mindful of your step count and complete your analysis efficiently
"""
        
        messages = [{"role": "system", "content": system_prompt}]
        
        if "messages" not in state or not state["messages"]:
            # Initial message
            self.context_mgr.update_state()
            initial_context = self.context_mgr.get_state_context()
            goal = state.get("goal", "Analyze the data")
            messages.append({"role": "user", "content": f"Task: {goal}\n\n{initial_context}"})
        else:
            # Add conversation history
            for msg in state["messages"]:
                messages.append({"role": msg["role"], "content": msg["content"]})
        
        return messages
    
    def run_loop(self, state: Dict[str, Any], gate: Callable[[], None]) -> Tuple[str, List[StepResult]]:
        """Run the agent loop with gating."""
        results = []
        current_state = state.copy()
        
        for step in range(1, self.config.max_steps + 1):
            # Gate before each step
            gate()
            
            # Run step
            current_state["step"] = step
            result = self.run_step(current_state)
            results.append(result)
            
            # Update state
            current_state = result.new_state
            
            # Check if complete
            if result.is_complete:
                return result.assistant_text, results
        
        return "Analysis incomplete - max steps reached.", results