#!/usr/bin/env python3
"""
Mirador Production API
Flask REST API with SSE streaming for real-time chain execution.
"""

import json
import logging
import os
import sys
import time
from datetime import datetime
from typing import Any, Dict, Generator, List

import requests
from flask import Flask, Response, jsonify, request, stream_with_context
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(mesfamily_member)s'
)
logger = logging.getLogger("mirador-api")

app = Flask(__name__)

ALLOWED_ORIGINS = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:3000,http://localhost:5173"
).split(",")

CORS(app, resources={r"/api/*": {"origins": ALLOWED_ORIGINS}})

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["60/minute"],
    storage_uri="memory://",
)

# ============================================================================
# Configuration
# ============================================================================

VERSION = "1.0.0"
OLLAMA_URL = "http://localhost:11434"
DEFAULT_TIMEOUT = 120

# Persona definitions with their Ollama model mappings and prompts
PERSONAS = {
    "master_coder": {
        "model": "llama3.2",
        "description": "Architecture and implementation strategy",
        "category": "development",
        "prompt_template": "You are a senior software architect. Analyze and provide implementation strategy for: {input}",
        "temperature": 0.4
    },
    "code_reviewer": {
        "model": "llama3.2",
        "description": "Code quality analysis and best practices",
        "category": "development",
        "prompt_template": "You are an expert code reviewer. Review this for quality, bugs, and improvements: {input}",
        "temperature": 0.3
    },
    "debug_specialist": {
        "model": "llama3.2",
        "description": "Issue identification and resolution",
        "category": "development",
        "prompt_template": "You are a debugging expert. Identify issues and provide fixes: {input}",
        "temperature": 0.3
    },
    "test_architect": {
        "model": "llama3.2",
        "description": "Testing strategy and coverage",
        "category": "development",
        "prompt_template": "You are a test architect. Design comprehensive test strategy for: {input}",
        "temperature": 0.4
    },
    "security_expert": {
        "model": "llama3.2",
        "description": "Vulnerability assessment and hardening",
        "category": "security",
        "prompt_template": "You are a security expert. Analyze for vulnerabilities and provide security recommendations: {input}",
        "temperature": 0.3
    },
    "performance_optimizer": {
        "model": "llama3.2",
        "description": "Speed and efficiency optimization",
        "category": "development",
        "prompt_template": "You are a performance optimization expert. Analyze and optimize: {input}",
        "temperature": 0.4
    },
    "api_designer": {
        "model": "llama3.2",
        "description": "Interface design and documentation",
        "category": "development",
        "prompt_template": "You are an API design expert. Design clean, RESTful interfaces for: {input}",
        "temperature": 0.5
    },
    "database_architect": {
        "model": "llama3.2",
        "description": "Data modeling and query optimization",
        "category": "development",
        "prompt_template": "You are a database architect. Design optimal data structures for: {input}",
        "temperature": 0.4
    },
    "devops_engineer": {
        "model": "llama3.2",
        "description": "Deployment and infrastructure",
        "category": "development",
        "prompt_template": "You are a DevOps engineer. Plan deployment and infrastructure for: {input}",
        "temperature": 0.4
    },
    "ux_analyst": {
        "model": "llama3.2",
        "description": "User experience evaluation",
        "category": "creative",
        "prompt_template": "You are a UX analyst. Evaluate and improve user experience for: {input}",
        "temperature": 0.6
    },
    "business_analyst": {
        "model": "llama3.2",
        "description": "Requirements and ROI analysis",
        "category": "business",
        "prompt_template": "You are a business analyst. Analyze requirements and ROI for: {input}",
        "temperature": 0.5
    },
    "project_manager": {
        "model": "llama3.2",
        "description": "Timeline and resource planning",
        "category": "business",
        "prompt_template": "You are a project manager. Plan timeline and resources for: {input}",
        "temperature": 0.5
    },
    "documentation_writer": {
        "model": "llama3.2",
        "description": "Technical writing and guides",
        "category": "creative",
        "prompt_template": "You are a technical writer. Create clear documentation for: {input}",
        "temperature": 0.5
    },
    "cross_model_synthesizer": {
        "model": "llama3.2",
        "description": "Pattern identification across outputs",
        "category": "meta",
        "prompt_template": "You are a meta-cognitive synthesizer. Analyze all previous outputs, identify patterns, conflicts, and synthesize into coherent recommendations: {input}",
        "temperature": 0.6
    },
    "feedback_loop_optimizer": {
        "model": "llama3.2",
        "description": "Output refinement and improvement",
        "category": "meta",
        "prompt_template": "You are an output optimizer. Refine and improve the quality of: {input}",
        "temperature": 0.5
    },
    "self_reflection_guardian": {
        "model": "llama3.2",
        "description": "Blindspot identification",
        "category": "meta",
        "prompt_template": "You are a critical reviewer. Identify blindspots, assumptions, and overlooked aspects in: {input}",
        "temperature": 0.6
    }
}

