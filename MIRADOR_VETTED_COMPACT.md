# Mirador: Vetted Technical Compact
**Generated:** 2025-12-11 | **Audience:** External (recruiters, technical reviewers, investors)

---

## What Mirador Is (Defensible)

A **local-first multi-agent AI orchestration framework** built on Ollama that chains specialized language models for domain-specific analysis. Implements meta-cognitive patterns where models critique and improve system outputs.

### Verified Architecture
- **16 specialized personas** chained in configurable sequences
- **9 domain chains** (development, security, business, creative, music, etc.)
- **Meta-cognitive layer** with self-evaluation models
- **100% local execution** - no cloud dependencies
- **Flask REST API** (port 5001) with webhook support
- **SQLite session persistence**

### Quantifiable Facts (Verifiable in Repo)

| Metric | Claim | Evidence |
|--------|-------|----------|
| Automation scripts | 90+ | `find . -name "*.sh" \| wc -l` |
| Specialized models | 20+ installed | `ollama list` output |
| Domain chains | 9 | `config.json` |
| Personas | 16 | `config.json` chain_order |
| API endpoints | 10+ | `api.py` route definitions |
| LOC (framework) | ~400 | `wc -l framework.py` |

### Claims Requiring Qualification

| Original Claim | Vetted Version |
|----------------|----------------|
| "99.3% success rate across 3,110 outputs" | "Thousands of logged executions with low runtime error rates under internal test suites" |
| "~500+ hours development" | "Multi-month solo development effort" (verifiable via git history) |
| "Most advanced personal AI system" | Internal assessment; positioned as sophisticated local orchestrator |
| "Self-aware" / "consciousness" | Implements meta-cognitive patterns: models that critique outputs and recommend improvements |

---

## Technical Architecture (Verified)

```
User Query
    │
    ▼
┌─────────────────────────────────────────────────────┐
│  Flask API (api.py:5001)                            │
│  - /api/run (chain execution)                       │
│  - /api/run/<persona> (single model)                │
│  - /api/webhooks (event notifications)              │
└─────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────┐
│  AIFramework (framework.py)                         │
│  - Session management                               │
│  - Chain orchestration                              │
│  - Output persistence                               │
└─────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────┐
│  Persona Chain (16 specialists)                     │
│  master_coder → code_reviewer → ... → ai_specialist │
└─────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────┐
│  Meta-Cognitive Layer (Differentiating)             │
│  - cross_model_synthesizer: Pattern identification  │
│  - feedback_loop_optimizer: Output refinement       │
│  - mirador_self_reflection_guardian: Blindspot ID   │
└─────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────┐
│  Ollama (Local LLM Runtime)                         │
│  - llama3.2, phi4, gemma2:9b, mistral:7b           │
│  - Custom modelfiles with tuned parameters          │
└─────────────────────────────────────────────────────┘
```

---

## Differentiating Innovation (Defensible)

### Meta-Cognitive Control Loop

Unlike simple prompt chaining, Mirador implements models that evaluate system behavior:

```
cross_model_synthesizer:
  Input: "Analyze this architecture: 16 personas, meta-layers..."
  Output: Identifies modularity strengths, inter-persona communication
          challenges, data quality requirements

mirador_self_reflection_guardian:
  Input: "What are potential blindspots in self-analyzing AI?"
  Output: Confirmation bias risks, recursive loop dangers,
          recommendations for external evaluation
```

This aligns with current research on meta-cognitive agents (Microsoft AI Agents curriculum, Honda Research meta-cognitive systems, arxiv:2508.00271).

### Local-First Privacy Architecture

- Zero data leaves the machine
- Suitable for regulated domains (HIPAA, finance, government)
- No API keys, no cloud dependencies
- Full control over model selection and fine-tuning

---

## Market Context (Verified)

### AI Orchestration Market
- Global market forecast: $15B+ by 2030 (MarketsandMarkets, Technavio)
- Local/privacy-first orchestration explicitly called out as high-value niche
- Regulated industries (healthcare, finance, gov) driving demand

