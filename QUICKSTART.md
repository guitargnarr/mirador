# 🚀 Mirador Quick Start Guide

Get up and running with Mirador in 5 minutes.

---

## Prerequisites

1. **macOS or Linux** (tested on macOS Sonoma, Ubuntu 22.04)
2. **Python 3.9+**
3. **Ollama installed** (see below)

---

## Installation Steps

### 1. Install Ollama

**macOS:**
```bash
brew install ollama
```

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Start Ollama:**
```bash
ollama serve
# Leave this running in a terminal
```

### 2. Download AI Models

Pull at least one model:
```bash
# Quick & small (1.3 GB)
ollama pull phi3

# General purpose (4.7 GB)
ollama pull llama3.2

# Code-focused (18 GB)
ollama pull qwen2.5-coder:32b
```

### 3. Install Mirador

```bash
# Clone repository
git clone https://github.com/guitargnarr/mirador.git
cd mirador

# Install
pip install -e .

# With web UI (recommended)
pip install -e ".[web]"
```

---

## First Query

**Test single model:**
```bash
mirador ask llama3.2 "What is multi-agent AI?"
```

You should see a response stream from the model.

---

## First Chain

**Run a 2-agent chain:**
```bash
mirador chain "Analyze this code" llama3.2 qwen2.5-coder
```

When prompted, paste some code or press Enter to use a default example.

---

## Launch Web UI

```bash
mirador web
```

This opens a Streamlit interface at `http://localhost:8501` where you can:
- Query models interactively
- Build custom chains
- Browse the agent library

---

## Next Steps

1. **Explore agents**: Check `models/domain/` for specialized agent definitions
2. **Create custom agent**: See [Agent Creation Guide](docs/guides/creating_agents.md)
3. **Read docs**: Browse `docs/` for advanced usage

---

## Troubleshooting

### "Cannot connect to Ollama"
**Solution:** Make sure Ollama is running: `ollama serve`

### "Model not found"
**Solution:** Pull the model first: `ollama pull <model-name>`

### "Command not found: mirador"
**Solution:** Make sure you installed with `pip install -e .` and your Python bin is in PATH

---

## Quick Commands Reference

```bash
# List installed models
mirador models

# System health check
mirador health

# Launch web UI
mirador web

# Get help
mirador --help
```

---

**You're ready!** Start chaining AI agents for complex tasks. 🎉
