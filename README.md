# What Is an Agent? - Interactive Demo

An educational Jupyter notebook that demonstrates how to build an AI agent from scratch, showing the core concepts of tools, state management, context handling, and planning.

## 🎯 What You'll Learn

- **What makes an AI agent** different from a simple LLM
- **Tool creation and management** for agent interactions
- **Context management** to maintain conversation coherence
- **State tracking** to help agents understand their environment
- **Error recovery** mechanisms for robust operation
- **Trace logging** for debugging and analysis

## 📋 Prerequisites

- Python 3.8 or higher
- OpenAI API key (get one at [platform.openai.com](https://platform.openai.com))
- Basic familiarity with Python and Jupyter notebooks

## 🚀 Quick Start

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

### 5. Run the Notebook

Start Jupyter:

```bash
jupyter notebook Agent_Demo_Clean.ipynb
```

Or use JupyterLab:

```bash
jupyter lab
```

Then open `Agent_Demo_Clean.ipynb` and run the cells in order.

## 📁 Project Structure

```
what-is-an-agent/
├── Agent_Demo_Clean.ipynb   # Main educational notebook
├── create_sample_data.py     # Generates sample CSV files
├── .env.template            # Template for environment variables
├── .env                     # Your API key (create from template)
├── README.md               # This file
├── data/                   # Sample data files (created by script)
│   ├── sales.csv
│   ├── hr.csv
│   └── leads.csv
└── workings/              # Agent outputs (created during execution)
    ├── agent_trace.txt    # Complete execution trace
    ├── *.csv              # Intermediate analysis results
    └── *.png              # Generated visualizations
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

**Happy Learning! 🎓** Build your own agents and explore the possibilities of AI-powered automation.