import threading
import subprocess
import time
from flask import Flask, request, jsonify
from research_agent.agent import ResearchAgent
import signal
import sys

# Global agent instance
agent = None
flask_thread = None
streamlit_process = None

app = Flask(__name__)

def run_flask():
    """Run the Flask API server"""
    app.run(host='0.0.0.0', port=5000)

def run_streamlit():
    """Run the Streamlit interface"""
    global streamlit_process
    streamlit_process = subprocess.Popen([
        'streamlit', 'run', 
        'research_agent/streamlit_app.py',
        '--server.port=8501',
        '--server.headless=true',
        '--browser.serverAddress=0.0.0.0'
    ])

def shutdown_handler(signum, frame):
    """Handle graceful shutdown"""
    global streamlit_process
    if streamlit_process:
        streamlit_process.terminate()
    sys.exit(0)

@app.route('/initialize', methods=['POST'])
def initialize_agent():
    global agent
    try:
        data = request.json
        agent = ResearchAgent(
            gemini_api_key=data['gemini_api_key'],
            google_api_key=data['google_api_key'],
            google_cse_id=data['google_cse_id']
        )
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/research', methods=['POST'])
def research():
    if not agent:
        return jsonify({"error": "Agent not initialized"}), 400
    
    try:
        query = request.json['query']
        results = agent.research(query)
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def main():
    global flask_thread

    # Set up signal handler for Ctrl+C
    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    # Start Flask in a separate thread
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # Wait briefly for Flask to start
    time.sleep(1)
    
    # Start Streamlit
    run_streamlit()
    
    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        shutdown_handler(None, None)

if __name__ == '__main__':
    main()