#!/usr/bin/env python3
"""
PyMOL Agent Web Interface
Flask web application with ChatGPT-style interface for PyMOL code generation
"""

from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import os
import json
import uuid
from datetime import datetime
from pymol_agent import PyMOLAgent

app = Flask(__name__)
app.secret_key = os.urandom(24)
CORS(app)

# Initialize PyMOL agent
try:
    pymol_agent = PyMOLAgent(model="gpt-4o")
    print("✅ PyMOL Agent initialized successfully")
except Exception as e:
    print(f"❌ Error initializing PyMOL Agent: {e}")
    pymol_agent = None

@app.route('/')
def index():
    """Main chat interface"""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages and generate PyMOL code"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        if not pymol_agent:
            return jsonify({'error': 'PyMOL Agent not initialized'}), 500
        
        # Generate session ID if not exists
        if 'session_id' not in session:
            session['session_id'] = str(uuid.uuid4())
        
        # Generate PyMOL code using the agent
        result = pymol_agent.generate_pymol_code(user_message)
        
        if result['success']:
            response = {
                'success': True,
                'message': result['explanation'],
                'pymol_commands': result['pymol_commands'],
                'timestamp': datetime.now().isoformat(),
                'session_id': session['session_id']
            }
        else:
            response = {
                'success': False,
                'error': result.get('error', 'Unknown error occurred'),
                'timestamp': datetime.now().isoformat()
            }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'pymol_agent_available': pymol_agent is not None,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/clear', methods=['POST'])
def clear_chat():
    """Clear chat history"""
    try:
        if pymol_agent:
            pymol_agent.conversation_history = []
        session.clear()
        return jsonify({'success': True, 'message': 'Chat history cleared'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    print("🧬 Starting PyMOL Agent Web Interface...")
    print("🌐 Access the application at: http://localhost:5000")
    print("💡 Make sure your OpenAI API key is set in the .env file")
    app.run(debug=True, host='0.0.0.0', port=5001)
