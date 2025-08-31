#!/usr/bin/env python3
"""
Configuration file for PyMOL Agent
Copy this to config.py and add your API key
"""

# OpenAI Configuration
OPENAI_API_KEY = "your-openai-api-key-here"
OPENAI_MODEL = "gpt-4o"

# PyMOL Configuration
PYMOL_EXECUTABLE = "pymol"  # Path to PyMOL executable if not in PATH

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FILE = "pymol_agent.log"

# Default Settings
DEFAULT_RENDERING_WIDTH = 1200
DEFAULT_RENDERING_HEIGHT = 900
DEFAULT_RAY_SHADOWS = False
