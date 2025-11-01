"""
Mirador: Local AI Orchestration Framework

A privacy-first multi-agent system for chaining Ollama models.
"""

__version__ = "1.0.0"
__author__ = "Matthew Scott"
__email__ = "matthewdscott7@gmail.com"

from .orchestrator import Orchestrator, AgentChain
from .cli import main

__all__ = ["Orchestrator", "AgentChain", "main"]
