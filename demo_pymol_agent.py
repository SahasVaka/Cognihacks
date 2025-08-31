#!/usr/bin/env python3
"""
PyMOL Agent Demo Script
Demonstrates the capabilities of the PyMOL specialist agent
"""

from pymol_agent import PyMOLAgent
import os

def main():
    """Demo the PyMOL agent capabilities"""
    
    print("🧬 PyMOL Specialist Agent Demo")
    print("=" * 50)
    
    # Initialize the agent (API key loaded from .env file)
    print("Initializing PyMOL Agent with GPT-4o...")
    try:
        agent = PyMOLAgent(model="gpt-4o")  # API key loaded automatically from .env
        print("✅ Agent initialized successfully!\n")
    except ValueError as e:
        print(f"❌ Error: {e}")
        return
    
    # Demo 1: Basic protein visualization
    print("📊 Demo 1: Basic Protein Visualization")
    print("-" * 40)
    
    request1 = "Load protein 1BNA (DNA-binding protein) and show it as cartoon colored by secondary structure"
    result1 = agent.generate_pymol_code(request1)
    
    if result1["success"]:
        print("Generated PyMOL commands:")
        for cmd in result1["pymol_commands"]:
            print(f"  {cmd}")
        print(f"\nExplanation:\n{result1['explanation'][:200]}...\n")
    
    # Demo 2: Complex molecular scene
    print("🎨 Demo 2: Complex Molecular Scene")
    print("-" * 40)
    
    request2 = """Create a publication-quality visualization of a protein-DNA complex:
    1. Load PDB 1JJ2 (protein-DNA complex)
    2. Show protein as cartoon in blue
    3. Show DNA as sticks with CPK coloring
    4. Add transparent surface around the protein
    5. Set up lighting for high-quality rendering"""
    
    result2 = agent.generate_pymol_code(request2)
    
    if result2["success"]:
        print("Generated complex visualization script:")
        for i, cmd in enumerate(result2["pymol_commands"][:5]):  # Show first 5 commands
            print(f"  {i+1}. {cmd}")
        if len(result2["pymol_commands"]) > 5:
            print(f"  ... and {len(result2['pymol_commands']) - 5} more commands")
        print()
    
    # Demo 3: Structural analysis
    print("🔬 Demo 3: Structural Analysis")
    print("-" * 40)
    
    request3 = """Perform structural analysis on two similar proteins:
    1. Load proteins 1A3N and 1A3O
    2. Align them structurally
    3. Calculate RMSD
    4. Highlight regions with significant differences
    5. Create a comparison visualization"""
    
    result3 = agent.generate_pymol_code(request3)
    
    if result3["success"]:
        print("Generated analysis workflow:")
        for cmd in result3["pymol_commands"]:
            print(f"  {cmd}")
        print()
    
    # Demo 4: Create a complete visualization script
    print("📝 Demo 4: Complete Visualization Script")
    print("-" * 40)
    
    script_request = "Create a rotating movie of hemoglobin showing the heme groups as sticks"
    script_result = agent.create_visualization_script(
        script_request, 
        output_file="hemoglobin_movie.py"
    )
    
    if script_result["success"]:
        print("✅ Complete visualization script created!")
        print(f"Script saved to: {script_result.get('script_file', 'hemoglobin_movie.py')}")
        print("First few lines of the script:")
        script_lines = script_result["complete_script"].split('\n')[:10]
        for line in script_lines:
            print(f"  {line}")
        print("  ...")
        print()
    
    # Demo 5: Interactive help system
    print("❓ Demo 5: Help System")
    print("-" * 40)
    
    help_topic = "coloring"
    help_result = agent.get_help(help_topic)
    print(f"Help for '{help_topic}':")
    print(help_result[:300] + "..." if len(help_result) > 300 else help_result)
    print()
    
    # Demo 6: Structure loading and analysis
    print("🧪 Demo 6: Structure Loading & Analysis")
    print("-" * 40)
    
    # Load a structure
    load_result = agent.load_structure(pdb_id="2HHB", name="hemoglobin")
    if load_result["success"]:
        print(f"✅ Loaded structure: {load_result['structure_name']}")
        
        # Analyze the structure
        analysis_result = agent.analyze_structure("hemoglobin")
        if analysis_result["success"]:
            print("Analysis recommendations:")
            print(analysis_result["explanation"][:400] + "...")
    
    print("\n🎉 Demo completed!")
    print("\nTo run the agent interactively:")
    print("python pymol_agent.py --api-key YOUR_KEY --interactive")
    print("\nTo process a specific request:")
    print('python pymol_agent.py --api-key YOUR_KEY --request "your request here"')

if __name__ == "__main__":
    main()
