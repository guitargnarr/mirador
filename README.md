# 🏰 Mirador: Local AI Orchestration Framework

**Privacy-first multi-agent system for chaining Ollama models with intelligent context accumulation**

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Ollama](https://img.shields.io/badge/Powered%20by-Ollama-orange)](https://ollama.com)

---

## 📊 Project Stats

- **25,000** lines of Python and Bash code
- **89** specialized AI agent definitions
- **64** unique agent modelfiles
- **Comprehensive** documentation and test suite
- **100%** local execution (privacy-first)

*Total repository: ~73K lines including documentation and configuration*

---

## 🎯 What is Mirador?

Mirador orchestrates multiple Ollama models into intelligent chains for complex reasoning tasks. Think "LangChain but simpler" - designed for privacy-conscious users who want powerful AI without sending data to the cloud.

### Key Features

✅ **89 Specialized Agents** - Domain experts for code, business, creativity, and more
✅ **Chain Orchestration** - Sequential execution with context accumulation
✅ **100% Local** - All processing on your machine via Ollama
✅ **Privacy-First** - No external APIs, no data sharing
✅ **Apple Silicon Optimized** - Leverages M-series GPU acceleration
✅ **Web UI** - Streamlit interface for easy interaction
✅ **CLI & Python API** - Use via command-line or programmatically

---

## 🚀 Quick Start

### Prerequisites

1. **Install Ollama**
   ```bash
   # macOS
   brew install ollama

   # Linux
   curl -fsSL https://ollama.com/install.sh | sh
   ```

2. **Pull some models**
   ```bash
   ollama pull llama3.2
   ollama pull qwen2.5-coder
   ```

### Installation

```bash
# Clone repository
git clone https://github.com/guitargnarr/mirador.git
cd mirador

# Install Mirador
pip install -e .

# Or with web UI
pip install -e ".[web]"
```

### Usage

**CLI - Single Query:**
```bash
mirador ask llama3.2 "Explain multi-agent systems"
```

**CLI - Agent Chain:**
```bash
mirador chain "Review this code" code-reviewer creative-entrepreneur
```

**Web UI:**
```bash
mirador web
# Opens Streamlit UI at http://localhost:8501
```

**Python API:**
```python
from mirador import Orchestrator

orch = Orchestrator()

# Single query
response = orch.query_single("llama3.2", "Hello!")

# Chain execution
results = orch.run_chain(
    description="Code review",
    models=["code-reviewer", "creative-entrepreneur"],
    initial_prompt="def hello(): print('world')"
)
```

---

## 🏗️ Architecture

```
User Query
    ↓
[Mirador Orchestrator]
    ↓
Agent 1 (Ollama Model) → Output 1
    ↓
Agent 2 (gets Output 1 as context) → Output 2
    ↓
Agent 3 (gets Output 1 + 2) → Final Answer
    ↓
Save to ~/mirador_outputs/
```

### How It Works

1. **Agent Selection**: Choose specialized agents for your task
2. **Sequential Execution**: Each agent processes output from previous agents
3. **Context Accumulation**: Knowledge builds through the chain
4. **Local Processing**: Everything runs on your machine via Ollama
5. **Output Persistence**: Results saved with full chain history

---

## 🤖 Agent Library

Mirador includes 89 specialized agents across domains:

### Code & Development
- `code-reviewer` - Bug detection and code quality
- `master-coder` - Code optimization and refactoring
- `ux-designer` - UI/UX design recommendations

### Business & Strategy
- `creative-entrepreneur` - Business applications and opportunities
- `decision-simplifier` - Complex decision making
- `content-strategist` - Content planning and strategy

### Creative & Media
- `digital-storyteller` - Narrative and content creation
- `audio-production-strategist` - Music production workflows
- `guitar-expert` - Guitar practice and music theory

### Analysis & Research
- `ai-leadership-strategist` - AI strategy and planning
- `cross-model-synthesizer` - Multi-perspective synthesis
- `engagement-optimizer` - Audience engagement strategies

*See `models/domain/` for all 64 agent definitions*

---

## 📦 Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up

# Access web UI
open http://localhost:8501
```

The Docker container includes:
- Ollama LLM runtime
- Mirador framework
- Streamlit web UI
- Default models pre-loaded

---

## 🛠️ Development

### Install for Development

```bash
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest tests/ -v
```

### Code Quality

```bash
# Format
black src/

# Lint
flake8 src/

# Type check
mypy src/
```

---

## 📚 Documentation

- [Quick Start Guide](docs/QUICKSTART.md)
- [Agent Creation Guide](docs/guides/creating_agents.md)
- [API Reference](docs/technical/API.md)
- [Architecture Overview](docs/ARCHITECTURE.md)

---

## 🎯 Use Cases

- **Code Review Chains**: `code-reviewer → creative-entrepreneur → decision-maker`
- **Content Creation**: `digital-storyteller → content-strategist → engagement-optimizer`
- **Decision Support**: `analyst → synthesizer → decision-simplifier`
- **Learning & Research**: `domain-expert → cross-model-synthesizer → practical-implementer`

---

## 🔒 Privacy & Security

**100% Local Execution:**
- All AI processing happens on your machine
- No data sent to external APIs
- No API keys or cloud accounts needed
- Complete control over your data

**Ideal For:**
- Healthcare professionals (HIPAA compliance)
- Legal work (client confidentiality)
- Financial analysis (proprietary data)
- Personal use (privacy-conscious users)

---

## 🚀 Performance

**Optimized for Apple Silicon:**
- Leverages Metal GPU acceleration
- Multi-threaded model execution
- Efficient context management

**Benchmarks (M1 Max):**
- Single query: ~2-5 seconds
- 3-agent chain: ~10-15 seconds
- Memory usage: ~4-8 GB (varies by model)

---

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Areas for contribution:**
- Additional agent definitions
- Performance optimizations
- New chain templates
- Documentation improvements

---

## 📈 Roadmap

- [ ] Vector database integration for RAG
- [ ] Parallel agent execution
- [ ] Model result caching
- [ ] Web API (REST endpoints)
- [ ] Cloud deployment options
- [ ] Model fine-tuning utilities

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file

---

## 👤 Author

**Matthew Scott** - AI Engineer | Multi-Agent Systems
📧 matthewdscott7@gmail.com
🔗 [LinkedIn](https://linkedin.com/in/mscott77)
💻 [Portfolio](https://jaspermatters.com)

---

## 🙏 Acknowledgments

Built with:
- [Ollama](https://ollama.com) - Local LLM runtime
- [Streamlit](https://streamlit.io) - Web UI framework
- Various open-source LLMs (Llama, Gemma, Qwen, Command-R)

---

**⭐ Star this repo if you find it useful!**
