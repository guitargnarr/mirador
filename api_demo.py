#!/usr/bin/env python3
"""
Mirador Demo API
Showcases the orchestration architecture without requiring local Ollama.
Deploy to Render for public demonstration.
"""

import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

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

VERSION = "2.0.0"
PORT = int(os.environ.get("PORT", 5001))

# Full persona catalog (30 specialists)
PERSONAS = {
    # Development
    "master_coder": {
        "model": "llama3.2",
        "description": "Architecture and implementation strategy",
        "category": "development"
    },
    "code_reviewer": {
        "model": "llama3.2",
        "description": "Code quality analysis and best practices",
        "category": "development"
    },
    "debug_specialist": {
        "model": "llama3.2",
        "description": "Issue identification and resolution",
        "category": "development"
    },
    "security_expert": {
        "model": "llama3.2",
        "description": "Vulnerability assessment and hardening",
        "category": "security"
    },
    "code-executor": {
        "model": "qwen2.5-coder:7b",
        "description": "Python code generation and execution",
        "category": "development"
    },
    "elite-frontend": {
        "model": "llama3.2",
        "description": "React/Vue/frontend architecture",
        "category": "development"
    },

    # Music & Guitar
    "guitar_expert_precise": {
        "model": "llama3.2",
        "description": "Guitar technique and music theory",
        "category": "music"
    },
    "guitar_tone_architect": {
        "model": "llama3.2",
        "description": "Tone shaping and gear recommendations",
        "category": "music"
    },
    "master_guitar_instructor": {
        "model": "llama3.2",
        "description": "Structured guitar lessons and practice plans",
        "category": "music"
    },
    "performance_anxiety_coach": {
        "model": "llama3.2",
        "description": "Stage presence and performance psychology",
        "category": "music"
    },
    "touring_readiness_coach": {
        "model": "llama3.2",
        "description": "Tour preparation and logistics",
        "category": "music"
    },

    # Career & Market
    "louisville_expert_v2": {
        "model": "llama3.2",
        "description": "Louisville KY market intelligence",
        "category": "career"
    },
    "louisville-job-market": {
        "model": "llama3.2",
        "description": "Louisville job market analysis",
        "category": "career"
    },
    "local_market_expert": {
        "model": "llama3.2",
        "description": "Local business and networking insights",
        "category": "career"
    },
    "opportunity_identification_specialist": {
        "model": "llama3.2",
        "description": "Career opportunity detection",
        "category": "career"
    },
    "barrier-breaker": {
        "model": "llama3.2",
        "description": "Hiring tactics and job search strategy",
        "category": "career"
    },

    # Financial
    "financial_planning_expert_v6": {
        "model": "llama3.2",
        "description": "Comprehensive financial planning",
        "category": "financial"
    },
    "financial_calculator": {
        "model": "phi4",
        "description": "Financial calculations and projections",
        "category": "financial"
    },
    "decision_enhancer": {
        "model": "llama3.2",
        "description": "Decision framework and analysis",
        "category": "financial"
    },
    "decision_simplifier_v2": {
        "model": "phi3:mini",
        "description": "Quick decision support",
        "category": "financial"
    },

    # Health & Wellness
    "health_wellness_optimizer": {
        "model": "llama3.2",
        "description": "Health optimization strategies",
        "category": "health"
    },
    "productivity_optimizer": {
        "model": "llama3.2",
        "description": "Workflow and productivity enhancement",
        "category": "health"
    },

    # Meta-Cognitive
    "cross_model_synthesizer": {
        "model": "llama3.2",
        "description": "Pattern identification across outputs",
        "category": "meta"
    },
    "mirador_self_reflection_guardian": {
        "model": "llama3.2",
        "description": "Blindspot and bias detection",
        "category": "meta"
    },
    "feedback_loop_optimizer": {
        "model": "llama3.2",
        "description": "Output refinement and improvement",
        "category": "meta"
    },
    "instruction_generation_specialist": {
        "model": "llama3.2",
        "description": "Actionable instruction creation",
        "category": "meta"
    },
    "fact_validation_specialist": {
        "model": "llama3.2",
        "description": "Fact checking and verification",
        "category": "meta"
    },

    # Utility
    "data-analyzer-qwen": {
        "model": "qwen2.5:7b",
        "description": "Data analysis and insights",
        "category": "utility"
    },
    "quick-advisor-phi": {
        "model": "phi3:mini",
        "description": "Quick advice and responses",
        "category": "utility"
    },
    "humanizer": {
        "model": "llama3.2",
        "description": "Natural language refinement",
        "category": "utility"
    },
}

