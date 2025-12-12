# Mirador Knowledge Compact
**Generated:** 2025-12-11 | **Status:** Operational | **API:** localhost:5001

---

## What Mirador IS

A **self-evolving AI orchestration system** that chains specialized language models for multi-perspective analysis. Not just AI tooling - an intelligence ecosystem that learns from itself.

### Core Stats
| Metric | Value |
|--------|-------|
| Development | ~500+ hours |
| Models | 65+ specialized |
| Scripts | 90+ automation |
| Outputs | 3,110 production |
| Success | 99.3% |
| Speed | 847 tok/s, 45s avg |

### Breakthrough Innovations
1. **cross_model_synthesizer** - Identifies patterns across specialists
2. **feedback_loop_optimizer** - Self-improves from outputs
3. **enhanced_agent_enforcer** - Meta-cognitive reflection
4. **mirador_self_reflection_guardian** - System self-analysis

---

## Architecture

### 16 Core Personas (in chain order)
```
master_coder → code_reviewer → file_reviewer → creative_entrepreneur
→ rag_node → ux_designer → data_scientist → system_architect
→ security_expert → guitar_expert → content_creator → task_planner
→ database_specialist → mobile_developer → devops_engineer → ai_specialist
```

### 9 Domain Chains
- **development_chain** - Software development
- **security_chain** - Security analysis
- **music_chain** - Guitar/music career
- **business_chain** - Business strategy
- **content_chain** - Content creation
- **finance_chain** - Financial planning
- **productivity_chain** - Productivity optimization
- **creative_chain** - Creative development
- **strategic_chain** - Strategic planning

### Key Components
```
framework.py      - AIFramework class (session mgmt, chain execution)
api.py            - Flask REST API (port 5001)
webhook_handler.py - Event notification system
config.json       - Personas, chains, optional nodes
```

---

## API Endpoints (localhost:5001)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/health` | GET | Health check |
| `/api/personas` | GET | List all personas |
| `/api/sessions` | GET | List sessions |
| `/api/sessions/<id>` | GET | Session info |
| `/api/run` | POST | Run full chain |
| `/api/run/<persona>` | POST | Run single persona |
| `/api/webhooks` | GET/POST | Webhook management |

### Run Chain Example
```bash
curl -X POST http://localhost:5001/api/run \
  -H "Content-Type: application/json" \
  -d '{"input": "Create a guitar practice schedule", "end_at": "task_planner"}'
```

---

## Installed Models (Sanitized)

### New Base Models (Dec 2025)
- phi4 (9.1 GB)
- gemma2:9b (5.4 GB)
- mistral:7b (4.4 GB)

### Sanitized Context-Free
- local_market_expert
- universal_context_provider
- productivity_optimizer
- health_wellness_optimizer
- content_strategist_pro
- llama3.2_balanced

### Specialized (Meta-Cognitive)
- cross_model_synthesizer
- mirador_self_reflection_guardian
- decision_enhancer

### Domain Specialists
- master_guitar_instructor
- guitar_tone_architect
- touring_readiness_coach
- performance_anxiety_coach
- financial_planning_expert_v6
- linkedin_voice_architect
- digital_asset_curator

---

## Key Scripts (90+)

### Daily Operations
- `morning_intelligence_brief.sh`
- `opportunity_dashboard.sh`
- `quick_linkedin_post.sh`

### Weekly Analysis
- `weekly_deep_analysis.sh`
- `weekly_strategic_deep_dive.sh`
- `weekly_theme_generator.sh`

### System Maintenance
- `system_maintenance.sh`
- `mirador_maintenance.sh`
- `validate_production_readiness.sh`

### Performance
- `monitor_mirador_performance.sh`
- `ultimate_performance_dashboard.sh`
- `output_quality_analyzer.sh`

---

## Ufamily_member Patterns

### Quick Query
```bash
./mirador-smart-v2 "Your question here"
```

### Custom Chain
```bash
./mirador-ez chain "Query" model1 model2 model3
```

### API Chain
```bash
curl -X POST http://localhost:5001/api/run \
  -d '{"input": "...", "start_at": "master_coder", "end_at": "code_reviewer"}'
```

---

## Strategic Value

### Documented Assessments
- **Technical Innovation:** 9.5/10
- **Market Potential:** 9.0/10
- **Architectural Quality:** 9.0/10
- **Domain Expertise:** 9.5/10
- **Overall Value:** 9.4/10

### Unique Differentiators
1. **100% Local** - No cloud dependencies
2. **Self-Evolving** - Learns from its own outputs
3. **Meta-Cognitive** - Can analyze itself
4. **Production-Proven** - 99.3% success rate
5. **Privacy-First** - Complete data control

### Market Position
- First-of-kind sophisticated local AI orchestration
- Enterprise-ready architecture
- Publishable research innovations

---

## File Locations

```
/Users/matthewscott/Projects/Security-Tools/mirador-test/
├── framework.py          # Core AIFramework class
├── api.py                # REST API
├── config.json           # Configuration
├── sanitized_modelfiles/ # Portable models (no personal context)
├── scripts/              # Automation scripts
├── src/ai_framework/     # Source modules
├── docs/                 # Technical documentation
├── tests/                # Test suites
└── Documentation and Saved Assets/  # Analysis & value docs
```

---

## Quick Start (After Recovery)

```bash
# 1. Verify API running
curl http://localhost:5001/api/health

# 2. List available personas
curl http://localhost:5001/api/personas

# 3. Run a query
curl -X POST http://localhost:5001/api/run/guitar_expert \
  -H "Content-Type: application/json" \
  -d '{"input": "Design a 30-day practice plan"}'
```

---

**Tagline:** "Observe. Adapt. Remain."
**Brand:** Watchtower theme
**Status:** Recovered, Operational, Sanitized
