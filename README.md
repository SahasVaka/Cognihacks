# PyMOL Specialist Agent

A sophisticated AI-powered agent that specializes in generating PyMOL code for molecular visualization and modeling. Built with OpenAI GPT-4 integration for intelligent molecular structure analysis and PyMOL scripting.

## 🧬 Features

- **Intelligent PyMOL Code Generation**: Natural language to PyMOL commands
- **Molecular Structure Analysis**: AI-powered structural insights and recommendations
- **Complete Visualization Scripts**: Generate publication-ready PyMOL scripts
- **Interactive Mode**: Real-time conversation with the PyMOL expert
- **Structure Loading & Management**: Automatic PDB fetching and file loading
- **Command Execution**: Direct PyMOL command execution (when PyMOL is available)
- **Educational Support**: Detailed explanations and best practices

## 🚀 Quick Start

### Installation

```bash
# Install required packages
pip install -r requirements.txt

# For full PyMOL functionality, install PyMOL
# Option 1: Conda (recommended)
conda install -c conda-forge pymol-open-source

# Option 2: PyMOL official (requires license for full features)
# Download from https://pymol.org/
```

### Basic Usage

```python
from pymol_agent import PyMOLAgent

# Initialize with your OpenAI API key
agent = PyMOLAgent(api_key="your-openai-api-key")

# Generate PyMOL code from natural language
result = agent.generate_pymol_code(
    "Load protein 1BNA and show it as cartoon colored by secondary structure"
)

print(result["explanation"])
for cmd in result["pymol_commands"]:
    print(cmd)

# Execute commands (if PyMOL is available)
if agent.pymol_available:
    agent.execute_pymol_commands(result["pymol_commands"])
```

### Command Line Usage

```bash
# Interactive mode
python pymol_agent.py --api-key YOUR_KEY --interactive

# Process single request
python pymol_agent.py --api-key YOUR_KEY --request "Show protein as surface"

# Load structure and analyze
python pymol_agent.py --api-key YOUR_KEY --load-pdb 1BNA --request "Analyze this structure"
```

## 📊 Demo

Run the comprehensive demo to see all features:

```bash
python demo_pymol_agent.py
```

The demo showcases:
- Basic protein visualization
- Complex molecular scenes
- Structural analysis workflows
- Complete script generation
- Interactive help system
- Structure loading and analysis

## 🎯 Use Cases

### 1. Protein Visualization
```python
result = agent.generate_pymol_code("""
Create a publication-quality view of lysozyme:
1. Load PDB 1LYZ
2. Show as cartoon with rainbow coloring
3. Highlight active site residues as sticks
4. Add transparent surface
5. Set up professional lighting
""")
```

### 2. Structural Comparison
```python
result = agent.generate_pymol_code("""
Compare two protein conformations:
1. Load structures 1A3N and 1A3O
2. Align them structurally
3. Show differences in red
4. Calculate and display RMSD
""")
```

### 3. Molecular Dynamics Analysis
```python
result = agent.generate_pymol_code("""
Analyze MD trajectory:
1. Load trajectory frames
2. Show conformational changes
3. Highlight flexible regions
4. Create smooth transition movie
""")
```

### 4. Drug-Target Visualization
```python
result = agent.generate_pymol_code("""
Visualize drug binding:
1. Load protein-ligand complex
2. Show binding pocket as surface
3. Display ligand interactions
4. Highlight key residues
""")
```

## 🔧 Advanced Features

### Structure Analysis
```python
# Load and analyze structure
agent.load_structure(pdb_id="2HHB", name="hemoglobin")
analysis = agent.analyze_structure("hemoglobin")
print(analysis["explanation"])
```

### Complete Script Generation
```python
# Generate complete visualization script
script = agent.create_visualization_script(
    "Create rotating movie of DNA double helix",
    output_file="dna_movie.py"
)
```

### Interactive Help
```python
# Get help on specific topics
help_text = agent.get_help("coloring")
print(help_text)
```

## 📁 Project Structure

```
├── pymol_agent.py          # Main agent class
├── demo_pymol_agent.py     # Comprehensive demo
├── requirements.txt        # Python dependencies
├── README.md              # This file
└── pymol_agent.log        # Agent activity log
```

## 🛠️ API Reference

### PyMOLAgent Class

#### `__init__(api_key, model="gpt-4")`
Initialize the agent with OpenAI API credentials.

#### `generate_pymol_code(request, context=None)`
Generate PyMOL commands from natural language description.

#### `execute_pymol_commands(commands)`
Execute PyMOL commands (requires PyMOL installation).

#### `load_structure(file_path=None, pdb_id=None, name=None)`
Load molecular structure from file or PDB database.

#### `analyze_structure(structure_name)`
AI-powered analysis of loaded molecular structure.

#### `create_visualization_script(request, output_file=None)`
Generate complete PyMOL visualization script.

#### `get_help(topic=None)`
Get help information about PyMOL commands or agent usage.

## 🎨 Example Outputs

The agent generates professional PyMOL commands like:

```python
# Load and prepare structure
cmd.fetch("1BNA", "dna_protein")
cmd.remove("solvent")

# Visualization setup
cmd.show("cartoon", "dna_protein and polymer.protein")
cmd.color("cyan", "dna_protein and polymer.protein")
cmd.show("sticks", "dna_protein and polymer.nucleic")
cmd.util.cnc("dna_protein and polymer.nucleic")

# Camera and rendering
cmd.orient()
cmd.zoom("all", 1.5)
cmd.set("ray_shadows", "off")
cmd.ray(1200, 900)
```

## 🔒 Security Notes

- API keys are handled securely and not logged
- Commands are validated before execution
- PyMOL execution is sandboxed when possible
- All operations are logged for audit trails

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenAI for GPT-4 API
- PyMOL development team
- Molecular visualization community
- Structural biology researchers worldwide

## 📞 Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Check the demo script for usage examples
- Review the comprehensive docstrings in the code

---

**Built with ❤️ for the molecular visualization community**
