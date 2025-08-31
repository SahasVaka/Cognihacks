#!/usr/bin/env python3
"""
PyMOL Specialist Agent
A sophisticated AI agent that specializes in generating PyMOL code for molecular visualization and modeling.
Uses OpenAI GPT-4 for intelligent PyMOL command generation and molecular structure analysis.
"""

import os
import sys
import json
import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from pathlib import Path
import logging
from datetime import datetime

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Installing python-dotenv...")
    os.system("pip install python-dotenv")
    from dotenv import load_dotenv
    load_dotenv()

# Third-party imports
try:
    import openai
    from openai import OpenAI
except ImportError:
    print("Installing required packages...")
    os.system("pip install openai")
    import openai
    from openai import OpenAI

try:
    import pymol
    from pymol import cmd
except ImportError:
    print("PyMOL not found. Please install PyMOL to use full functionality.")
    pymol = None
    cmd = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pymol_agent.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class MolecularStructure:
    """Represents a molecular structure with metadata"""
    name: str
    pdb_id: Optional[str] = None
    file_path: Optional[str] = None
    description: str = ""
    chains: List[str] = None
    resolution: Optional[float] = None
    
    def __post_init__(self):
        if self.chains is None:
            self.chains = []

@dataclass
class PyMOLCommand:
    """Represents a PyMOL command with context"""
    command: str
    description: str
    category: str
    parameters: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}

