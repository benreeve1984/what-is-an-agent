# What Is an Agent? - Interactive Demo with Context Engineering Visualization

An educational Jupyter notebook and interactive visualization tool that demonstrates how to build an AI agent from scratch, showing the core concepts of tools, state management, context handling, and planning. 

**NEW:** Now includes a Context Engineering module that lets you visualize exactly what prompts are sent to the model at each step, bringing the concept of prompt engineering and context management to life!

## 🎯 What You'll Learn

- **What makes an AI agent** different from a simple LLM
- **Tool creation and management** for agent interactions
- **Context management** to maintain conversation coherence
- **Context Engineering** - NEW! See exactly how prompts are structured and evolve
- **State tracking** to help agents understand their environment
- **Error recovery** mechanisms for robust operation
- **Trace logging** for debugging and analysis

## 📋 Prerequisites

- Python 3.8 or higher
- OpenAI API key (get one at [platform.openai.com](https://platform.openai.com))
- Basic familiarity with Python and Jupyter notebooks

## 🚀 Quick Start

### 🌟 Quick Start for Context Engineering Demo (2 minutes!)

Want to see Context Engineering in action immediately? Follow these steps:

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set your OpenAI API key in .env file
cp .env.template .env
# Edit .env and add your key: OPENAI_API_KEY=your-key-here

# 3. Generate sample data
python create_sample_data.py

# 4. Launch the Context Engineering visualization
python agent.py --browser
```

Your browser will open automatically. Click "Run next step" to watch the agent work while seeing exactly what prompts are being sent!

### Traditional Setup

### 1. Clone or Download the Project

```bash
git clone <repository-url>
cd what-is-an-agent
```

### 2. Set Up Your Environment

Create a virtual environment (recommended):

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Install required packages:

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install openai pandas numpy duckdb matplotlib python-dotenv jupyter
```

### 3. Configure Your API Key

Copy the environment template:

```bash
cp .env.template .env
```

Edit `.env` and add your OpenAI API key:

```
OPENAI_API_KEY=your-api-key-here
```

### 4. Generate Sample Data

The agent needs sample CSV files to analyze. Run the data generation script:

```bash
python create_sample_data.py
```

This creates three CSV files in the `data/` folder:
- `sales.csv` - Sales transaction data (the target file)
- `hr.csv` - HR employee data (decoy)
- `leads.csv` - Sales leads data (decoy)

### 5. Run the Demo

#### Option A: Interactive Browser Mode (NEW! - Recommended for Learning Context Engineering)

Launch the agent with the Context Engineering visualization:

```bash
python agent.py --browser
```

This will:
- Start a Flask server on http://127.0.0.1:5000
- Open your browser automatically
- Show you a beautiful UI with:
  - The **exact prompt** sent to the model at each step
  - **Tool traces** showing what the agent is doing
  - **Assistant responses** in real-time
  - A **"Run next step" button** to control execution

Perfect for webinars and teaching!

#### Option B: Command-Line Mode

Run the agent step-by-step in your terminal:

```bash
python agent.py --max-steps 5
```

Press Enter to advance each step. Great for debugging and quick tests.

#### Option C: Original Jupyter Notebook

Start Jupyter:

```bash
jupyter notebook Agent_Demo.ipynb
```

Or use JupyterLab:

```bash
jupyter lab
```

Then open `Agent_Demo.ipynb` and run the cells in order.

## 🎓 NEW: Context Engineering Visualization

The Context Engineering module brings prompt engineering to life by showing you exactly what's happening inside the agent's "mind" at each step.

### What is Context Engineering?

Context Engineering is the art and science of crafting prompts that guide AI models effectively. It includes:
- **System instructions** - Setting the agent's role and capabilities
- **Tool definitions** - Teaching the agent what tools it can use
- **State management** - Keeping track of what's been done
- **Error recovery** - Helping the agent learn from mistakes
- **Progressive disclosure** - Adding information as needed

### How to Use the Visualization

1. **Launch in browser mode**: `python agent.py --browser`
2. **Watch the prompt structure**: The left panel shows the 10 components of a well-structured prompt
3. **See the full prompt**: The main panel displays the exact text sent to the model
4. **Track tool usage**: Tool calls and results appear below the prompt
5. **Control execution**: Use the "Run next step" button to advance at your own pace

### What You'll See

Each step shows:
- **The complete prompt** including system instructions, available tools, current state, and task
- **Tool traces** with arguments and results
- **Assistant responses** showing the model's reasoning
- **State updates** as the agent learns about its environment

This visualization is perfect for:
- **Teaching prompt engineering** in workshops and webinars
- **Debugging agent behavior** by seeing exactly what the model receives
- **Understanding context management** and how state evolves
- **Learning best practices** for structuring complex prompts

### Key Insights from the Visualization

Watch how the agent:
1. **Starts with minimal context** - just the task and empty state
2. **Discovers information** - finding data files and their structure
3. **Builds understanding** - accumulating knowledge in its context
4. **Recovers from errors** - getting hints when things go wrong
5. **Completes the task** - using all accumulated context effectively

## 📁 Project Structure

```
what-is-an-agent/
├── Agent_Demo.ipynb         # Main educational notebook
├── agent.py                 # CLI/Browser runner with Context Engineering
├── agent_core.py            # Core agent implementation
├── app.py                   # Flask server for browser visualization
├── events.py                # Event logging system
├── tools.py                 # Tool implementations
├── create_sample_data.py    # Generates sample CSV files
├── .env.template            # Template for environment variables
├── .env                     # Your API key (create from template)
├── README.md                # This file
├── requirements.txt         # Python dependencies
├── templates/               # HTML templates for browser UI
│   └── run.html            # Main visualization page
├── static/                  # CSS and JavaScript for UI
│   ├── styles.css          # Styling for the visualization
│   └── client.js           # Real-time updates
├── data/                    # Sample data files (created by script)
│   ├── sales.csv
│   ├── hr.csv
│   └── leads.csv
├── runs/                    # Execution logs (created during runs)
│   └── <timestamp>/
│       └── events.jsonl    # Complete event trace
└── workings/                # Agent outputs (created during execution)
    ├── agent_trace.txt      # Complete execution trace
    ├── *.csv                # Intermediate analysis results
    └── *.png                # Generated visualizations
```

## 🎮 Using the Notebook

### Step-by-Step Guide

1. **Run Setup Cells** (Sections 1-5)
   - Imports and configuration
   - API setup
   - Tool infrastructure
   - Tool implementations
   - Tool registration

2. **Understand Core Components** (Sections 6-8)
   - Context management system
   - Trace logging
   - Agent loop architecture

3. **Run the Agent** (Section 9)
   - Watch the agent discover data files
   - Observe how it analyzes patterns
   - See visualizations being created
   - Read the final insights

4. **Explore Results**
   - Check `workings/agent_trace.txt` for full execution log
   - Review generated CSV files for intermediate results
   - Examine PNG files for visualizations

### What to Expect

The agent will:
1. Discover available CSV files in the `data/` folder
2. Identify which file contains sales data
3. Load and examine the data structure
4. Analyze weekly sales patterns
5. Create visualizations (bar charts, line graphs)
6. Identify anomalies and patterns
7. Provide 3-5 quantified business insights

Typical execution time: 2-4 minutes (depends on API response times)

## 💻 Command-Line Options

The `agent.py` script supports several options:

```bash
# Browser mode with visualization (recommended for learning)
python agent.py --browser

# CLI mode with custom step limit
python agent.py --max-steps 10

# Custom goal/task
python agent.py --goal "Analyze sales by region and create a pie chart"

# Specify a run ID (useful for debugging)
python agent.py --run-id my-analysis-001

# Combine options
python agent.py --browser --max-steps 5 --goal "Find the top performing sales channel"
```

### Understanding the Execution Modes

**Browser Mode (`--browser`)**
- Best for: Teaching, webinars, understanding Context Engineering
- Features: Visual prompt display, step-by-step control, real-time traces
- Use when: You want to see exactly what's happening

**CLI Mode (default)**
- Best for: Quick tests, automation, debugging
- Features: Terminal output, press Enter to advance
- Use when: You're comfortable with command-line interfaces

## 🔧 Customization

### Modify the Task

Edit the `goal` variable in Section 9 to give the agent different analysis tasks:

```python
goal = """Your custom analysis task here..."""
```

### Add New Tools

Create new tools by following the pattern in Section 4:

```python
def my_custom_tool(param1: str, param2: int) -> Dict:
    """Tool description"""
    # Implementation
    return {"result": "data"}

# Register in Section 5
registry.register(Tool(
    name="my_custom_tool",
    description="What it does",
    parameters=[...],
    func=my_custom_tool
))
```

### Adjust Agent Behavior

- **Max steps**: Change `MAX_AGENT_STEPS` (default: 20)
- **Model**: Change `MODEL` to use different GPT models
- **System prompt**: Modify in `create_system_prompt()` function

## 🐛 Troubleshooting

### "Missing OPENAI_API_KEY"
- Make sure you created `.env` from `.env.template`
- Verify your API key is correctly set in `.env`
- Check that `.env` is in the project root directory

### "Request timed out"
- The API might be overloaded - wait a moment and retry
- Check your internet connection
- Verify your API key has credits

### "No such file or directory: 'data/sales.csv'"
- Run `python create_sample_data.py` first
- Make sure you're in the project root directory

### Agent runs out of steps
- Increase `MAX_AGENT_STEPS` (try 25 or 30)
- Simplify the analysis task
- The agent shows remaining steps - it should prioritize completion

## 👨‍🏫 For Educators and Presenters

The Context Engineering visualization is specifically designed for teaching:

### Perfect for Webinars
- **Live demonstration**: Show real AI agent execution step-by-step
- **Audience control**: Let viewers decide when to advance
- **Clear visualization**: Everyone can see the prompt structure
- **Real examples**: Watch actual tool calls and responses

### Teaching Points to Highlight
1. **Prompt Evolution**: Show how context grows with each step
2. **Tool Integration**: Demonstrate how agents use tools effectively
3. **Error Recovery**: Let errors happen and show recovery mechanisms
4. **State Management**: Visualize how agents track their progress
5. **Context Window**: Discuss token limits and optimization

### Sample Teaching Script
```bash
# Start the visualization
python agent.py --browser --goal "Find weekly sales patterns"

# At each step, explain:
# - What's in the prompt (system instructions, tools, state)
# - Why the agent chose specific tools
# - How the context updates after tool execution
# - How errors are handled with recovery hints
```

### Workshop Ideas
- **Prompt Engineering 101**: Use the visualization to teach prompt structure
- **Building AI Agents**: Show the complete agent lifecycle
- **Context Management**: Deep dive into maintaining conversation state
- **Tool Design**: Demonstrate how to create effective agent tools

## 📚 Learning Resources

### Key Concepts Demonstrated

1. **Tool Calling**: How agents interact with external functions
2. **Context Management**: Maintaining conversation state efficiently
3. **Error Recovery**: Helping agents recover from mistakes
4. **Planning**: Breaking complex tasks into steps
5. **Tracing**: Logging for debugging and analysis

### Extensions to Try

- Add a web scraping tool
- Implement a machine learning prediction tool
- Create tools for different data formats (JSON, XML)
- Build a multi-agent system with specialized agents

## 🤝 Contributing

This is an educational project. Feel free to:
- Add new analysis capabilities
- Improve error handling
- Create additional visualizations
- Enhance the context management system

## 📝 Notes

- The step limit (20 steps) is for demonstration purposes
- In production, you'd analyze task patterns to set appropriate limits
- The agent uses GPT-5-mini by default (adjust based on your needs)
- All generated files are saved to `workings/` for inspection

## 📧 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review the agent trace in `workings/agent_trace.txt`
3. Ensure all dependencies are installed correctly
4. Verify your OpenAI API key is active with credits

---

## 🎯 Summary: Context Engineering Made Visible

This project started as a Jupyter notebook demonstrating AI agents. With the new Context Engineering module, it's evolved into a powerful teaching tool that makes the invisible visible.

**What makes this special:**
- **See the prompts**: No more black box - watch exactly what the AI receives
- **Control the pace**: Step through execution at your speed
- **Learn by doing**: Modify goals and see how the agent adapts
- **Teach effectively**: Perfect for workshops, webinars, and tutorials

Whether you're learning prompt engineering, teaching AI concepts, or building your own agents, this visualization brings clarity to the complex world of AI context management.

**Happy Learning! 🎓** Build your own agents and explore the possibilities of AI-powered automation with a deeper understanding of what's really happening under the hood.