# Chain presets
CHAIN_PRESETS = {
    "security_audit": {
        "name": "Security Audit",
        "description": "Comprehensive security review with meta-cognitive synthesis",
        "personas": ["security_expert", "code_reviewer", "cross_model_synthesizer", "self_reflection_guardian"]
    },
    "code_review": {
        "name": "Code Review",
        "description": "Full code review with testing and feedback optimization",
        "personas": ["master_coder", "code_reviewer", "test_architect", "feedback_loop_optimizer"]
    },
    "architecture": {
        "name": "Architecture Analysis",
        "description": "System design analysis across all technical domains",
        "personas": ["master_coder", "api_designer", "database_architect", "devops_engineer"]
    },
    "business_analysis": {
        "name": "Business Analysis",
        "description": "Requirements and planning analysis",
        "personas": ["business_analyst", "project_manager", "ux_analyst"]
    },
    "full_chain": {
        "name": "Full 16-Persona Chain",
        "description": "Comprehensive analysis through all 16 personas",
        "personas": list(PERSONAS.keys())
    },
    "meta_only": {
        "name": "Meta-Cognitive Only",
        "description": "Meta-cognitive evaluation layer only",
        "personas": ["cross_model_synthesizer", "feedback_loop_optimizer", "self_reflection_guardian"]
    },
    "quick_review": {
        "name": "Quick Review",
        "description": "Fast code review with key insights",
        "personas": ["master_coder", "code_reviewer", "cross_model_synthesizer"]
    }
}

# ============================================================================
# Ollama Integration
# ============================================================================

def check_ollama_health() -> Dict[str, Any]:
    """Check if Ollama is running and available."""
    try:
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            return {
                "status": "healthy",
                "models_available": len(models),
                "model_names": [m.get("name", "unknown") for m in models[:10]]
            }
    except Exception as e:
        logger.error(f"Ollama health check failed: {e}")
    return {"status": "unavailable", "error": "Cannot connect to Ollama"}


def query_ollama(model: str, prompt: str, temperature: float = 0.7, timeout: int = DEFAULT_TIMEOUT) -> Generator[str, None, None]:
    """
    Query Ollama with streaming response.

    Yields chunks of the response as they arrive.
    """
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": True,
        "options": {
            "temperature": temperature,
            "num_gpu": 1,
            "num_thread": 8
        }
    }

    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json=payload,
            stream=True,
            timeout=timeout
        )

        for line in response.iter_lines():
            if line:
                try:
                    chunk = json.loads(line.decode('utf-8'))
                    if "response" in chunk:
                        yield chunk["response"]
                except json.JSONDecodeError:
                    continue

    except requests.exceptions.Timeout:
        yield f"[ERROR: Request timed out after {timeout}s]"
    except Exception as e:
        yield f"[ERROR: {str(e)}]"


def query_ollama_sync(model: str, prompt: str, temperature: float = 0.7, timeout: int = DEFAULT_TIMEOUT) -> str:
    """Query Ollama and return complete response."""
    result = ""
    for chunk in query_ollama(model, prompt, temperature, timeout):
        result += chunk
    return result


# ============================================================================
# Chain Execution
# ============================================================================

