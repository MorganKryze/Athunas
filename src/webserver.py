import os
import sys
import yaml
import threading
import logging
import signal
import subprocess
from typing import Dict, Any, List, Optional
from flask import Flask, render_template, request, redirect, url_for, jsonify
import time

from settings import Settings
from path import PathTo
from enums.variable_importance import Importance

app = Flask(__name__, 
            template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), "../web/templates"),
            static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), "../web/static"))

# Global variable to track if someone is connected
is_connected = False
# Global variable to store the control thread for matrix
matrix_control_thread = None
# Lock to prevent race conditions
lock = threading.Lock()

def load_config() -> Dict[str, Any]:
    """Load configuration from file"""
    with open(PathTo.CONFIG_FILE, 'r') as f:
        return yaml.safe_load(f)

def save_config(config: Dict[str, Any]) -> None:
    """Save configuration to file"""
    with open(PathTo.CONFIG_FILE, 'w') as f:
        yaml.safe_dump(config, f)
    logging.info("Configuration saved")

@app.route('/')
def index():
    """Main page showing configuration sections"""
    global is_connected
    
    with lock:
        is_connected = True
        
    config = load_config()
    sections = list(config.keys())
    return render_template(PathTo.INDEX_HTML_FILE, sections=sections)

@app.route('/section/<section_name>')
def edit_section(section_name):
    """Edit a specific section of the configuration"""
    config = load_config()
    if section_name in config:
        return render_template(PathTo.SECTION_HTML_FILE, 
                              section_name=section_name, 
                              section_data=config[section_name])
    return redirect(url_for('index'))

@app.route('/update', methods=['POST'])
def update_config():
    """Update the configuration with form data"""
    config = load_config()
    data = request.form.to_dict()
    
    section = data.get('section')
    if section and section in config:
        for key, value in data.items():
            if key != 'section' and key in config[section]:
                # Convert values to appropriate types
                if isinstance(config[section][key], bool):
                    config[section][key] = (value.lower() == 'true')
                elif isinstance(config[section][key], int):
                    try:
                        config[section][key] = int(value)
                    except ValueError:
                        pass
                elif isinstance(config[section][key], float):
                    try:
                        config[section][key] = float(value)
                    except ValueError:
                        pass
                else:
                    config[section][key] = value
    
    save_config(config)
    return redirect(url_for('index'))

@app.route('/restart', methods=['POST'])
def restart_system():
    """Restart the Raspberry Pi"""
    logging.info("System restart requested from web interface")
    
    def restart():
        time.sleep(1)  # Brief delay to allow response to be sent
        subprocess.call(['sudo', 'reboot'])
    
    threading.Thread(target=restart).start()
    return jsonify({"status": "Restarting..."})

@app.route('/close', methods=['POST'])
def close_connection():
    """Close the connection and re-enable matrix control"""
    global is_connected
    
    with lock:
        is_connected = False
        
    return jsonify({"status": "Connection closed"})

def is_user_connected() -> bool:
    """Check if anyone is connected to the web interface"""
    global is_connected
    with lock:
        return is_connected

def start_web_server(port: int = 8080, debug: bool = False) -> threading.Thread:
    """Start the web server in a separate thread"""
    def run_server():
        app.run(host='0.0.0.0', port=port, debug=debug)
    
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()
    
    logging.info(f"Web server started on port {port}")
    return server_thread