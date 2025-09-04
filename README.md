# What Is an Agent? - Interactive Demo with Context Engineering

An educational tool that demonstrates how AI agents work, featuring a Context Engineering visualization that shows exactly what prompts are sent to the model at each step.

## 🎯 What You'll Learn

- **What makes an AI agent** different from a simple LLM
- **Tool creation and management** for agent interactions
- **Context management** to maintain conversation coherence
- **Context Engineering** - See exactly how prompts are structured and evolve
- **State tracking** to help agents understand their environment
- **Error recovery** mechanisms for robust operation

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- OpenAI API key (get one at [platform.openai.com](https://platform.openai.com))

### Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd what-is-an-agent
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure your API key**
```bash
cp .env.template .env
# Edit .env and add your key: OPENAI_API_KEY=your-key-here
```

4. **Generate sample data**
```bash
python create_sample_data.py
```

## 🎮 Running the Demo

### Option 1: Browser Mode with Context Visualization (Recommended)

Launch the agent with real-time visualization:

```bash
python agent.py --browser
```

This opens a browser showing:
- The **exact prompt structure** sent to the model (6 color-coded sections)
- **Agent responses** with full reasoning
- **Tool execution traces**
- A **"Run next step" button** for controlled execution

Perfect for understanding how context builds up and teaching prompt engineering!

### Option 2: Command-Line Mode

Run step-by-step in your terminal:

```bash
python agent.py --max-steps 5
```

Press Enter to advance each step.

### Option 3: Original Jupyter Notebook

Explore the concepts interactively:

```bash
jupyter notebook Agent_Demo.ipynb
```

## 📋 Understanding the Context Structure

The visualization shows the prompt in 6 distinct sections:

1. **System Role** - Agent's identity and expertise
2. **Approach & Guidelines** - How the agent should work
3. **Available Tools** - Tool definitions and usage
4. **User's Task** - The original request
5. **History (incl. tool responses)** - Complete conversation with all tool results
6. **Current State** - Tables loaded, errors, and progress

Each section is color-coded to help you understand how different types of context contribute to the agent's decision-making.

## 📁 Project Structure

```
what-is-an-agent/
├── agent.py                 # CLI/Browser runner
├── agent_core.py           # Core agent implementation
├── app.py                  # Flask server for browser UI
├── events.py               # Event logging system
├── tools.py                # Tool implementations
├── create_sample_data.py   # Generate sample CSV files
├── Agent_Demo.ipynb        # Original educational notebook
├── templates/              # HTML templates
│   └── run.html
├── static/                 # CSS and JavaScript
│   ├── styles.css
│   └── client.js
├── data/                   # Sample data (generated)
├── runs/                   # Execution logs
└── workings/               # Agent outputs
```

## 💻 Command-Line Options

```bash
# Browser mode with visualization
python agent.py --browser

# CLI mode with custom steps
python agent.py --max-steps 10

# Custom goal
python agent.py --goal "Analyze sales by region"

# Combine options
python agent.py --browser --max-steps 5
```

## 🔧 How It Works

The agent:
1. **Discovers** available data files
2. **Loads** relevant CSV files into memory
3. **Examines** data structure
4. **Analyzes** using SQL and statistics
5. **Creates** visualizations
6. **Provides** insights

At each step, the Context Engineering visualization shows exactly what the model sees, helping you understand how agents maintain memory and make decisions.

## 🐛 Troubleshooting

### "Missing OPENAI_API_KEY"
- Ensure `.env` file exists with your API key
- Check that you're in the project root directory

### "No such file or directory: 'data/sales.csv'"
- Run `python create_sample_data.py` first

### Browser doesn't open automatically
- Navigate manually to http://localhost:7654
- Check console for any error messages

## 📚 Key Concepts

**Tools**: Functions the agent can call (file discovery, CSV loading, SQL queries, charts)

**Context Management**: How the agent maintains conversation state across steps

**Context Engineering**: The art of structuring prompts for optimal model performance

**State Tracking**: Keeping track of loaded tables, errors, and progress

## 🤝 Contributing

This is an educational project. Feel free to:
- Add new tools and capabilities
- Improve the visualization
- Enhance error handling
- Create additional examples

## 📝 License

MIT License - See LICENSE file for details