# Chain definitions
CHAINS = {
    "security_audit": {
        "description": "Comprehensive security analysis",
        "personas": ["security_expert", "code_reviewer", "cross_model_synthesizer"],
        "accuracy": "100%"
    },
    "code_review": {
        "description": "Full code quality assessment",
        "personas": ["master_coder", "code_reviewer", "debug_specialist", "feedback_loop_optimizer"],
        "accuracy": "~85%"
    },
    "life_optimization": {
        "description": "Multi-domain life planning",
        "personas": [
            "financial_planning_expert_v6", "health_wellness_optimizer",
            "productivity_optimizer", "cross_model_synthesizer"
        ],
        "accuracy": "High"
    },
    "guitar_mastery": {
        "description": "Guitar skill development",
        "personas": ["guitar_expert_precise", "master_guitar_instructor", "performance_anxiety_coach"],
        "accuracy": "High"
    },
    "career_acceleration": {
        "description": "Career strategy and job search",
        "personas": [
            "louisville_expert_v2", "opportunity_identification_specialist",
            "barrier-breaker", "cross_model_synthesizer"
        ],
        "accuracy": "High"
    },
    "financial_planning": {
        "description": "Financial strategy and decisions",
        "personas": ["financial_planning_expert_v6", "financial_calculator", "decision_enhancer"],
        "accuracy": "High"
    }
}

# OCEAN personality traits
OCEAN_PROFILE = {
    "openness": {
        "score": 85,
        "chain_impact": "Creative Innovation chains - explores unconventional solutions"
    },
    "conscientiousness": {
        "score": 78,
        "chain_impact": "Family-Conscious Planning - structured, deadline-aware advice"
    },
    "extraversion": {
        "score": 45,
        "chain_impact": "Depth-Focused Networking - quality over quantity connections"
    },
    "agreeableness": {
        "score": 72,
        "chain_impact": "Values-Based Leadership - servant leadership patterns"
    },
    "neuroticism": {
        "score": 35,
        "chain_impact": "Resilience chains - adaptive career development"
    }
}

# ============================================================================
# Demo Response Generator
# ============================================================================


def generate_demo_response(persona_id: str, input_text: str) -> Dict[str, Any]:
    """Generate a demo response showing what the persona would produce."""
    persona = PERSONAS.get(persona_id, {})

    return {
        "persona": persona_id,
        "model": persona.get("model", "unknown"),
        "category": persona.get("category", "unknown"),
        "description": persona.get("description", ""),
        "demo_mode": True,
        "note": "This is a demo response. Full execution requires local Ollama installation.",
        "sample_output": f"[{persona.get('description', persona_id)}] Analysis of: {input_text[:100]}...",
        "would_invoke": f"ollama run {persona.get('model', 'llama3.2')}"
    }


def generate_chain_demo(chain_id: str, input_text: str) -> Dict[str, Any]:
    """Generate a demo chain execution showing the flow."""
    chain = CHAINS.get(chain_id, {})

    steps = []
    for i, persona_id in enumerate(chain.get("personas", []), 1):
        persona = PERSONAS.get(persona_id, {})
        steps.append({
            "step": i,
            "persona": persona_id,
            "model": persona.get("model", "llama3.2"),
            "description": persona.get("description", ""),
            "status": "would_execute"
        })

    return {
        "chain": chain_id,
        "description": chain.get("description", ""),
        "accuracy": chain.get("accuracy", "Unknown"),
        "steps": steps,
        "total_personas": len(steps),
        "demo_mode": True,
        "note": "Chain execution requires local Ollama. This shows the execution flow.",
        "input_preview": input_text[:200] + "..." if len(input_text) > 200 else input_text
    }

# ============================================================================
# API Endpoints
# ============================================================================