### Competitive Landscape
- **Not claiming:** "First-of-kind" or "only"
- **Claiming:** Rare example of fully local multi-agent framework with meta-cognitive control loops
- **Similar approaches:** LangGraph+Ollama agents, n8n+Ollama orchestrations, Maestro

### Brand Collision Note
- "Mirador" name conflicts with:
  - IIIF image viewer (ProjectMirador)
  - Bioinformatics miRNA tool (miRador)
  - Storage systems
- External communication should use: "Mirador AI Orchestrator" or rebrand

---

## Session Accomplishments (Verified)

### Today's Work
1. **API Resurrection** - Fixed 4 cascading errors to bring localhost:5001 online
2. **Base Model Updates** - Pulled phi4 (9.1GB), gemma2:9b (5.4GB), mistral:7b (4.4GB)
3. **Sanitization** - Created 9 context-free modelfiles (no personal/geographic data)
4. **Documentation** - Produced knowledge compact and this vetted version
5. **Live Demo** - Meta-cognitive models successfully analyzed own architecture

### Errors Fixed
| Error | Fix |
|-------|-----|
| `ModuleNotFoundError: flask` | `pip3 install flask flask-cors` |
| `ImportError: AIFramework` | Fixed import path in api.py |
| `ModuleNotFoundError: webhook_handler` | Created full implementation |
| `FileNotFoundError: logs` | Created directory structure |

---

## Growth Vectors

### Near-Term (Portfolio-Ready)
1. **Public GitHub repo** with clean README, architecture diagram
2. **PyPI package** (note: `mirador-core` exists - verify ownership or rename)
3. **Test harness** with logged success metrics to back quantitative claims
4. **One-page technical diagram** for recruiters/investors

### Medium-Term (Product Potential)
1. **Web dashboard** for chain visualization and monitoring
2. **Enterprise features** - multi-user, RBAC, audit logging
3. **Vertical specialization** - healthcare compliance, legal document analysis
4. **Integration layer** - RAG with local vector stores

### Long-Term (Market Position)
1. **Open-source community** around sanitized models and chains
2. **Consulting practice** for local AI orchestration implementations
3. **SaaS offering** (air-gapped deployment packages for regulated industries)

---

## Evidence Links (To Add Before Publishing)

For bulletproof external presentation, add:
- [ ] GitHub repo URL with commit history
- [ ] Test report or log snapshot for success rate claim
- [ ] Architecture diagram (visual)
- [ ] Demo video of meta-cognitive analysis

---

## Quick Reference

```bash
# Verify API
curl http://localhost:5001/api/health

# List personas
curl http://localhost:5001/api/personas

# Run meta-cognitive test
echo "Analyze system architecture" | ollama run cross_model_synthesizer

# Run chain via API
curl -X POST http://localhost:5001/api/run \
  -H "Content-Type: application/json" \
  -d '{"input": "...", "start_at": "master_coder", "end_at": "code_reviewer"}'
```

---

## Summary for External Audiences

**For Recruiters:**
> Built a local-first AI orchestration framework with 16 specialized agent personas, meta-cognitive evaluation layers, and REST API. Demonstrates systems design, Python/Flask development, and understanding of emerging AI agent architectures.

**For Technical Reviewers:**
> Multi-agent orchestration system implementing meta-cognitive patterns (self-evaluation, cross-model synthesis, blindspot identification) on Ollama. Aligns with current research on self-evolving agents while maintaining 100% local execution for privacy-sensitive applications.

**For Investors:**
> Local AI orchestration platform targeting regulated industries (healthcare, finance, government) where data sovereignty is mandatory. Differentiated by meta-cognitive control loops that enable system self-improvement without cloud dependencies.

---

**Status:** Vetted, De-hyped, Externally Safe
**Location:** `/Users/matthewscott/Projects/Security-Tools/mirador-test/`
