# ULTRATHINK: Production Mirador Chains

**Created:** 2025-12-11
**Objective:** Make Mirador a production-ready AI orchestration framework with real chains exposed via API

---

## Phase 1: Reality Assessment

### Current State
- **Source Code:** `~/Projects/Security-Tools/mirador-test/`
- **Landing Page:** `~/Projects/projectlavos-monorepo/services/mirador/`
- **Constraint:** Requires local Ollama (~50GB models)

### The Fundamental Question
How do we expose real chains to end users when the system requires local execution?

### Options Matrix

| Option | Description | Pros | Cons |
|--------|-------------|------|------|
| A: Demo Mode API | Serverless returns pre-recorded outputs | Easy deploy, always works | Not real, users can't run their queries |
| B: Local Connect | Landing page connects to user's local Mirador | Real chains, user's data stays local | Requires user setup, CORS issues |
| C: Hybrid | Demo mode + "Connect Local" option | Best of both worlds | More complexity |
| D: API Gateway | Deploy lightweight proxy that routes to user tunnels | Scalable | Complex infrastructure |

**DECISION: Option C (Hybrid)**
- Landing page has "Demo Mode" for showcase
- "Connect to Local Instance" for real ufamily_member
- Source code is the product, landing page is the showroom

---

## Phase 2: Architecture Design

### Component 1: Production Mirador Core (Source)
```
~/Projects/Security-Tools/mirador-test/
├── api.py                    # Flask API (ENHANCE)
├── framework.py              # Chain orchestration (VERIFY)
├── config.json               # Chain configuration (REVIEW)
├── src/ai_framework/         # Core modules
│   ├── __init__.py
│   ├── chain_executor.py     # NEW: Clean chain execution
│   ├── persona_registry.py   # NEW: Dynamic persona management
│   └── output_formatter.py   # NEW: Structured output
├── sanitized_modelfiles/     # Ollama model definitions
└── test_mirador.sh           # Test harness
```

### Component 2: Landing Page API Integration
```
~/Projects/projectlavos-monorepo/services/mirador/
├── src/
│   ├── App.jsx               # ENHANCE with real API calls
│   ├── hooks/
│   │   └── useMiradorAPI.js  # NEW: API connection hook
│   ├── components/
│   │   ├── ChainExecutor.jsx # NEW: Real chain UI
│   │   ├── LocalConnect.jsx  # NEW: Local connection manager
│   │   └── OutputViewer.jsx  # NEW: Streaming output display
│   └── api/
│       └── mirador.js        # NEW: API client
└── vite.config.js            # CORS proxy config
```

### Component 3: API Endpoints (Production)

| Endpoint | Method | Purpose | Response |
|----------|--------|---------|----------|
| `/api/health` | GET | Health check | `{status, version, personas_loaded}` |
| `/api/personas` | GET | List all personas | `{personas: [...], chain_order: [...]}` |
| `/api/chains` | GET | List available chain presets | `{chains: [{id, name, personas, description}]}` |
| `/api/run` | POST | Execute full chain | SSE stream of persona outputs |
| `/api/run/<persona>` | POST | Execute single persona | `{persona, output, tokens, time_ms}` |
| `/api/chain/<preset>` | POST | Execute preset chain | SSE stream |
| `/api/sessions` | GET | List sessions | `{sessions: [...]}` |
| `/api/session/<id>` | GET | Get session details | `{id, inputs, outputs, chain_used}` |

### Component 4: Chain Presets (Real Value)

| Chain ID | Name | Personas | Use Case |
|----------|------|----------|----------|
| `security_audit` | Security Audit | security_expert → code_reviewer → cross_model_synthesizer | Code security review |
| `code_review` | Code Review | master_coder → code_reviewer → test_architect → feedback_optimizer | Full code review |
| `architecture` | Architecture Analysis | master_coder → api_designer → database_architect → devops_engineer | System design |
| `business_analysis` | Business Analysis | business_analyst → project_manager → ux_analyst | Requirements analysis |
| `full_chain` | Full 16-Persona Chain | All 16 personas | Comprehensive analysis |
| `meta_only` | Meta-Cognitive Only | cross_model_synthesizer → feedback_optimizer → self_reflection_guardian | Output improvement |

---

## Phase 3: Parallel Development Plan

### Terminal 1: Source Code - API Enhancement
**Path:** `~/Projects/Security-Tools/mirador-test/`
**Focus:** Production API endpoints with SSE streaming

Tasks:
1. Add SSE streaming to `/api/run`
2. Add chain presets configuration
3. Add `/api/chains` endpoint
4. Add `/api/chain/<preset>` endpoint
5. Add CORS headers for local dev
6. Add proper error handling
7. Add request validation

### Terminal 2: Source Code - Chain Executor
**Path:** `~/Projects/Security-Tools/mirador-test/`
**Focus:** Clean chain execution module