@app.route("/")
def root():
    """Root endpoint with API info."""
    return jsonify({
        "name": "Mirador AI Orchestrator API",
        "version": VERSION,
        "description": "30 specialized personas with conductor-based orchestration",
        "demo_mode": True,
        "endpoints": {
            "/api/health": "Health check",
            "/api/personas": "List all 30 personas",
            "/api/personas/<id>": "Get persona details",
            "/api/chains": "List available chains",
            "/api/chains/<id>": "Get chain details",
            "/api/ocean": "OCEAN personality profile",
            "/api/stats": "System statistics",
            "/api/audit": "Self-audit results (July 2025)",
            "/api/architecture": "Architecture documentation",
            "/api/run": "Run chain (demo mode)",
            "/api/run/<persona>": "Run single persona (demo mode)"
        },
        "github": "https://github.com/guitargnarr/mirador",
        "landing_page": "https://mirador-9kfgysimq-matthew-scotts-projects-1dc9743e.vercel.app",
        "api_docs": "https://github.com/guitargnarr/mirador#try-the-api"
    })


@app.route("/api/health")
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "version": VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "demo_mode": True,
        "personas_loaded": len(PERSONAS),
        "chains_available": len(CHAINS)
    })


@app.route("/api/personas")
def list_personas():
    """List all available personas."""
    by_category = {}
    for pid, pdata in PERSONAS.items():
        cat = pdata.get("category", "other")
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append({
            "id": pid,
            "model": pdata.get("model"),
            "description": pdata.get("description")
        })

    return jsonify({
        "total": len(PERSONAS),
        "by_category": by_category,
        "categories": list(by_category.keys())
    })


@app.route("/api/personas/<persona_id>")
def get_persona(persona_id: str):
    """Get details for a specific persona."""
    if persona_id not in PERSONAS:
        return jsonify({"error": f"Persona '{persona_id}' not found"}), 404

    persona = PERSONAS[persona_id]
    return jsonify({
        "id": persona_id,
        **persona
    })


@app.route("/api/chains")
def list_chains():
    """List all available chains."""
    chain_list = []
    for cid, cdata in CHAINS.items():
        chain_list.append({
            "id": cid,
            "description": cdata.get("description"),
            "persona_count": len(cdata.get("personas", [])),
            "accuracy": cdata.get("accuracy")
        })

    return jsonify({
        "total": len(CHAINS),
        "chains": chain_list
    })


@app.route("/api/chains/<chain_id>")
def get_chain(chain_id: str):
    """Get details for a specific chain."""
    if chain_id not in CHAINS:
        return jsonify({"error": f"Chain '{chain_id}' not found"}), 404

    chain = CHAINS[chain_id]
    personas_detail = []
    for pid in chain.get("personas", []):
        if pid in PERSONAS:
            personas_detail.append({
                "id": pid,
                **PERSONAS[pid]
            })

    return jsonify({
        "id": chain_id,
        "description": chain.get("description"),
        "accuracy": chain.get("accuracy"),
        "personas": personas_detail
    })


@app.route("/api/ocean")
def get_ocean():
    """Get OCEAN personality profile."""
    return jsonify({
        "description": "Big Five personality integration for personalized recommendations",
        "traits": OCEAN_PROFILE,
        "impact": "Personality data shapes which specialists activate and how they frame recommendations"
    })


@app.route("/api/stats")
def get_stats():
    """Get system statistics."""
    categories = {}
    for pdata in PERSONAS.values():
        cat = pdata.get("category", "other")
        categories[cat] = categories.get(cat, 0) + 1

    models = {}
    for pdata in PERSONAS.values():
        model = pdata.get("model", "unknown")
        models[model] = models.get(model, 0) + 1

    return jsonify({
        "personas": {
            "total": len(PERSONAS),
            "by_category": categories
        },
        "chains": {
            "total": len(CHAINS),
            "names": list(CHAINS.keys())
        },
        "models": {
            "unique": len(models),
            "distribution": models
        },
        "architecture": {
            "conductor": "conductor.py - Dynamic task routing",
            "mesfamily_member_bus": "mesfamily_member_bus.py - Bidirectional communication",
            "specialist_handler": "specialist_handler.py - Model invocation",
            "intervention_manager": "intervention_manager.py - Human-in-the-loop"
        },
        "lines_of_code": {
            "python": "30,000+",
            "shell_scripts": 877
        }
    })


@app.route("/api/run", methods=["POST"])
@limiter.limit("10/minute")
def run_chain():
    """Run a chain (demo mode)."""
    data = request.get_json() or {}
    input_text = data.get("input", "")
    chain_id = data.get("chain", "code_review")

    if not input_text:
        return jsonify({"error": "Missing 'input' field"}), 400

    if chain_id not in CHAINS:
        return jsonify({"error": f"Chain '{chain_id}' not found", "available": list(CHAINS.keys())}), 404

    return jsonify(generate_chain_demo(chain_id, input_text))


