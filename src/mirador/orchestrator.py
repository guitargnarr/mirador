"""
Mirador Orchestrator - Core multi-agent chaining logic
"""

import requests
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class AgentChain:
    """Represents a chain of AI agents"""

    def __init__(self, description: str, models: List[str]):
        self.description = description
        self.models = models
        self.outputs = []
        self.start_time = None
        self.end_time = None

    def __repr__(self):
        return f"AgentChain('{self.description}', {len(self.models)} models)"


class Orchestrator:
    """Main orchestration engine for chaining Ollama models"""

    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.ollama_url = ollama_url
        self.output_dir = Path.home() / "mirador_outputs"
        self.output_dir.mkdir(exist_ok=True)

    def query_single(
        self,
        model: str,
        prompt: str,
        temperature: float = 0.7,
        timeout: int = 60
    ) -> str:
        """
        Query a single Ollama model

        Args:
            model: Model name (e.g., 'llama3.2', 'qwen2.5-coder')
            prompt: The prompt to send
            temperature: Sampling temperature (0.0-1.0)
            timeout: Request timeout in seconds

        Returns:
            Model response as string
        """
        logger.info(f"Querying {model} (temp={temperature})")

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_gpu": 1,
                "num_thread": 8
            }
        }

        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=timeout
            )
            response.raise_for_status()

            data = response.json()
            return data.get("response", "")

        except requests.exceptions.Timeout:
            raise TimeoutError(f"Request to {model} timed out after {timeout}s")
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Ollama API error: {e}")

    def run_chain(
        self,
        description: str,
        models: List[str],
        initial_prompt: Optional[str] = None
    ) -> Dict:
        """
        Execute a chain of models sequentially with context accumulation

        Args:
            description: Description of the task
            models: List of model names to execute in order
            initial_prompt: Optional initial prompt (uses description if not provided)

        Returns:
            Dictionary with chain results and metadata
        """
        chain = AgentChain(description, models)
        chain.start_time = datetime.now()

        logger.info(f"Starting chain: {description}")
        logger.info(f"Models: {' → '.join(models)}")

        # Create output directory for this chain
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        chain_dir = self.output_dir / f"chain_{timestamp}"
        chain_dir.mkdir(exist_ok=True)

        # Initial context
        context = initial_prompt or description
        accumulated_outputs = []

        # Execute each model in sequence
        for i, model in enumerate(models, 1):
            logger.info(f"Executing model {i}/{len(models)}: {model}")

            # Build prompt for this model
            if i == 1:
                full_prompt = context
            else:
                # Include previous outputs as context
                full_prompt = f"{context}\n\nPrevious analysis:\n{accumulated_outputs[-1]}"

            # Query the model
            try:
                output = self.query_single(model, full_prompt)
                accumulated_outputs.append(output)

                # Save individual output
                output_file = chain_dir / f"{i:02d}_{model}.md"
                output_file.write_text(output)

                logger.info(f"✓ {model} completed ({len(output)} chars)")

            except Exception as e:
                logger.error(f"✗ {model} failed: {e}")
                accumulated_outputs.append(f"[ERROR: {model} failed - {e}]")

        chain.end_time = datetime.now()
        chain.outputs = accumulated_outputs

        # Save chain summary
        summary = {
            "description": description,
            "models": models,
            "start_time": chain.start_time.isoformat(),
            "end_time": chain.end_time.isoformat(),
            "duration_seconds": (chain.end_time - chain.start_time).total_seconds(),
            "output_count": len(accumulated_outputs),
            "output_dir": str(chain_dir)
        }

        summary_file = chain_dir / "chain_summary.json"
        summary_file.write_text(json.dumps(summary, indent=2))

        # Save final combined output
        final_output = f"# Chain: {description}\n\n"
        for i, (model, output) in enumerate(zip(models, accumulated_outputs), 1):
            final_output += f"## Agent {i}: {model}\n\n{output}\n\n---\n\n"

        final_file = chain_dir / "final_output.md"
        final_file.write_text(final_output)

        return {
            "chain": chain,
            "outputs": accumulated_outputs,
            "summary": summary,
            "output_dir": chain_dir,
            "final_output": final_output
        }

    def list_models(self) -> List[Dict]:
        """Get list of available Ollama models"""

        try:
            response = requests.get(f"{self.ollama_url}/api/tags")
            response.raise_for_status()
            data = response.json()
            return data.get("models", [])
        except Exception as e:
            logger.error(f"Failed to list models: {e}")
            return []
