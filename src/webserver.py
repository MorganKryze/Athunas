import yaml
import threading
import logging
import subprocess
from typing import Dict, Any
from flask import Flask, render_template, request, redirect, url_for, jsonify
import time

from settings import Configuration
from path import PathTo


class WebServer:
    """Web server for configuring Athunas settings"""

    def __init__(self):
        """Initialize the web server"""
        self.is_connected = False
        self.lock = threading.Lock()
        self.app = Flask(
            __name__,
            template_folder=PathTo.TEMPLATES_FOLDER,
            static_folder=PathTo.STATIC_FOLDER,
        )
        self._register_routes()
        self.server_thread = None

    def _register_routes(self):
        """Register all routes with the Flask app"""
        # Landing page
        self.app.add_url_rule("/", "index", self.index)

        # Home page with configuration categories
        self.app.add_url_rule("/home", "homepage", self.homepage)

        # Edit sections
        self.app.add_url_rule(
            "/section/<section_name>", "edit_section", self.edit_section
        )
        self.app.add_url_rule(
            "/section/<section_name>/<subsection>", "edit_section", self.edit_section
        )

        # Update configuration
        self.app.add_url_rule(
            "/update", "update_config", self.update_config, methods=["POST"]
        )

        # System control
        self.app.add_url_rule(
            "/restart", "restart_system", self.restart_system, methods=["POST"]
        )
        self.app.add_url_rule(
            "/close", "close_connection", self.close_connection, methods=["POST"]
        )

    def save_config(self, config: Dict[str, Any]) -> None:
        """Save configuration to a temporary file"""
        temp_config_path = PathTo.TEMPORARY_CONFIG_FILE
        with open(temp_config_path, "w") as f:
            yaml.safe_dump(config, f)
        logging.info("Configuration saved to temporary file")

    def index(self):
        """Welcome page with warnings"""
        with self.lock:
            self.is_connected = True
        return render_template("index.html")

    def homepage(self):
        """Main page showing configuration categories"""
        config = Configuration.data

        # Split configuration into three main categories
        apps = config.get("Apps", {})
        modules = config.get("Modules", {})
        system = config.get("System", {})

        return render_template("home.html", apps=apps, modules=modules, system=system)

    def edit_section(self, section_name, subsection=None):
        """Edit a specific section/subsection of the configuration"""
        config = Configuration.data

        if section_name in config:
            if subsection and subsection in config[section_name]:
                # Edit a specific subsection
                return render_template(
                    "section.html",
                    section_name=section_name,
                    subsection=subsection,
                    section_data=config[section_name][subsection],
                )
            else:
                # Edit the whole section
                return render_template(
                    "section.html",
                    section_name=section_name,
                    section_data=config[section_name],
                )

        return redirect(url_for("homepage"))

    def update_config(self):
        """Update the configuration with form data"""
        config = Configuration.data
        data = request.form.to_dict()

        section = data.get("section")
        subsection = data.get("subsection")

        if section and section in config:
            if subsection and subsection in config[section]:
                # Update subsection
                for key, value in data.items():
                    if (
                        key not in ["section", "subsection"]
                        and key in config[section][subsection]
                    ):
                        # Convert values to appropriate types
                        if isinstance(config[section][subsection][key], bool):
                            config[section][subsection][key] = value.lower() == "true"
                        elif isinstance(config[section][subsection][key], int):
                            try:
                                config[section][subsection][key] = int(value)
                            except ValueError:
                                pass
                        elif isinstance(config[section][subsection][key], float):
                            try:
                                config[section][subsection][key] = float(value)
                            except ValueError:
                                pass
                        else:
                            config[section][subsection][key] = value
            else:
                # Update main section
                for key, value in data.items():
                    if key != "section" and key in config[section]:
                        # Convert values to appropriate types
                        if isinstance(config[section][key], bool):
                            config[section][key] = value.lower() == "true"
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

        self.save_config(config)
        return redirect(url_for("homepage"))

    def restart_system(self):
        """Restart the Raspberry Pi to apply configuration changes"""
        logging.info("System restart requested from web interface")

        def restart():
            time.sleep(1)  # Brief delay to allow response to be sent
            subprocess.call(["sudo", "reboot"])

        threading.Thread(target=restart).start()
        return jsonify({"status": "Restarting to apply configuration changes..."})

    def close_connection(self):
        """Close the connection and re-enable matrix control"""
        with self.lock:
            self.is_connected = False

        return jsonify({"status": "Connection closed"})

    def is_user_connected(self) -> bool:
        """Check if anyone is connected to the web interface"""
        with self.lock:
            return self.is_connected

    def start(self, port: int, debug: bool) -> threading.Thread:
        """Start the web server in a separate thread"""

        def run_server():
            self.app.run(host="0.0.0.0", port=port, debug=debug)

        self.server_thread = threading.Thread(target=run_server)
        self.server_thread.daemon = True
        self.server_thread.start()

        logging.info(f"Web server started on port {port}")
        return self.server_thread
