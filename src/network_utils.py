"""
FaceRunner Network Utilities - Network configuration and verification functions.
"""

import requests
import json
from pathlib import Path

OLLAMA_PORT = 11434
WEBUI_PORT = 8080

def verify_accessibility():
    """Verify Ollama and WebUI accessibility."""
    from system_utils import get_host_ip
    host_ip = get_host_ip()
    messages = []

    # Test Ollama
    try:
        response = requests.post(f"http://localhost:{OLLAMA_PORT}/api/generate",
                                json={"model": "llama3.1", "prompt": "Hello"}, timeout=10)
        if response.status_code == 200:
            messages.append(f"Ollama is accessible locally (URL: http://localhost:{OLLAMA_PORT}/api/generate).")
        else:
            messages.append(f"Ollama responded but with error. Tried URL: http://localhost:{OLLAMA_PORT}/api/generate")
    except requests.RequestException as e:
        messages.append(f"Ollama not accessible locally. Tried URL: http://localhost:{OLLAMA_PORT}/api/generate. Error: {e}")

    # Test WebUI
    try:
        response = requests.get(f"http://localhost:{WEBUI_PORT}", timeout=10)
        if response.status_code == 200:
            messages.append("Open WebUI is accessible locally.")
        else:
            messages.append("Open WebUI responded but with error.")
    except requests.RequestException:
        messages.append("Open WebUI not accessible locally.")

    try:
        response = requests.get(f"http://{host_ip}:{WEBUI_PORT}", timeout=10)
        if response.status_code == 200:
            messages.append(f"Open WebUI is accessible over network at {host_ip}.")
        else:
            messages.append("Open WebUI responded but with error over network.")
    except requests.RequestException:
        messages.append("Open WebUI not accessible over network.")

    return messages

def configure_network():
    """Configure network and firewall settings."""
    from system_utils import get_os, configure_firewall_linux, configure_firewall_windows, configure_firewall_macos, get_host_ip
    messages = []
    os_type = get_os()
    if os_type == 'linux':
        messages.append(configure_firewall_linux())
    elif os_type == 'windows':
        messages.append(configure_firewall_windows())
    elif os_type == 'darwin':
        messages.append(configure_firewall_macos())
    else:
        pass

    host_ip = get_host_ip()
    messages.append(f"Host IP: {host_ip}")
    messages.append("Ensure your network allows connections to ports 11434 and 8080.")
    return messages

def integrate_vscode(ip):
    """Generate VS Code Continue config for the given host IP."""
    import yaml
    from ollama_utils import list_installed_models

    import streamlit as st
    ollama_mode = st.session_state.get("ollama_mode", "Docker")
    models_output = list_installed_models()
    models = []
    lines = models_output.strip().split('\n')
    for line in lines[1:]:
        if line.strip():
            parts = line.split()
            model_id = parts[0]
            if ollama_mode == "Local":
                api_base = f"http://127.0.0.1:{OLLAMA_PORT}"
            else:
                api_base = f"http://{ip}:{OLLAMA_PORT}"
            model_entry = {
                "name": model_id,
                "provider": "ollama",
                "model": model_id,
                "apiBase": api_base
            }
            models.append(model_entry)

    config = {
        "name": "Local Agent",
        "version": "1.0.0",
        "schema": "v1",
        "models": models
    }

    config_yaml = yaml.dump(config, sort_keys=False)

    config_dir = Path.home() / ".continue"
    config_dir.mkdir(exist_ok=True)
    config_file = config_dir / "config.yaml"
    with open(config_file, 'w') as f:
        f.write(config_yaml)

    return config_yaml