def run_persona(persona_id: str, input_text: str, context: str = "") -> Generator[Dict, None, None]:
    """
    Run a single persona and yield streaming results.

    Yields dicts with: {type: 'chunk'|'complete', persona, content, ...}
    """
    if persona_id not in PERSONAS:
        yield {"type": "error", "persona": persona_id, "error": f"Unknown persona: {persona_id}"}
        return

    persona = PERSONAS[persona_id]

    # Build prompt with context
    full_input = input_text
    if context:
        full_input = f"Previous analysis:\n{context}\n\nCurrent task:\n{input_text}"

    prompt = persona["prompt_template"].format(input=full_input)

    # Yield start event
    yield {
        "type": "start",
        "persona": persona_id,
        "description": persona["description"],
        "category": persona["category"],
        "timestamp": datetime.now().isoformat()
    }

    # Stream response
    full_response = ""
    start_time = time.time()

    for chunk in query_ollama(persona["model"], prompt, persona["temperature"]):
        full_response += chunk
        yield {
            "type": "chunk",
            "persona": persona_id,
            "content": chunk
        }

    elapsed = time.time() - start_time

    # Yield completion event
    yield {
        "type": "complete",
        "persona": persona_id,
        "full_response": full_response,
        "tokens": len(full_response.split()),
        "time_ms": int(elapsed * 1000)
    }


def run_chain(input_text: str, persona_ids: List[str]) -> Generator[Dict, None, None]:
    """
    Run a chain of personas with context accumulation.

    Yields events for each step of the chain.
    """
    yield {
        "type": "chain_start",
        "input": input_text,
        "personas": persona_ids,
        "total_steps": len(persona_ids),
        "timestamp": datetime.now().isoformat()
    }

    accumulated_context = ""

    for step, persona_id in enumerate(persona_ids):
        yield {
            "type": "step_start",
            "step": step + 1,
            "total": len(persona_ids),
            "persona": persona_id
        }

        # Run persona
        for event in run_persona(persona_id, input_text, accumulated_context):
            yield event

            # Accumulate context from completed responses
            if event.get("type") == "complete":
                accumulated_context += f"\n\n### {persona_id} Analysis:\n{event.get('full_response', '')}"

    yield {
        "type": "chain_complete",
        "total_personas": len(persona_ids),
        "timestamp": datetime.now().isoformat()
    }


