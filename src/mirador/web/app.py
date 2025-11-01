"""
Mirador Web UI - Streamlit interface for AI orchestration
"""

import streamlit as st
import requests
from pathlib import Path
import sys

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mirador.orchestrator import Orchestrator

# Page config
st.set_page_config(
    page_title="Mirador AI Orchestration",
    page_icon="🏰",
    layout="wide"
)

# Initialize
if 'orchestrator' not in st.session_state:
    st.session_state.orchestrator = Orchestrator()

orchestrator = st.session_state.orchestrator

# Header
st.title("🏰 Mirador AI Orchestration")
st.markdown("**Privacy-first multi-agent AI framework** • Built on Ollama • 100% Local")

# Sidebar - Model Selection
st.sidebar.header("⚙️ Configuration")

# Get available models
try:
    models_list = orchestrator.list_models()
    model_names = [m['name'] for m in models_list]

    if not model_names:
        st.sidebar.error("No Ollama models found. Install models first:")
        st.sidebar.code("ollama pull llama3.2")
        st.stop()

except Exception as e:
    st.sidebar.error(f"Cannot connect to Ollama: {e}")
    st.sidebar.info("Make sure Ollama is running: `ollama serve`")
    st.stop()

# Main interface
tab1, tab2, tab3 = st.tabs(["🤖 Single Query", "⛓️ Agent Chain", "📊 Agent Library"])

# Tab 1: Single Query
with tab1:
    st.header("Query Single Model")

    col1, col2 = st.columns([3, 1])

    with col1:
        selected_model = st.selectbox(
            "Select Model",
            options=model_names,
            index=0 if model_names else None
        )

    with col2:
        temperature = st.slider("Temperature", 0.0, 1.0, 0.7, 0.1)

    prompt = st.text_area(
        "Enter your prompt",
        height=150,
        placeholder="Ask anything..."
    )

    if st.button("🚀 Query Model", type="primary"):
        if prompt:
            with st.spinner(f"Querying {selected_model}..."):
                try:
                    response = orchestrator.query_single(selected_model, prompt, temperature)
                    st.success("✓ Complete!")
                    st.markdown("### Response:")
                    st.markdown(response)
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("Please enter a prompt")

# Tab 2: Agent Chain
with tab2:
    st.header("Multi-Agent Chain")

    description = st.text_input("Chain Description", placeholder="e.g., Review and improve this code")

    st.markdown("**Select Models (in execution order):**")

    chain_models = st.multiselect(
        "Choose models for the chain",
        options=model_names,
        default=model_names[:2] if len(model_names) >= 2 else model_names[:1]
    )

    if len(chain_models) > 0:
        st.info(f"Chain: {' → '.join(chain_models)}")

    chain_prompt = st.text_area(
        "Initial Prompt",
        height=150,
        placeholder="The first model will receive this prompt. Subsequent models receive accumulated context."
    )

    if st.button("⛓️ Execute Chain", type="primary"):
        if description and chain_prompt and chain_models:
            progress_bar = st.progress(0)
            status = st.empty()

            results_container = st.container()

            try:
                total_models = len(chain_models)

                with st.spinner("Running chain..."):
                    # Execute chain
                    results = orchestrator.run_chain(description, chain_models, chain_prompt)

                    # Show results
                    st.success(f"✓ Chain complete! ({results['summary']['duration_seconds']:.1f}s)")

                    with results_container:
                        for i, (model, output) in enumerate(zip(chain_models, results['outputs']), 1):
                            with st.expander(f"Agent {i}: {model}", expanded=(i == total_models)):
                                st.markdown(output)

                        st.info(f"Full output saved to: {results['output_dir']}")

            except Exception as e:
                st.error(f"Chain failed: {e}")
        else:
            st.warning("Please fill in all fields and select at least one model")

# Tab 3: Agent Library
with tab3:
    st.header("Available AI Agents")

    # Show installed models
    st.subheader(f"Installed Models ({len(model_names)})")

    for model_data in models_list:
        with st.expander(f"📦 {model_data['name']}"):
            col1, col2 = st.columns(2)

            with col1:
                st.metric("Size", f"{model_data.get('size', 0) / 1e9:.2f} GB")

            with col2:
                modified = model_data.get('modified_at', '')[:10]
                st.metric("Modified", modified)

    # Agent templates info
    st.subheader("Pre-configured Agent Templates")

    agent_dir = Path(__file__).parent.parent.parent.parent / "models" / "domain"

    if agent_dir.exists():
        modelfiles = list(agent_dir.glob("*.modelfile"))
        st.info(f"Found {len(modelfiles)} agent templates in `models/domain/`")

        # Show sample agents
        samples = [
            ("code_reviewer_fix", "Code review and bug detection"),
            ("creative_entrepreneur", "Identify business applications"),
            ("decision_simplifier_v3", "Simplify complex decisions"),
            ("ux_designer", "UI/UX design recommendations"),
        ]

        for agent_name, description in samples:
            st.markdown(f"- **{agent_name}**: {description}")

    else:
        st.warning("No agent templates found")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <p>Mirador AI Orchestration Framework • Built by Matthew Scott</p>
        <p>100% Local • Privacy-First • Powered by Ollama</p>
    </div>
    """,
    unsafe_allow_html=True
)