Tasks:
1. Create `src/ai_framework/chain_executor.py`
2. Implement streaming output
3. Add token counting
4. Add timing metrics
5. Add chain preset loader

### Terminal 3: Landing Page - API Integration
**Path:** `~/Projects/projectlavos-monorepo/services/mirador/`
**Focus:** Real API connection in React

Tasks:
1. Create `useMiradorAPI` hook
2. Add local instance connection UI
3. Implement SSE client for streaming
4. Add real chain execution component
5. Add output viewer with streaming

### Terminal 4: Landing Page - UI Components
**Path:** `~/Projects/projectlavos-monorepo/services/mirador/`
**Focus:** Production UI components

Tasks:
1. ChainExecutor component (input, run, view output)
2. LocalConnect component (URL input, connection status)
3. OutputViewer component (streaming display)
4. ChainSelector component (preset picker)

---

## Phase 4: Implementation Details

### API Enhancement (api.py)

```python
# New imports
from flask import Response, stream_with_context
import json

# SSE streaming endpoint
@app.route('/api/run', methods=['POST'])
def run_chain_stream():
    data = request.json
    input_text = data.get('input', '')
    chain_id = data.get('chain', 'full_chain')

    def generate():
        for persona, output in framework.run_chain_streaming(input_text, chain_id):
            yield f"data: {json.dumps({'persona': persona, 'output': output})}\n\n"
        yield f"data: {json.dumps({'done': True})}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Access-Control-Allow-Origin': '*'
        }
    )

# Chain presets endpoint
@app.route('/api/chains', methods=['GET'])
def get_chains():
    return jsonify({
        'chains': [
            {'id': 'security_audit', 'name': 'Security Audit', 'personas': ['security_expert', 'code_reviewer', 'cross_model_synthesizer']},
            {'id': 'code_review', 'name': 'Code Review', 'personas': ['master_coder', 'code_reviewer', 'test_architect', 'feedback_optimizer']},
            # ... more presets
        ]
    })
```

### React API Hook (useMiradorAPI.js)

```javascript
import { useState, useCallback } from 'react'

export function useMiradorAPI(baseUrl = 'http://localhost:5001') {
  const [connected, setConnected] = useState(false)
  const [streaming, setStreaming] = useState(false)
  const [outputs, setOutputs] = useState([])

  const connect = useCallback(async () => {
    try {
      const res = await fetch(`${baseUrl}/api/health`)
      const data = await res.json()
      setConnected(data.status === 'healthy')
      return data
    } catch {
      setConnected(false)
      return null
    }
  }, [baseUrl])

  const runChain = useCallback(async (input, chainId = 'full_chain') => {
    setStreaming(true)
    setOutputs([])

    const eventSource = new EventSource(
      `${baseUrl}/api/run?input=${encodeURIComponent(input)}&chain=${chainId}`
    )

    eventSource.onmesfamily_member = (event) => {
      const data = JSON.parse(event.data)
      if (data.done) {
        eventSource.close()
        setStreaming(false)
      } else {
        setOutputs(prev => [...prev, data])
      }
    }

    eventSource.onerror = () => {
      eventSource.close()
      setStreaming(false)
    }
  }, [baseUrl])

  return { connected, streaming, outputs, connect, runChain }
}
```

---

## Phase 5: Success Criteria

### Source Code (Mirador Core)
- [ ] `/api/run` returns SSE stream
- [ ] `/api/chains` returns preset list
- [ ] `/api/chain/<preset>` executes preset chain
- [ ] CORS enabled for localhost origins
- [ ] Error responses are structured JSON
- [ ] Token counting per persona
- [ ] Timing metrics per persona

### Landing Page
- [ ] "Connect to Local Instance" UI
- [ ] Real-time streaming output display
- [ ] Chain preset selector
- [ ] Connection status indicator
- [ ] Fallback demo mode when not connected
- [ ] Copy-pasteable outputs

### Integration
- [ ] Landing page can connect to local Mirador
- [ ] Chain execution streams to UI
- [ ] Errors display gracefully
- [ ] Works with default localhost:5001

---

## Phase 6: Risk Analysis

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| CORS blocks local connection | High | Add flask-cors, explicit headers |
| SSE not supported in all browsers | Low | Fallback to polling |
| Ollama not running | High | Clear error mesfamily_member, setup guide |
| Models not loaded | High | Health check reports missing models |
| Long chain timeouts | Medium | Per-persona timeout, progress indicator |

---

## Phase 7: Execution Order

1. **API Enhancement** (Terminal 1) - Core streaming
2. **Chain Executor** (Terminal 2) - Clean execution
3. **API Integration** (Terminal 3) - React hooks
4. **UI Components** (Terminal 4) - Interface

All 4 terminals can run in parallel - they touch different files.

---

**STATUS:** READY FOR PARALLEL EXECUTION
