#!/bin/bash
# Install ONLY generic Mirador models (no personal context)
# Created: 2025-12-11

set -e

MIRADOR_DIR="$HOME/Projects/Security-Tools/mirador-test"
cd "$MIRADOR_DIR"

echo "=== Mirador Generic Model Installation ==="
echo "Installing models WITHOUT personal context..."
echo ""

# Generic models to install (verified no personal context)
MODELS=(
    "audio_production_strategist"
    "content_strategist_pro"
    "cross_model_synthesizer"
    "decision_enhancer"
    "decision_simplifier_v2"
    "digital_asset_curator"
    "digital_storyteller"
    "engagement_optimizer"
    "enhanced_agent_enforcer_v2"
    "enhanced_agent_fast_v6"
    "feedback_loop_optimizer"
    "financial_planning_expert_v6"
    "guitar_tone_architect"
    "health_wellness_optimizer"
    "linkedin_voice_architect"
    "master_guitar_instructor"
    "mirador_self_reflection_guardian"
    "opportunity_analyst"
    "opportunity_validator_v2"
    "performance_anxiety_coach"
    "productivity_optimizer"
    "sales_content_creator"
    "touring_readiness_coach"
)

INSTALLED=0
SKIPPED=0
FAILED=0

for model in "${MODELS[@]}"; do
    modelfile="${model}.modelfile"

    # Check if modelfile exists in main dir or optimized_configs
    if [ -f "$modelfile" ]; then
        filepath="$modelfile"
    elif [ -f "optimized_configs/modelfiles/$modelfile" ]; then
        filepath="optimized_configs/modelfiles/$modelfile"
    else
        echo "SKIP: $modelfile not found"
        ((SKIPPED++))
        continue
    fi

    # Check if model already exists
    if ollama list 2>/dev/null | grep -q "^${model}:"; then
        echo "EXISTS: $model already installed"
        ((SKIPPED++))
        continue
    fi

    echo "INSTALLING: $model from $filepath"
    if ollama create "$model" -f "$filepath" 2>/dev/null; then
        echo "SUCCESS: $model"
        ((INSTALLED++))
    else
        echo "FAILED: $model"
        ((FAILED++))
    fi
done

echo ""
echo "=== Installation Complete ==="
echo "Installed: $INSTALLED"
echo "Skipped: $SKIPPED"
echo "Failed: $FAILED"
echo ""
echo "Total models now available:"
ollama list | wc -l