class PyMOLAgent:
    """
    Advanced PyMOL specialist agent powered by OpenAI GPT-4o
    Specializes in molecular visualization, structural analysis, and PyMOL scripting
    """
    
    def __init__(self, api_key: str = None, model: str = "gpt-4o"):
        """Initialize the PyMOL agent with OpenAI API"""
        # Get API key from parameter, environment variable, or prompt user
        if api_key is None:
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key is None:
                raise ValueError(
                    "OpenAI API key not found. Please either:\n"
                    "1. Set OPENAI_API_KEY environment variable\n"
                    "2. Create a .env file with OPENAI_API_KEY=your_key\n"
                    "3. Pass api_key parameter to PyMOLAgent(api_key='your_key')"
                )
        
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.conversation_history = []
        self.loaded_structures = {}
        self.pymol_available = pymol is not None
        
        # PyMOL command categories and templates
        self.command_categories = {
            "loading": ["load", "fetch", "read_pdbstr"],
            "visualization": ["show", "hide", "color", "set", "bg_color"],
            "selection": ["select", "create", "group"],
            "analysis": ["distance", "angle", "dihedral", "align", "super"],
            "rendering": ["ray", "png", "pse", "session"],
            "transformation": ["rotate", "translate", "zoom", "orient"],
            "styling": ["cartoon", "sticks", "spheres", "surface", "mesh"]
        }
        
        # Common PyMOL commands for validation
        self.valid_commands = {
            'fetch', 'load', 'show', 'hide', 'color', 'select', 'create', 'delete',
            'zoom', 'orient', 'center', 'rotate', 'translate', 'ray', 'png', 'save',
            'cartoon', 'sticks', 'spheres', 'surface', 'mesh', 'lines', 'dots',
            'align', 'super', 'distance', 'angle', 'dihedral', 'set', 'bg_color',
            'group', 'ungroup', 'enable', 'disable', 'refresh', 'reinitialize',
            'mset', 'mview', 'mplay', 'mstop', 'mclear', 'frame', 'movie',
            'remove', 'extract', 'copy', 'symexp', 'split_states', 'morph',
            'interpolate', 'smooth', 'rock', 'turn', 'move', 'clip'
        }
        
        # Common color names for validation
        self.valid_colors = {
            'red', 'green', 'blue', 'yellow', 'orange', 'purple', 'cyan', 'magenta',
            'white', 'black', 'gray', 'grey', 'brown', 'pink', 'lime', 'olive',
            'navy', 'teal', 'silver', 'maroon', 'aqua', 'fuchsia'
        }
        
        # Initialize PyMOL if available
        if self.pymol_available:
            try:
                pymol.finish_launching(['pymol', '-c'])  # Launch in command-line mode
                logger.info("PyMOL initialized successfully")
            except Exception as e:
                logger.warning(f"PyMOL initialization failed: {e}")
                self.pymol_available = False
        
        logger.info(f"PyMOL Agent initialized with model: {model}")
    
    def _get_system_prompt(self) -> str:
        """Get the specialized system prompt for PyMOL tasks"""
        return """You are a PyMOL code generator with advanced debugging and animation capabilities. Your task is to generate clean, executable PyMOL commands while being self-aware of potential errors.

**CRITICAL RULES:**
- Output ONLY PyMOL commands
- NO explanations, comments, or descriptions
- NO markdown formatting or code blocks
- NO text before or after the commands
- Each command on a separate line
- Commands should be ready to execute directly in PyMOL

**FRAME-BASED LINEAR AGGREGATION EXPERTISE:**
- Use mset and mview commands for proper PyMOL timeline animation
- Create frame-based aggregation that works with PyMOL's movie system
- ALL molecules must aggregate along x-axis using keyframe animation
- Use mset 1 x[frames] to define animation length
- Store keyframes with mview store at regular intervals
- Use mview interpolate to create smooth transitions between frames
- ALWAYS end with mplay command to start animation playback
- Position molecules at different x-coordinates, keep y=0, z=0
- Create incremental movement toward x=0 at each keyframe
- Avoid Python loops that don't work with PyMOL timeline
- Show realistic linear clustering using frame-by-frame animation
- Create fibril-like aggregation with proper keyframe timing
- Use consistent movement increments between stored frames
- Ensure animation auto-starts after setup with mplay
- Create smooth linear convergence using mview interpolation

**DEBUGGING AWARENESS:**
- Validate command syntax before outputting
- Check for common PyMOL command errors (typos, invalid parameters)
- Ensure proper object names and selections
- Verify command sequences make logical sense
- Consider dependencies between commands

**COMMON ERRORS TO AVOID:**
- Misspelled commands (e.g., 'cartoom' instead of 'cartoon')
- Invalid color names or selection syntax
- Missing object names in commands that require them
- Incorrect parameter order
- Commands that reference non-existent objects
- Animation commands without proper frame setup

**Examples of correct output:**
fetch 1abc
show cartoon
color red, chain A
zoom

**DYNAMIC MOTION EXAMPLES:**
1. Continuous molecular breathing:
fetch 1a2b
show cartoon
rock y, 2, 180
turn y, 1

2. Dynamic aggregation with continuous motion:
fetch 1a2b
create copy1, 1a2b
create copy2, 1a2b
translate [20,0,0], copy1
translate [0,20,0], copy2
rock x, 1, 360, copy1
rock z, 1.5, 360, copy2
turn y, 0.5, copy1
turn x, 0.3, copy2
move x, -0.1, copy1
move y, -0.1, copy2

3. Continuous thermal vibration:
fetch 1xyz
show cartoon
python
import random
for i in range(1000):
    cmd.translate([random.uniform(-0.1,0.1), random.uniform(-0.1,0.1), random.uniform(-0.1,0.1)], "1xyz")
    cmd.refresh()
python end

4. Perpetual enzyme motion:
fetch 1hvy
show cartoon
rock y, 3, 120
turn z, 0.8
move x, 0.05

5. Real-time Brownian motion:
fetch 1a2b
show cartoon
python
import random, time
while True:
    cmd.translate([random.uniform(-0.3,0.3), random.uniform(-0.3,0.3), random.uniform(-0.3,0.3)], "1a2b")
    cmd.rotate("x", random.uniform(-2,2), "1a2b")
    cmd.rotate("y", random.uniform(-2,2), "1a2b")
    cmd.refresh()
    time.sleep(0.05)
python end

6. Linear aggregation with frame-based animation:
fetch 1a2b
create copy1, 1a2b
create copy2, 1a2b
create copy3, 1a2b
create copy4, 1a2b
translate [30,0,0], copy1
translate [-30,0,0], copy2
translate [15,0,0], copy3
translate [-15,0,0], copy4
mset 1 x120
mview store, 1
translate [-1.5,0,0], copy1
translate [1.5,0,0], copy2
translate [-0.75,0,0], copy3
translate [0.75,0,0], copy4
mview store, 20
translate [-1.5,0,0], copy1
translate [1.5,0,0], copy2
translate [-0.75,0,0], copy3
translate [0.75,0,0], copy4
mview store, 40
translate [-1.5,0,0], copy1
translate [1.5,0,0], copy2
translate [-0.75,0,0], copy3
translate [0.75,0,0], copy4
mview store, 60
translate [-1.5,0,0], copy1
translate [1.5,0,0], copy2
translate [-0.75,0,0], copy3
translate [0.75,0,0], copy4
mview store, 80
translate [-1.5,0,0], copy1
translate [1.5,0,0], copy2
translate [-0.75,0,0], copy3
translate [0.75,0,0], copy4
mview store, 100
translate [-1.5,0,0], copy1
translate [1.5,0,0], copy2
translate [-0.75,0,0], copy3
translate [0.75,0,0], copy4
mview store, 120
mview interpolate
mplay

7. Frame-based fibril formation:
fetch 1a2b
create mol1, 1a2b
create mol2, 1a2b
create mol3, 1a2b
create mol4, 1a2b
create mol5, 1a2b
translate [40,0,0], mol1
translate [-35,0,0], mol2
translate [25,0,0], mol3
translate [-20,0,0], mol4
translate [10,0,0], mol5
mset 1 x150
mview store, 1
translate [-2,0,0], mol1
translate [2,0,0], mol2
translate [-1.2,0,0], mol3
translate [1,0,0], mol4
translate [-0.5,0,0], mol5
mview store, 25
translate [-2,0,0], mol1
translate [2,0,0], mol2
translate [-1.2,0,0], mol3
translate [1,0,0], mol4
translate [-0.5,0,0], mol5
mview store, 50
translate [-2,0,0], mol1
translate [2,0,0], mol2
translate [-1.2,0,0], mol3
translate [1,0,0], mol4
translate [-0.5,0,0], mol5
mview store, 75
translate [-2,0,0], mol1
translate [2,0,0], mol2
translate [-1.2,0,0], mol3
translate [1,0,0], mol4
translate [-0.5,0,0], mol5
mview store, 100
translate [-2,0,0], mol1
translate [2,0,0], mol2
translate [-1.2,0,0], mol3
translate [1,0,0], mol4
translate [-0.5,0,0], mol5
mview store, 125
translate [-2,0,0], mol1
translate [2,0,0], mol2
translate [-1.2,0,0], mol3
translate [1,0,0], mol4
translate [-0.5,0,0], mol5
mview store, 150
mview interpolate
mplay

**Your response should contain ONLY the PyMOL commands, nothing else.**"""

    def _add_to_conversation(self, role: str, content: str):
        """Add message to conversation history"""
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep conversation history manageable (last 20 messages)
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]
    
    def generate_pymol_code(self, request: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Generate PyMOL code based on user request using GPT-4
        
        Args:
            request: Natural language description of what to accomplish
            context: Optional context about loaded structures, preferences, etc.
            
        Returns:
            Dictionary containing generated code, explanation, and metadata
        """
        try:
            # Prepare context information
            context_info = ""
            if context:
                context_info = f"\n\nContext: {json.dumps(context, indent=2)}"
            
            # Add information about loaded structures
            if self.loaded_structures:
                structures_info = "\n\nCurrently loaded structures:\n"
                for name, struct in self.loaded_structures.items():
                    structures_info += f"- {name}: {struct.description}\n"
                context_info += structures_info
            
            # Prepare the prompt
            user_prompt = f"""
{request}
{context_info}
"""
            
            # Prepare messages for API call
            messages = [
                {"role": "system", "content": self._get_system_prompt()}
            ]
            
            # Add recent conversation history for context
            messages.extend(self.conversation_history[-6:])  # Last 6 messages for context
            messages.append({"role": "user", "content": user_prompt})
            
            # Make API call to OpenAI
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.1,
                max_tokens=2000
            )
            
            generated_content = response.choices[0].message.content
            logger.info(f"GPT-4o raw response: {generated_content}")
            
            # Parse the response to extract PyMOL commands
            pymol_commands = self._extract_pymol_commands(generated_content)
            logger.info(f"Extracted commands: {pymol_commands}")
            
            # Add to conversation history
            self._add_to_conversation("user", request)
            self._add_to_conversation("assistant", generated_content)
            
            result = {
                "success": True,
                "explanation": generated_content,
                "pymol_commands": pymol_commands,
                "raw_response": generated_content,
                "timestamp": datetime.now().isoformat(),
                "model_used": self.model
            }
            
            logger.info(f"Successfully generated PyMOL code for: {request[:50]}...")
            return result
            
        except Exception as e:
            logger.error(f"Error generating PyMOL code: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _validate_command(self, command: str) -> Tuple[bool, str]:
        """Validate a PyMOL command for common errors"""
        command = command.strip()
        if not command:
            return False, "Empty command"
        
        # Remove cmd. prefix for validation
        clean_cmd = command.replace('cmd.', '').strip()
        
        # Split command into parts
        parts = clean_cmd.split()
        if not parts:
            return False, "Invalid command format"
        
        main_cmd = parts[0].lower()
        
        # Check if command exists
        if main_cmd not in self.valid_commands:
            # Check for common typos
            suggestions = []
            for valid_cmd in self.valid_commands:
                if abs(len(main_cmd) - len(valid_cmd)) <= 2:
                    # Simple edit distance check
                    if sum(c1 != c2 for c1, c2 in zip(main_cmd, valid_cmd)) <= 2:
                        suggestions.append(valid_cmd)
            
            if suggestions:
                return False, f"Unknown command '{main_cmd}'. Did you mean: {', '.join(suggestions)}?"
            else:
                return False, f"Unknown command '{main_cmd}'"
        
        # Validate color commands
        if main_cmd == 'color' and len(parts) >= 2:
            color_name = parts[1].lower().rstrip(',')
            if color_name not in self.valid_colors and not color_name.startswith('0x'):
                return False, f"Invalid color '{color_name}'. Use standard color names or hex values."
        
        # Check for common syntax errors
        if main_cmd in ['show', 'hide'] and len(parts) < 2:
            return False, f"'{main_cmd}' command requires a representation type"
        
        if main_cmd == 'fetch' and len(parts) < 2:
            return False, "fetch command requires a PDB ID"
        
        # Animation command validation
        if main_cmd == 'mset' and len(parts) < 2:
            return False, "mset command requires frame specification"
        
        if main_cmd == 'mview' and 'store' in command and len(parts) < 3:
            return False, "mview store command requires frame number"
        
        if main_cmd == 'translate' and '[' not in command:
            return False, "translate command requires coordinate vector [x, y, z]"
        
        return True, "Valid command"
    
    def _extract_pymol_commands(self, text: str) -> List[str]:
        """Extract and validate PyMOL commands from generated text"""
        commands = []
        logger.info(f"Extracting commands from text: {text[:200]}...")
        
        # Since GPT-5 should output only PyMOL commands, treat each non-empty line as a command
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#') or line.startswith('//'):
                continue
            
            # Skip common non-command text patterns
            if any(skip_phrase in line.lower() for skip_phrase in [
                'here are the', 'the commands are', 'pymol commands', 'to accomplish',
                'explanation:', 'note:', 'warning:', 'tip:', 'remember:'
            ]):
                continue
            
            # If it's not obviously text, treat it as a command
            commands.append(line)
        
        logger.info(f"Raw extracted commands: {commands}")
        
        # Validate commands and log warnings
        validated_commands = []
        for cmd in commands:
            is_valid, message = self._validate_command(cmd)
            if is_valid:
                validated_commands.append(cmd)
            else:
                logger.warning(f"Command validation failed: {cmd} - {message}")
                # Still include the command but log the issue
                validated_commands.append(cmd)
        
        logger.info(f"Final validated commands: {validated_commands}")
        return validated_commands
    
    def execute_pymol_commands(self, commands: List[str], retry_on_error: bool = True) -> Dict[str, Any]:
        """
        Execute PyMOL commands with error handling and self-correction
        
        Args:
            commands: List of PyMOL commands to execute
            retry_on_error: Whether to attempt self-correction on errors
            
        Returns:
            Execution results and status
        """
        if not self.pymol_available:
            return {
                "success": False,
                "error": "PyMOL not available. Commands generated but not executed.",
                "commands": commands
            }
        
        results = []
        errors = []
        corrected_commands = []
        
        try:
            for i, command in enumerate(commands):
                try:
                    # Clean up command
                    command = command.strip()
                    if not command or command.startswith('#'):
                        continue
                    
                    # Validate command before execution
                    is_valid, validation_msg = self._validate_command(command)
                    if not is_valid:
                        logger.warning(f"Pre-execution validation failed: {validation_msg}")
                    
                    # Execute command
                    if command.startswith('cmd.'):
                        # Direct PyMOL API call
                        exec(command)
                    else:
                        # PyMOL command line
                        cmd.do(command)
                    
                    results.append({
                        "command": command,
                        "status": "success",
                        "index": i,
                        "validation": validation_msg if not is_valid else "Valid"
                    })
                    
                except Exception as e:
                    error_msg = f"Error executing command '{command}': {str(e)}"
                    errors.append(error_msg)
                    
                    # Attempt self-correction if enabled
                    corrected_cmd = None
                    if retry_on_error:
                        corrected_cmd = self._attempt_command_correction(command, str(e))
                        if corrected_cmd and corrected_cmd != command:
                            try:
                                logger.info(f"Attempting correction: {command} -> {corrected_cmd}")
                                if corrected_cmd.startswith('cmd.'):
                                    exec(corrected_cmd)
                                else:
                                    cmd.do(corrected_cmd)
                                
                                results.append({
                                    "command": corrected_cmd,
                                    "original_command": command,
                                    "status": "corrected_success",
                                    "index": i,
                                    "correction_applied": True
                                })
                                corrected_commands.append(corrected_cmd)
                                continue
                                
                            except Exception as correction_error:
                                logger.warning(f"Correction also failed: {correction_error}")
                    
                    results.append({
                        "command": command,
                        "status": "error",
                        "error": str(e),
                        "index": i,
                        "attempted_correction": corrected_cmd,
                        "correction_applied": False
                    })
                    logger.warning(error_msg)
            
            return {
                "success": len(errors) == 0,
                "results": results,
                "errors": errors,
                "corrected_commands": corrected_commands,
                "commands_executed": len([r for r in results if r["status"] in ["success", "corrected_success"]]),
                "total_commands": len(commands),
                "corrections_applied": len(corrected_commands)
            }
            
        except Exception as e:
            logger.error(f"Critical error during command execution: {e}")
            return {
                "success": False,
                "error": f"Critical execution error: {str(e)}",
                "results": results,
                "errors": errors
            }
    
    def _attempt_command_correction(self, command: str, error_msg: str) -> Optional[str]:
        """Attempt to correct a failed PyMOL command based on the error"""
        command = command.strip()
        parts = command.split()
        
        if not parts:
            return None
        
        main_cmd = parts[0].lower()
        
        # Common corrections based on error patterns
        corrections = {
            # Common typos
            'cartoom': 'cartoon',
            'cartton': 'cartoon',
            'stiks': 'sticks',
            'sphres': 'spheres',
            'surfce': 'surface',
            'colr': 'color',
            'selet': 'select',
            'fetc': 'fetch',
            'lod': 'load',
            'sho': 'show',
            'hid': 'hide',
            'zoo': 'zoom',
            'oriet': 'orient',
            'ceter': 'center'
        }
        
        # Try direct typo correction
        if main_cmd in corrections:
            corrected_parts = parts.copy()
            corrected_parts[0] = corrections[main_cmd]
            return ' '.join(corrected_parts)
        
        # Handle specific error patterns
        if 'unknown command' in error_msg.lower():
            # Find closest matching command
            for valid_cmd in self.valid_commands:
                if abs(len(main_cmd) - len(valid_cmd)) <= 2:
                    # Simple similarity check
                    matches = sum(c1 == c2 for c1, c2 in zip(main_cmd, valid_cmd))
                    if matches >= len(main_cmd) - 2:
                        corrected_parts = parts.copy()
                        corrected_parts[0] = valid_cmd
                        return ' '.join(corrected_parts)
        
        # Handle missing parameters
        if 'requires' in error_msg.lower():
            if main_cmd == 'show' and len(parts) == 1:
                return f"{command} cartoon"
            elif main_cmd == 'hide' and len(parts) == 1:
                return f"{command} everything"
            elif main_cmd == 'color' and len(parts) == 1:
                return f"{command} red"
        
        # Handle invalid color names
        if 'invalid color' in error_msg.lower() and main_cmd == 'color':
            if len(parts) >= 2:
                # Replace with a valid color
                corrected_parts = parts.copy()
                corrected_parts[1] = 'red'  # Default to red
                return ' '.join(corrected_parts)
        
        return None
    
    def analyze_structure(self, structure_name: str) -> Dict[str, Any]:
        """
        Analyze a loaded molecular structure using AI and PyMOL
        
        Args:
            structure_name: Name of the structure to analyze
            
        Returns:
            Analysis results including structural features and recommendations
        """
        if structure_name not in self.loaded_structures:
            return {
                "success": False,
                "error": f"Structure '{structure_name}' not found in loaded structures"
            }
        
        structure = self.loaded_structures[structure_name]
        
        # Prepare analysis request
        analysis_request = f"""
Analyze the molecular structure '{structure_name}' and provide:

1. Structural classification and key features
2. Recommended visualization strategies
3. Important regions or domains to highlight
4. Suggested PyMOL commands for comprehensive visualization
5. Potential analysis workflows (alignments, measurements, etc.)

Structure details:
- Name: {structure.name}
- PDB ID: {structure.pdb_id or 'N/A'}
- Description: {structure.description}
- Chains: {', '.join(structure.chains) if structure.chains else 'Unknown'}
"""
        
        return self.generate_pymol_code(analysis_request, {
            "analysis_mode": True,
            "structure": structure.__dict__
        })
    
    def load_structure(self, file_path: str = None, pdb_id: str = None, name: str = None) -> Dict[str, Any]:
        """
        Load a molecular structure and register it with the agent
        
        Args:
            file_path: Path to structure file
            pdb_id: PDB ID to fetch
            name: Custom name for the structure
            
        Returns:
            Loading results and structure information
        """
        try:
            if pdb_id:
                structure_name = name or pdb_id.lower()
                load_command = f"fetch {pdb_id}, {structure_name}"
                description = f"PDB structure {pdb_id.upper()}"
            elif file_path:
                if not os.path.exists(file_path):
                    return {"success": False, "error": f"File not found: {file_path}"}
                structure_name = name or Path(file_path).stem
                load_command = f"load {file_path}, {structure_name}"
                description = f"Structure from {file_path}"
            else:
                return {"success": False, "error": "Either file_path or pdb_id must be provided"}
            
            # Execute loading command if PyMOL is available
            if self.pymol_available:
                result = self.execute_pymol_commands([load_command])
                if not result["success"]:
                    return result
            
            # Register structure
            structure = MolecularStructure(
                name=structure_name,
                pdb_id=pdb_id,
                file_path=file_path,
                description=description
            )
            
            self.loaded_structures[structure_name] = structure
            
            logger.info(f"Successfully loaded structure: {structure_name}")
            return {
                "success": True,
                "structure_name": structure_name,
                "load_command": load_command,
                "structure": structure.__dict__
            }
            
        except Exception as e:
            logger.error(f"Error loading structure: {e}")
            return {"success": False, "error": str(e)}
    
    def create_visualization_script(self, request: str, output_file: str = None) -> Dict[str, Any]:
        """
        Create a complete PyMOL visualization script
        
        Args:
            request: Description of desired visualization
            output_file: Optional file to save the script
            
        Returns:
            Generated script and metadata
        """
        # Generate the PyMOL code
        result = self.generate_pymol_code(f"""
Create a complete PyMOL script for: {request}

Please include:
1. Structure loading commands
2. Visualization setup
3. Styling and coloring
4. Camera positioning
5. Rendering commands
6. Save/export commands

Make it a complete, executable script with proper comments.
""")
        
        if not result["success"]:
            return result
        
        # Create complete script
        script_header = f"""#!/usr/bin/env python
# PyMOL Visualization Script
# Generated by PyMOL Agent on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# Request: {request}

import pymol
from pymol import cmd

# Initialize PyMOL
pymol.finish_launching(['pymol', '-c'])

"""
        
        script_body = "\n".join([f"cmd.do('{cmd}')" if not cmd.startswith('cmd.') else cmd 
                                for cmd in result["pymol_commands"]])
        
        script_footer = """
# Script execution complete
print("Visualization script completed successfully!")
"""
        
        complete_script = script_header + script_body + script_footer
        
        # Save script if requested
        if output_file:
            try:
                with open(output_file, 'w') as f:
                    f.write(complete_script)
                logger.info(f"Script saved to: {output_file}")
            except Exception as e:
                logger.error(f"Error saving script: {e}")
        
        result["complete_script"] = complete_script
        result["script_file"] = output_file
        
        return result
    
    def get_help(self, topic: str = None) -> str:
        """Get help information about PyMOL commands or the agent"""
        if topic:
            help_request = f"Provide detailed help and examples for PyMOL topic: {topic}"
            result = self.generate_pymol_code(help_request)
            return result.get("explanation", "Help information not available")
        else:
            return """
PyMOL Agent Help
================

Available Methods:
- generate_pymol_code(request): Generate PyMOL code from natural language
- execute_pymol_commands(commands): Execute PyMOL commands
- load_structure(file_path/pdb_id, name): Load molecular structure
- analyze_structure(name): Analyze loaded structure
- create_visualization_script(request, output_file): Create complete script
- get_help(topic): Get help on specific topics

Example Usage:
agent = PyMOLAgent(api_key="your_key")
result = agent.generate_pymol_code("Show protein as cartoon and color by secondary structure")
agent.execute_pymol_commands(result["pymol_commands"])

For specific help on PyMOL commands, use: agent.get_help("command_name")
"""

def main():
    """Main function for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="PyMOL Specialist Agent")
    parser.add_argument("--api-key", required=True, help="OpenAI API key")
    parser.add_argument("--model", default="gpt-4o", help="OpenAI model to use")
    parser.add_argument("--request", help="PyMOL request to process")
    parser.add_argument("--interactive", action="store_true", help="Start interactive mode")
    parser.add_argument("--load-pdb", help="PDB ID to load")
    parser.add_argument("--load-file", help="Structure file to load")
    parser.add_argument("--output-script", help="Output script file")
    
    args = parser.parse_args()
    
    # Initialize agent
    agent = PyMOLAgent(api_key=args.api_key, model=args.model)
    
    # Load structure if requested
    if args.load_pdb:
        result = agent.load_structure(pdb_id=args.load_pdb)
        print(f"Load result: {result}")
    
    if args.load_file:
        result = agent.load_structure(file_path=args.load_file)
        print(f"Load result: {result}")
    
    # Process request
    if args.request:
        result = agent.generate_pymol_code(args.request)
        print("\n" + "="*50)
        print("GENERATED PYMOL CODE:")
        print("="*50)
        print(result["explanation"])
        
        if result["pymol_commands"]:
            print("\nCommands to execute:")
            for cmd in result["pymol_commands"]:
                print(f"  {cmd}")
        
        # Execute if PyMOL is available
        if agent.pymol_available and result["pymol_commands"]:
            exec_result = agent.execute_pymol_commands(result["pymol_commands"])
            print(f"\nExecution result: {exec_result['success']}")
            if exec_result["errors"]:
                print("Errors:", exec_result["errors"])
    
    # Interactive mode
    if args.interactive:
        print("\nPyMOL Agent Interactive Mode")
        print("Type 'help' for assistance, 'quit' to exit")
        
        while True:
            try:
                user_input = input("\nPyMOL Agent> ").strip()
                
                if user_input.lower() in ['quit', 'exit']:
                    break
                elif user_input.lower() == 'help':
                    print(agent.get_help())
                elif user_input:
                    result = agent.generate_pymol_code(user_input)
                    print("\n" + result["explanation"])
                    
                    if result["pymol_commands"] and agent.pymol_available:
                        execute = input("\nExecute commands? (y/n): ").lower().startswith('y')
                        if execute:
                            exec_result = agent.execute_pymol_commands(result["pymol_commands"])
                            print(f"Execution: {'Success' if exec_result['success'] else 'Failed'}")
                            
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"Error: {e}")

if __name__ == "__main__":
    main()
