#!/bin/bash
# Mirador Universal Runner v3 - Optimized with diverse models

# Configuration
MIRADOR_HOME="${HOME}/Projects/mirador"

# Source metrics logger
source "${MIRADOR_HOME}/bin/mirador_metrics.sh"

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RESET='\033[0m'

# Check arguments
if [ $# -lt 2 ]; then
    echo "Usage: $0 <chain_type> <prompt> [format]"
    echo ""
    echo "Chain types:"
    echo "  life_optimization    - Personal productivity & wellness"
    echo "  business_acceleration - Career & business strategy"
    echo "  creative_breakthrough - Innovation & creative work"
    echo "  relationship_harmony  - Communication & relationships"
    echo "  technical_mastery    - Technology & programming"
    echo "  strategic_synthesis  - High-level planning"
    echo "  deep_analysis       - Complex reasoning (Gemma-powered)"
    echo "  global_insight      - Multilingual & cultural (Qwen-powered)"
    echo "  rapid_decision      - Fast decisions (Phi-powered)"
    echo ""
    echo "Formats: quick, summary, detailed (default), export"
    exit 1
fi

CHAIN_TYPE=$1
PROMPT=$2
FORMAT=${3:-detailed}

# Set models based on chain type
case "$CHAIN_TYPE" in
    "life_optimization")
        MODELS=(
            "universal_context_provider:latest"
            "health_wellness_optimizer:latest"
            "productivity_optimizer:latest"
            "decision_simplifier_v2:latest"
        )
        ;;

    "business_acceleration")
        MODELS=(
            "universal_context_provider:latest"
            "matthew-career-coach:latest"
            "cot-career-strategist:latest"
            "decision_simplifier_v2:latest"
        )
        ;;

    "creative_breakthrough")
        MODELS=(
            "universal_context_provider:latest"
            "content_strategist_pro:latest"
            "cross_model_synthesizer:latest"
            "decision_enhancer:latest"
        )
        ;;

    "relationship_harmony")
        MODELS=(
            "universal_context_provider:latest"
            "decision_enhancer:latest"
            "cross_model_synthesizer:latest"
            "decision_simplifier_v2:latest"
        )
        ;;

    "technical_mastery")
        MODELS=(
            "universal_context_provider:latest"
            "cot-software-architect:latest"
            "qwen2.5-coder:7b"
            "decision_simplifier_v2:latest"
        )
        ;;

    "strategic_synthesis")
        MODELS=(
            "universal_context_provider:latest"
            "cross_model_synthesizer:latest"
            "gemma2:9b"
            "decision_simplifier_v2:latest"
        )
        ;;

    "deep_analysis")
        MODELS=(
            "universal_context_provider:latest"
            "gemma2:9b"
            "cross_model_synthesizer:latest"
            "decision_simplifier_v2:latest"
        )
        ;;

    "global_insight")
        MODELS=(
            "universal_context_provider:latest"
            "qwen2.5:7b"
            "cross_model_synthesizer:latest"
            "decision_simplifier_v2:latest"
        )
        ;;

    "rapid_decision")
        MODELS=(
            "quick-advisor-phi:latest"
            "universal_context_provider:latest"
            "decision_simplifier_v2:latest"
        )
        ;;

    *)
        echo "Invalid chain type: $CHAIN_TYPE"
        exit 1
        ;;
esac

# Create output directory
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_DIR="outputs/universal_${CHAIN_TYPE}_${TIMESTAMP}"
mkdir -p "$OUTPUT_DIR"

echo -e "${BLUE}Running Optimized ${CHAIN_TYPE} Chain${RESET}"
echo -e "${GREEN}Models: ${MODELS[*]}${RESET}"
echo -e "${YELLOW}Format: $FORMAT${RESET}"
echo ""

# Start metrics
SESSION_ID=$(metrics_session_id)
metrics_start "$SESSION_ID" "$PROMPT" "v3:${CHAIN_TYPE}"

# Initialize context
CONTEXT=""
FULL_OUTPUT=""

# Run through model chain
for i in "${!MODELS[@]}"; do
    MODEL="${MODELS[$i]}"
    echo -e "${BLUE}Running $MODEL ($(($i + 1))/${#MODELS[@]})...${RESET}"

    # Prepare input
    if [ $i -eq 0 ]; then
        INPUT="$PROMPT"
    else
        INPUT="Original request: $PROMPT

Previous analysis:
$CONTEXT

Please add your perspective and insights."
    fi

    # Run model and capture output
    MODEL_START=$(date +%s)
    OUTPUT=$(echo "$INPUT" | ollama run "$MODEL" 2>/dev/null)
    MODEL_END=$(date +%s)
    MODEL_ELAPSED=$(( MODEL_END - MODEL_START ))

    # Log model metrics
    if [ -n "$OUTPUT" ]; then
        metrics_log_model "$MODEL" "${#OUTPUT}" "$MODEL_ELAPSED" "1"
    else
        metrics_log_model "$MODEL" "0" "$MODEL_ELAPSED" "0"
    fi

    # Save individual output
    echo "$OUTPUT" > "$OUTPUT_DIR/response_$(($i + 1))_${MODEL//:/_}.md"

    # Update context
    CONTEXT="$CONTEXT

=== $MODEL ===
$OUTPUT"

    FULL_OUTPUT="$FULL_OUTPUT

## Model $(($i + 1)): $MODEL

$OUTPUT"
done

# Generate final output based on format
case "$FORMAT" in
    "quick")
        echo "$FULL_OUTPUT" | grep -E "^[-*]|^[0-9]\." | head -20 > "$OUTPUT_DIR/summary.md"
        cat "$OUTPUT_DIR/summary.md"
        ;;

    "summary")
        echo "$FULL_OUTPUT" | head -100 > "$OUTPUT_DIR/summary.md"
        cat "$OUTPUT_DIR/summary.md"
        ;;

    "detailed")
        echo "$FULL_OUTPUT" > "$OUTPUT_DIR/full_analysis.md"
        cat "$OUTPUT_DIR/full_analysis.md"
        ;;

    "export")
        echo "$FULL_OUTPUT" > "$OUTPUT_DIR/full_analysis.md"
        echo -e "${GREEN}Analysis exported to: $OUTPUT_DIR/full_analysis.md${RESET}"
        ;;
esac

# Save metadata (include session_id now)
cat > "$OUTPUT_DIR/metadata.json" << EOJSON
{
    "session_id": "$SESSION_ID",
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "chain_type": "$CHAIN_TYPE",
    "format": "$FORMAT",
    "models": $(echo "${MODELS[@]}" | jq -R -s -c 'split(" ")'),
    "prompt": $(echo "$PROMPT" | jq -R -s -c .)
}
EOJSON

# Finish metrics
if [ "$_METRICS_ERROR_COUNT" -eq 0 ]; then
    metrics_finish 1
else
    metrics_finish 0
fi

echo -e "\n${GREEN}Chain complete! Results in: $OUTPUT_DIR [Session: ${SESSION_ID}]${RESET}"