@app.route("/api/run/<persona_id>", methods=["POST"])
@limiter.limit("10/minute")
def run_persona(persona_id: str):
    """Run a single persona (demo mode)."""
    if persona_id not in PERSONAS:
        return jsonify({"error": f"Persona '{persona_id}' not found"}), 404

    data = request.get_json() or {}
    input_text = data.get("input", "")

    if not input_text:
        return jsonify({"error": "Missing 'input' field"}), 400

    return jsonify(generate_demo_response(persona_id, input_text))


@app.route("/api/audit")
def get_self_audit():
    """
    Self-audit endpoint - demonstrates Mirador's ability to analyze its own architecture.
    This returns the actual audit results from July 2025 that the LinkedIn article references.
    """
    return jsonify({
        "audit_date": "2025-07-09T17:13:39.883914",
        "audit_type": "self_analysis",
        "description": "Mirador analyzed its own model inventory and identified optimization opportunities",

        "findings": {
            "total_models_analyzed": 74,
            "duplicates_found": {
                "exact_duplicates": 1,
                "details": [{
                    "models": ["llama3.2:3b", "llama3.2:latest"],
                    "hash_match": "50d140eb45be6330292f5f813dbf670a",
                    "storage_waste": "2 GB"
                }]
            },
            "consolidation_opportunities": {
                "count": 71,
                "description": "71 models share the same base LLM architecture",
                "base_llm": "llama3.2",
                "recommendation": "Route through 8 universal models instead of 71 specialized variants"
            },
            "diversity_analysis": {
                "before": {
                    "unique_base_llms": 2,
                    "diversity_percentage": "5.4%",
                    "risk": "Single-vendor dependency on Llama family"
                },
                "after": {
                    "unique_base_llms": 5,
                    "diversity_percentage": "~20%",
                    "models_added": ["Gemma 2", "Qwen 2.5", "Phi-3", "Command-R"]
                }
            }
        },

        "actions_taken": {
            "approved_by": "human (one-click approval)",
            "executed": "2025-07-10",
            "changes": [
                "Removed 1 exact duplicate (saved 2 GB)",
                "Consolidated routing through 8 universal models",
                "Added 4 diverse base LLMs",
                "Created full audit trail"
            ]
        },

        "governance": {
            "human_in_the_loop": True,
            "reversible": True,
            "audit_trail": "All decisions logged with justification",
            "git_commit": "c5ef7ad - Implement Ollama model optimizations"
        },

        "source_files": {
            "analysis_script": "analyze_model_duplicates.py",
            "results_file": "ollama_duplicate_analysis.json",
            "implementation": "optimize_mirador_chains.sh"
        }
    })


@app.route("/api/architecture")
def get_architecture():
    """Get architecture documentation."""
    return jsonify({
        "overview": "Conductor-based orchestration with bidirectional communication",
        "flow": [
            "1. User Query → Conductor Agent",
            "2. Conductor analyzes task, selects optimal persona chain",
            "3. Mesfamily_member Bus enables specialist communication",
            "4. Persona Chain executes (30 specialists available)",
            "5. Meta-Cognitive Layer critiques and synthesizes",
            "6. Ollama executes local LLM inference"
        ],
        "components": {
            "conductor.py": {
                "lines": 16709,
                "purpose": "Dynamic task routing and chain selection"
            },
            "mesfamily_member_bus.py": {
                "lines": 25567,
                "purpose": "Bidirectional agent communication, session management"
            },
            "specialist_handler.py": {
                "lines": 20762,
                "purpose": "Model invocation and response handling"
            },
            "intervention_manager.py": {
                "lines": 33267,
                "purpose": "Human-in-the-loop intervention support"
            },
            "framework.py": {
                "lines": 28421,
                "purpose": "Main orchestration and session management"
            }
        },
        "base_models": [
            "llama3.2 - Primary reasoning",
            "phi4 - Fast decisions",
            "qwen2.5 - Multilingual/code",
            "deepseek-r1 - Deep reasoning",
            "gemma2 - Efficient analysis"
        ]
    })

# ============================================================================
# Main
# ============================================================================


if __name__ == "__main__":
    logger.info(f"Starting Mirador Demo API v{VERSION} on port {PORT}")
    logger.info(f"Loaded {len(PERSONAS)} personas, {len(CHAINS)} chains")
    app.run(host="0.0.0.0", port=PORT, debug=False)
