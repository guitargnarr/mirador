#!/bin/bash
# Mirador Metrics Logger - Automatic instrumentation for chain runners
# Sources into mirador-smart-v2 and mirador_universal_runner_v3_optimized.sh
# Writes to ~/.mirador/metrics.db (existing schema)

METRICS_DB="${HOME}/.mirador/metrics.db"

# Generate session ID
metrics_session_id() {
    echo "$(date +%Y%m%d-%H%M%S)-$$"
}

# Initialize a chain execution
# Usage: metrics_start SESSION_ID "prompt text" "intent_or_chain_type"
metrics_start() {
    local session_id="$1"
    local prompt="$2"
    local task_type="$3"
    local prompt_hash
    prompt_hash=$(echo -n "$prompt" | md5 -q 2>/dev/null || echo -n "$prompt" | md5sum | cut -d' ' -f1)

    _METRICS_SESSION_ID="$session_id"
    _METRICS_START_TIME=$(date +%s)
    _METRICS_START_ISO=$(date -u +%Y-%m-%dT%H:%M:%S.000000)
    _METRICS_PROMPT="$prompt"
    _METRICS_PROMPT_HASH="$prompt_hash"
    _METRICS_TASK_TYPE="$task_type"
    _METRICS_MODELS_USED=""
    _METRICS_MODEL_COUNT=0
    _METRICS_ERROR_COUNT=0
    _METRICS_TOTAL_OUTPUT_CHARS=0
}

# Log a single model execution within the chain
# Usage: metrics_log_model "model_name" output_length_chars elapsed_seconds success
metrics_log_model() {
    local model_name="$1"
    local output_len="$2"
    local elapsed="$3"
    local success="$4"

    if [ -z "$_METRICS_MODELS_USED" ]; then
        _METRICS_MODELS_USED="$model_name"
    else
        _METRICS_MODELS_USED="${_METRICS_MODELS_USED},$model_name"
    fi

    _METRICS_MODEL_COUNT=$((_METRICS_MODEL_COUNT + 1))
    _METRICS_TOTAL_OUTPUT_CHARS=$((_METRICS_TOTAL_OUTPUT_CHARS + output_len))

    if [ "$success" != "1" ]; then
        _METRICS_ERROR_COUNT=$((_METRICS_ERROR_COUNT + 1))
    fi
}

# Finalize and write to metrics.db
# Usage: metrics_finish [success]
metrics_finish() {
    local success="${1:-1}"
    local end_time
    end_time=$(date +%s)
    local end_iso
    end_iso=$(date -u +%Y-%m-%dT%H:%M:%S.000000)
    local duration=$(( end_time - _METRICS_START_TIME ))

    # Estimate tokens (rough: 1 token ~ 4 chars for output, input is prompt length)
    local tokens_output=$(( _METRICS_TOTAL_OUTPUT_CHARS / 4 ))
    local tokens_input=$(( ${#_METRICS_PROMPT} / 4 ))

    # Escape single quotes in prompt for SQL
    local safe_prompt
    safe_prompt=$(echo "$_METRICS_PROMPT" | sed "s/'/''/g")

    sqlite3 "$METRICS_DB" "INSERT OR IGNORE INTO executions (
        session_id, start_time, end_time, duration_seconds,
        prompt, prompt_hash, models_used,
        tokens_input, tokens_output, error_count, success, task_type
    ) VALUES (
        '${_METRICS_SESSION_ID}',
        '${_METRICS_START_ISO}',
        '${end_iso}',
        ${duration},
        '${safe_prompt}',
        '${_METRICS_PROMPT_HASH}',
        '${_METRICS_MODELS_USED}',
        ${tokens_input},
        ${tokens_output},
        ${_METRICS_ERROR_COUNT},
        ${success},
        '${_METRICS_TASK_TYPE}'
    );" 2>/dev/null
}