# ============================================================================
# API Endpoints
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint."""
    ollama_status = check_ollama_health()

    return jsonify({
        "status": "healthy",
        "version": VERSION,
        "ollama": ollama_status,
        "personas_loaded": len(PERSONAS),
        "chain_presets": len(CHAIN_PRESETS),
        "timestamp": datetime.now().isoformat()
    })


@app.route('/api/personas', methods=['GET'])
def list_personas():
    """List all available personas."""
    personas_list = []
    for pid, pdata in PERSONAS.items():
        personas_list.append({
            "id": pid,
            "description": pdata["description"],
            "category": pdata["category"],
            "model": pdata["model"]
        })

    return jsonify({
        "personas": personas_list,
        "total": len(personas_list),
        "categories": list(set(p["category"] for p in PERSONAS.values()))
    })


@app.route('/api/chains', methods=['GET'])
def list_chains():
    """List available chain presets."""
    chains_list = []
    for cid, cdata in CHAIN_PRESETS.items():
        chains_list.append({
            "id": cid,
            "name": cdata["name"],
            "description": cdata["description"],
            "personas": cdata["personas"],
            "persona_count": len(cdata["personas"])
        })

    return jsonify({
        "chains": chains_list,
        "total": len(chains_list)
    })


@app.route('/api/run', methods=['POST', 'OPTIONS'])
@limiter.limit("10/minute")
def run_chain_endpoint():
    """
    Execute a chain with streaming SSE response.

    POST body:
    {
        "input": "Your query here",
        "chain": "security_audit" | "code_review" | ... (optional, defaults to quick_review)
        "personas": ["persona1", "persona2"] (optional, overrides chain)
    }

    Returns SSE stream of chain execution events.
    """
    if request.method == 'OPTIONS':
        return '', 204

    data = request.json or {}
    input_text = data.get('input', '')

    if not input_text:
        return jsonify({"error": "Missing 'input' field"}), 400

    # Determine which personas to use
    if 'personas' in data:
        persona_ids = data['personas']
    else:
        chain_id = data.get('chain', 'quick_review')
        if chain_id not in CHAIN_PRESETS:
            return jsonify({"error": f"Unknown chain: {chain_id}"}), 400
        persona_ids = CHAIN_PRESETS[chain_id]['personas']

    # Validate personas
    for pid in persona_ids:
        if pid not in PERSONAS:
            return jsonify({"error": f"Unknown persona: {pid}"}), 400

    def generate():
        for event in run_chain(input_text, persona_ids):
            yield f"data: {json.dumps(event)}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'X-Content-Type-Options': 'nosniff'
        }
    )


@app.route('/api/run/<persona_id>', methods=['POST', 'OPTIONS'])
@limiter.limit("10/minute")
def run_single_persona(persona_id: str):
    """
    Execute a single persona.

    POST body:
    {
        "input": "Your query here",
        "context": "Optional previous context"
    }
    """
    if request.method == 'OPTIONS':
        return '', 204

    if persona_id not in PERSONAS:
        return jsonify({"error": f"Unknown persona: {persona_id}"}), 404

    data = request.json or {}
    input_text = data.get('input', '')
    context = data.get('context', '')

    if not input_text:
        return jsonify({"error": "Missing 'input' field"}), 400

    def generate():
        for event in run_persona(persona_id, input_text, context):
            yield f"data: {json.dumps(event)}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'X-Content-Type-Options': 'nosniff'
        }
    )


@app.route('/api/chain/<chain_id>', methods=['POST', 'OPTIONS'])
@limiter.limit("10/minute")
def run_preset_chain(chain_id: str):
    """
    Execute a preset chain by ID.

    POST body:
    {
        "input": "Your query here"
    }
    """
    if request.method == 'OPTIONS':
        return '', 204

    if chain_id not in CHAIN_PRESETS:
        return jsonify({"error": f"Unknown chain: {chain_id}"}), 404

    data = request.json or {}
    input_text = data.get('input', '')

    if not input_text:
        return jsonify({"error": "Missing 'input' field"}), 400

    persona_ids = CHAIN_PRESETS[chain_id]['personas']

    def generate():
        for event in run_chain(input_text, persona_ids):
            yield f"data: {json.dumps(event)}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'X-Content-Type-Options': 'nosniff'
        }
    )


@app.route('/api/run/sync', methods=['POST'])
@limiter.limit("10/minute")
def run_chain_sync():
    """
    Execute a chain and return complete result (non-streaming).
    Useful for simpler clients that don't support SSE.
    """
    data = request.json or {}
    input_text = data.get('input', '')

    if not input_text:
        return jsonify({"error": "Missing 'input' field"}), 400

    # Determine which personas to use
    if 'personas' in data:
        persona_ids = data['personas']
    else:
        chain_id = data.get('chain', 'quick_review')
        if chain_id not in CHAIN_PRESETS:
            return jsonify({"error": f"Unknown chain: {chain_id}"}), 400
        persona_ids = CHAIN_PRESETS[chain_id]['personas']

    # Run chain and collect results
    results = []
    accumulated_context = ""

    for persona_id in persona_ids:
        if persona_id not in PERSONAS:
            continue

        persona = PERSONAS[persona_id]
        full_input = input_text
        if accumulated_context:
            full_input = f"Previous analysis:\n{accumulated_context}\n\nCurrent task:\n{input_text}"

        prompt = persona["prompt_template"].format(input=full_input)

        start_time = time.time()
        response = query_ollama_sync(persona["model"], prompt, persona["temperature"])
        elapsed = time.time() - start_time

        results.append({
            "persona": persona_id,
            "description": persona["description"],
            "category": persona["category"],
            "response": response,
            "tokens": len(response.split()),
            "time_ms": int(elapsed * 1000)
        })

        accumulated_context += f"\n\n### {persona_id}:\n{response}"

    return jsonify({
        "input": input_text,
        "chain": persona_ids,
        "results": results,
        "total_personas": len(results),
        "timestamp": datetime.now().isoformat()
    })


# ============================================================================
# Main
# ============================================================================

if __name__ == '__main__':
    # Ensure logs directory exists
    os.makedirs(os.path.join(os.path.dirname(__file__), 'logs'), exist_ok=True)

    logger.info(f"Starting Mirador API v{VERSION}")
    logger.info(f"Loaded {len(PERSONAS)} personas")
    logger.info(f"Loaded {len(CHAIN_PRESETS)} chain presets")

    # Check Ollama on startup
    ollama_health = check_ollama_health()
    if ollama_health["status"] == "healthy":
        logger.info(f"Ollama connected: {ollama_health['models_available']} models available")
    else:
        logger.warning("Ollama not available - chains will fail until Ollama is started")

    app.run(host='0.0.0.0', port=5001, debug=False, threaded=True)
