# Mirador AI Orchestrator

Local-first multi-agent AI framework with meta-cognitive evaluation. **Proven effective for security audits** - found real CORS vulnerability in production code.

## What It Does

- **16 specialized personas** chained for security audits and code analysis
- **Meta-cognitive layer** - models that critique and identify blindspots
- **100% local execution** via Ollama - code never leaves your machine (HIPAA/finance ready)
- **REST API** - Flask API for integration into CI/CD pipelines

## Validated Use Cases

| Chain | Accuracy | Best For |
|-------|----------|----------|
| `security_audit` | **100%** | Finding CORS, auth, injection, secrets issues |
| `architecture` | ~70% | General design review (inject deployment context) |
| `code_review` | Weak | Not recommended (use Claude Code instead) |

**Real Result:** Mirador's security audit chain found a CORS vulnerability (`allow_origins=["*"]` with credentials) in a production API that was subsequently fixed and deployed.

## Quick Start

```bash
# 1. Prerequisites
# Install Ollama: https://ollama.ai

# 2. Clone
git clone https://github.com/guitargnarr/mirador
cd mirador

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start API
python api.py

# 5. Verify
curl http://localhost:5001/api/health
```

## Test Harness

Verify your installation with the included test script:

```bash
./test_mirador.sh
```

## Architecture

```
User Query
    |
    v
+---------------------------------------------------+
|  Flask API (api.py:5001)                          |
|  - /api/run (chain execution)                     |
|  - /api/run/<persona> (single model)              |
|  - /api/webhooks (event notifications)            |
+---------------------------------------------------+
    |
    v
+---------------------------------------------------+
|  AIFramework (framework.py)                       |
|  - Session management                             |
|  - Chain orchestration                            |
|  - Output persistence                             |
+---------------------------------------------------+
    |
    v
+---------------------------------------------------+
|  Persona Chain (16 specialists)                   |
|  master_coder -> code_reviewer -> ... -> ai_specialist |
+---------------------------------------------------+
    |
    v
+---------------------------------------------------+
|  Meta-Cognitive Layer                             |
|  - cross_model_synthesizer: Pattern identification|
|  - feedback_loop_optimizer: Output refinement     |
|  - mirador_self_reflection_guardian: Blindspot ID |
+---------------------------------------------------+
    |
    v
+---------------------------------------------------+
|  Ollama (Local LLM Runtime)                       |
|  - llama3.2, phi4, gemma2:9b, mistral:7b         |
|  - Custom modelfiles with tuned parameters        |
+---------------------------------------------------+
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/personas` | GET | List all personas and chain order |
| `/api/sessions` | GET | List available sessions |
| `/api/run` | POST | Run full chain with input |
| `/api/run/<persona_id>` | POST | Run single persona |
| `/api/webhooks` | GET/POST | Webhook management |

## Example Ufamily_member

```bash
# Run a single persona
curl -X POST http://localhost:5001/api/run/master_coder \
  -H "Content-Type: application/json" \
  -d '{"input": "Write a Python function to validate email addresses"}'

# Run a chain segment
curl -X POST http://localhost:5001/api/run \
  -H "Content-Type: application/json" \
  -d '{"input": "Review this code for security issues", "start_at": "code_reviewer", "end_at": "security_expert"}'
```

## Research Alignment

Mirador implements meta-cognitive patterns aligned with current AI agent research:

- [Microsoft AI Agents Curriculum - Metacognition](https://microsoft.github.io/ai-agents-for-beginners/09-metacognition/)
- [Honda Research - Meta-Cognitive Agentic AI Systems](https://usa.honda-ri.com/-/meta-cognitive-agentic-ai-systems)
- [Self-Evolving Agents (arxiv:2508.00271)](https://arxiv.org/abs/2508.00271)

## Requirements

- Python 3.11+
- Ollama installed and running
- ~50GB disk space for models

## License

MIT
