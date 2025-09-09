"""
FaceRunner CLI - Automate Ollama and Open WebUI setup for Hugging Face models.
"""

import click
import docker
import requests
import socket
import platform
import subprocess
import sys
import json
import os
import time
import re
import itertools
import threading
from pathlib import Path

WEBUI_IMAGE = "ghcr.io/open-webui/open-webui:main"
STREAMLIT_IMAGE = "facerunner-webui:latest"
OLLAMA_IMAGE = "ollama/ollama:latest"
OPENWEBUI_IMAGE = "ghcr.io/open-webui/open-webui:main"
OLLAMA_PORT = 11434
WEBUI_PORT = 8080
STREAMLIT_PORT = 8501

def get_host_ip():
    """Get the host's IP address."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def get_os():
    """Get the operating system."""
    return platform.system().lower()

def configure_firewall_linux():
    """Configure firewall on Linux."""
    try:
        subprocess.run(["sudo", "ufw", "allow", str(OLLAMA_PORT)], check=True)
        subprocess.run(["sudo", "ufw", "allow", str(WEBUI_PORT)], check=True)
        return "Firewall configured for Linux."
    except subprocess.CalledProcessError:
        return "Failed to configure firewall. You may need to run with sudo."

def configure_firewall_windows():
    """Configure firewall on Windows."""
    try:
        subprocess.run([
            "netsh", "advfirewall", "firewall", "add", "rule",
            "name=Ollama", "dir=in", "action=allow", "protocol=TCP", "localport=" + str(OLLAMA_PORT)
        ], check=True)
        subprocess.run([
            "netsh", "advfirewall", "firewall", "add", "rule",
            "name=OpenWebUI", "dir=in", "action=allow", "protocol=TCP", "localport=" + str(WEBUI_PORT)
        ], check=True)
        return "Firewall configured for Windows."
    except subprocess.CalledProcessError:
        return "Failed to configure firewall."

def configure_firewall_macos():
    """Configure firewall on macOS."""
    return "macOS firewall configuration: Please allow ports 11434 and 8080 in System Settings > Network > Firewall."

def check_webui_running():
    """Check if FaceRunner web UI is already running on port 8501."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', STREAMLIT_PORT))
        sock.close()
        return result == 0
    except Exception:
        return False

def kill_existing_webui():
    """Kill any existing FaceRunner web UI processes."""
    try:
        if platform.system().lower() == 'windows':
            subprocess.run(["taskkill", "/f", "/im", "streamlit.exe"], capture_output=True)
        else:
            subprocess.run(["pkill", "-f", "streamlit.*webui.py"], capture_output=True)
        time.sleep(1)
        return True
    except Exception:
        return False

def parse_model_name(model_input):
    """Parse and convert various model name formats to Ollama format."""
    model_input = model_input.strip()
    if model_input.startswith("https://huggingface.co/"):
        match = re.search(r"huggingface\.co/([^/]+/[^/]+)", model_input)
        if match:
            model_name = match.group(1)
        else:
            return model_input, f"Could not parse model name from URL: {model_input}"
    elif "/" in model_input:
        model_name = model_input
    else:
        return model_input, None

    conversions = {
        "openai/gpt-oss-20b": "gpt-oss:20b",
        "openai/gpt-oss-120b": "gpt-oss:120b",
        "meta-llama/llama-3.1-8b": "llama3.1:8b",
        "meta-llama/llama-3.1-70b": "llama3.1:70b",
        "meta-llama/llama-3.1-405b": "llama3.1:405b",
        "microsoft/wizardlm-2-8x22b": "wizardlm2:8x22b",
        "mistralai/mistral-7b-instruct": "mistral:7b",
        "mistralai/mixtral-8x7b-instruct": "mixtral:8x7b",
        "google/gemma-7b": "gemma:7b",
        "google/gemma-2-9b": "gemma2:9b",
    }

    if model_name in conversions:
        ollama_name = conversions[model_name]
        return ollama_name, f"Converted {model_name} → {ollama_name}"

    if "gpt-oss-20b" in model_name:
        return "gpt-oss:20b", f"Converted {model_name} → gpt-oss:20b"
    elif "gpt-oss-120b" in model_name:
        return "gpt-oss:120b", f"Converted {model_name} → gpt-oss:120b"
    elif "llama-3.1-8b" in model_name:
        return "llama3.1:8b", f"Converted {model_name} → llama3.1:8b"
    elif "llama-3.1-70b" in model_name:
        return "llama3.1:70b", f"Converted {model_name} → llama3.1:70b"
    elif "llama-3.1-405b" in model_name:
        return "llama3.1:405b", f"Converted {model_name} → llama3.1:405b"

    return model_name, f"No conversion found for {model_name}, trying as-is"

def wait_for_containers_removal(patterns, max_wait=10):
    """Spinner and wait/check for container removal."""
    spinner = itertools.cycle(['|', '/', '-', '\\'])
    waited = 0
    while True:
        ps_result = subprocess.run([
            "docker", "ps", "-a", "--format", "{{.ID}} {{.Names}}"
        ], capture_output=True, text=True)
        found = False
        for line in ps_result.stdout.strip().split('\n'):
            if not line:
                continue
            _, cname = line.split(maxsplit=1)
            if any(p in cname for p in patterns):
                found = True
                break
        if not found or waited >= max_wait:
            break
        sys.stdout.write(f"\r{next(spinner)} Waiting for containers to be removed...   ")
        sys.stdout.flush()
        time.sleep(0.5)
        waited += 0.5
    sys.stdout.write("\r   \r")
    sys.stdout.flush()

def launch_webui_background():
    """Launch FaceRunner web UI in the background."""
    try:
        if check_webui_running():
            click.echo("🔄 Existing web UI found. Terminating...")
            kill_existing_webui()
            click.echo("✅ Existing web UI terminated.")

        click.echo("🚀 Launching FaceRunner web UI in background...")
        process = subprocess.Popen([
            "streamlit", "run", "src/main.py",
            "--server.address", "0.0.0.0",
            "--server.port", str(STREAMLIT_PORT),
            "--server.headless", "true"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        time.sleep(2)
        if check_webui_running():
            click.echo("✅ FaceRunner web UI launched successfully!")
            click.echo(f"🌐 Web UI available at: http://localhost:{STREAMLIT_PORT}")
            return True
        else:
            click.echo("❌ Failed to launch web UI")
            return False
    except Exception as e:
        click.echo(f"❌ Error launching web UI: {e}")
        return False

@click.group()
def cli():
    """FaceRunner CLI for managing Ollama and Open WebUI."""
    pass

@cli.command()
@click.option('--verbose', is_flag=True, help='Show detailed Docker Compose logs during setup.')
def setup(verbose):
    def is_ollama_running():
        try:
            result = subprocess.run(["pgrep", "-f", "ollama"], capture_output=True)
            return result.returncode == 0
        except Exception:
            return False

    def start_ollama():
      click.echo("🚀 Starting Ollama service on localhost...")
      env = os.environ.copy()
      env["OLLAMA_HOST"] = "localhost"
      proc = subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env)
      time.sleep(2)
      return proc
      # Check if ollama is installed
    def is_ollama_installed():
        return subprocess.run(["which", "ollama"], capture_output=True).returncode == 0

    def install_ollama():
        os_type = get_os()
        if os_type == "linux":
            click.echo("Ollama not found. Installing Ollama for Linux...")
            result = subprocess.run("curl -fsSL https://ollama.com/install.sh | sh", shell=True)
            if result.returncode == 0:
                click.echo("✅ Ollama installed successfully.")
            else:
                click.echo("❌ Failed to install Ollama automatically. Please install manually from https://ollama.com/download.")
        else:
            click.echo(f"Ollama installation not automated for {os_type}. Please install manually from https://ollama.com/download.")

    if not is_ollama_installed():
        install_ollama()
    click.echo("🔧 Starting FaceRunner local setup...")
    def is_openwebui_installed():
        return subprocess.run(["which", "open-webui"], capture_output=True).returncode == 0
    def install_openwebui():
        click.echo("🔎 Installing Open WebUI via pip...")
        result = subprocess.run([sys.executable, "-m", "pip", "install", "open-webui"], capture_output=True, text=True)
        if result.returncode == 0:
            click.echo("✅ Open WebUI installed successfully.")
            return True
        else:
            click.echo(f"❌ Failed to install Open WebUI: {result.stderr}")
            click.echo("Please install manually: pip install open-webui")
            return False

    try:
        # Ensure Ollama service is running
        if is_ollama_running():
            click.echo("🔄 Ollama is already running. Restarting...")
            subprocess.run(["pkill", "-f", "ollama"], capture_output=True)
            time.sleep(2)
        start_ollama()
        click.echo(f"🤖 Ollama service started on port {OLLAMA_PORT}")
        # Ensure Open WebUI is installed
        if not is_openwebui_installed():
            if not install_openwebui():
                return
        # Start Open WebUI locally
        click.echo("🚀 Starting Open WebUI locally...")
        webui_proc = subprocess.Popen([
            "open-webui", "serve", "--host", "0.0.0.0", "--port", str(WEBUI_PORT)
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(2)
        click.echo(f"🌐 Open WebUI (chat interface): http://localhost:{WEBUI_PORT}")
        # Start FaceRunner web UI (Streamlit)
        click.echo("🚀 Starting FaceRunner web UI locally...")
        launch_webui_background()
        click.echo("🎉 Setup complete!")
        click.echo("\n🔗 Access your services:")
        click.echo(f"  🤖 Ollama API:        http://localhost:{OLLAMA_PORT}")
        click.echo(f"  🌐 Open WebUI:        http://localhost:{WEBUI_PORT}")
        click.echo(f"  🖥️ FaceRunner Web UI: http://localhost:{STREAMLIT_PORT}")
    except Exception as e:
        click.echo(f"❌ Error during local setup: {e}")

@cli.command()
@click.argument('model')
def pull(model):
    """Pull a Hugging Face model into Ollama with automatic format conversion."""
    click.echo(f"📥 Pulling model: {model}")

    try:
        ollama_model, conversion_msg = parse_model_name(model)
        if conversion_msg:
            click.echo(f"🤖 {conversion_msg}")
        click.echo("� Executing pull command in local Ollama...")
        result = subprocess.run([
            "ollama", "pull", ollama_model
        ], capture_output=True, text=True)
        if result.returncode == 0:
            click.echo(f"✅ Model {ollama_model} pulled successfully!")
            if conversion_msg and "Converted" in conversion_msg:
                click.echo(f"📝 {conversion_msg}")
        else:
            click.echo(f"❌ Error pulling model: {result.stderr}")
    except Exception as e:
        click.echo(f"❌ Error during model pull: {e}")

@cli.command()
def start():
    """Start all FaceRunner services locally (no Docker)."""
    # Start Ollama
    click.echo("🚀 Starting FaceRunner services...")
    # Start Ollama
    click.echo("✅ Starting Ollama server...")
    try:
        subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        click.echo("   Ollama started.")
    except Exception as e:
        click.echo(f"❌ Error starting Ollama: {e}")
    time.sleep(2)
    # Start Open WebUI
    click.echo("✅ Starting Open WebUI...")
    try:
        subprocess.Popen(["open-webui", "serve", "--host", "0.0.0.0", "--port", str(WEBUI_PORT)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        click.echo("   Open WebUI started.")
    except Exception as e:
        click.echo(f"❌ Error starting Open WebUI: {e}")
    time.sleep(2)
    # Start FaceRunner Web UI
    click.echo("✅ Launching FaceRunner web UI in background...")
    webui_started = launch_webui_background()
    if webui_started:
        click.echo("✅ FaceRunner web UI launched successfully!")
        click.echo(f"🌐 Web UI available at: http://localhost:{STREAMLIT_PORT}")
    else:
        click.echo("⚠️  Web UI failed to launch. Run 'facerunner webui' manually.")

@cli.command()
def stop():
    """Stop all FaceRunner services (Ollama, Open WebUI, FaceRunner Web UI)."""
    click.echo("🛑 Stopping FaceRunner services...")
    errors = []
    # Stop Ollama
    try:
        subprocess.run(["pkill", "-f", "ollama"], check=False)
        click.echo("✅ Ollama stopped.")
    except Exception as e:
        errors.append(f"Ollama: {e}")
    # Stop Open WebUI
    try:
        subprocess.run(["pkill", "-f", "open-webui"], check=False)
        click.echo("✅ Open WebUI stopped.")
    except Exception as e:
        errors.append(f"Open WebUI: {e}")
    # Stop FaceRunner Web UI
    try:
        subprocess.run(["pkill", "-f", "streamlit.*main.py"], check=False)
        subprocess.run(["pkill", "-f", "streamlit.*webui.py"], check=False)
        click.echo("✅ FaceRunner Web UI stopped.")
    except Exception as e:
        errors.append(f"FaceRunner Web UI: {e}")
    if errors:
        click.echo("⚠️  Some errors occurred:")
        for err in errors:
            click.echo(f"   {err}")
    else:
        click.echo("✅ All FaceRunner services stopped successfully.")
        # Removed stray except blocks

@cli.command()
def verify():
    """Verify Ollama, Open WebUI, and FaceRunner Web UI accessibility."""
    click.echo("🔍 Verifying FaceRunner services...")

    host_ip = get_host_ip()
    click.echo(f"📍 Host IP: {host_ip}")

    # Test Ollama
    click.echo("🤖 Testing Ollama API...")
    try:
        click.echo("  📡 Testing local connection...")
        response = requests.post(f"http://localhost:{OLLAMA_PORT}/api/generate",
                                json={"model": "llama3.1", "prompt": "Hello"}, timeout=10)
        if response.status_code == 200:
            click.echo("  ✅ Ollama accessible locally")
        else:
            click.echo(f"  ⚠️  Ollama responded with status {response.status_code}")
    except requests.RequestException as e:
        click.echo(f"  ❌ Ollama not accessible locally: {e}")

    try:
        click.echo(f"  🌐 Testing network connection ({host_ip})...")
        response = requests.post(f"http://{host_ip}:{OLLAMA_PORT}/api/generate",
                                json={"model": "llama3.1", "prompt": "Hello"}, timeout=10)
        if response.status_code == 200:
            click.echo(f"  ✅ Ollama accessible over network at {host_ip}")
        else:
            click.echo(f"  ⚠️  Ollama responded with status {response.status_code} over network")
    except requests.RequestException as e:
        click.echo(f"  ❌ Ollama not accessible over network: {e}")

    # Test WebUI
    click.echo("🌐 Testing Open WebUI...")
    try:
        click.echo("  📡 Testing local connection...")
        response = requests.get(f"http://localhost:{WEBUI_PORT}", timeout=10)
        if response.status_code == 200:
            click.echo("  ✅ Open WebUI accessible locally")
        else:
            click.echo(f"  ⚠️  Open WebUI responded with status {response.status_code}")
    except requests.RequestException as e:
        click.echo(f"  ❌ Open WebUI not accessible locally: {e}")

    try:
        click.echo(f"  🌐 Testing network connection ({host_ip})...")
        response = requests.get(f"http://{host_ip}:{WEBUI_PORT}", timeout=10)
        if response.status_code == 200:
            click.echo(f"  ✅ Open WebUI accessible over network at {host_ip}")
        else:
            click.echo(f"  ⚠️  Open WebUI responded with status {response.status_code} over network")
    except requests.RequestException as e:
        click.echo(f"  ❌ Open WebUI not accessible over network: {e}")

    # Test FaceRunner Web UI (runs locally, not in container)
    click.echo("🎛️  Testing FaceRunner Web UI...")
    click.echo("  💡 Note: Web UI runs locally - use 'facerunner webui' to start it")
    try:
        click.echo("  📡 Testing local connection...")
        response = requests.get(f"http://localhost:{STREAMLIT_PORT}", timeout=10)
        if response.status_code == 200:
            click.echo("  ✅ FaceRunner Web UI accessible locally")
        else:
            click.echo(f"  ⚠️  FaceRunner Web UI responded with status {response.status_code}")
    except requests.RequestException as e:
        click.echo(f"  ❌ FaceRunner Web UI not accessible locally (use 'facerunner webui' to start it)")

    try:
        click.echo(f"  🌐 Testing network connection ({host_ip})...")
        response = requests.get(f"http://{host_ip}:{STREAMLIT_PORT}", timeout=10)
        if response.status_code == 200:
            click.echo(f"  ✅ FaceRunner Web UI accessible over network at {host_ip}")
        else:
            click.echo(f"  ⚠️  FaceRunner Web UI responded with status {response.status_code} over network")
    except requests.RequestException as e:
        click.echo(f"  ❌ FaceRunner Web UI not accessible over network (use 'facerunner webui' to start it)")

    click.echo("🎯 Verification complete!")

@cli.command()
def configure_network():
    """Configure network and firewall settings."""
    os_type = get_os()
    if os_type == 'linux':
        result = configure_firewall_linux()
    elif os_type == 'windows':
        result = configure_firewall_windows()
    elif os_type == 'darwin':
        result = configure_firewall_macos()
    else:
        result = "Unknown OS; firewall not configured."
    click.echo(result)

    host_ip = get_host_ip()
    click.echo(f"Host IP: {host_ip}")
    click.echo("Ensure your network allows connections to ports 11434 and 8080.")

@cli.command()
@click.argument('ip')
def integrate_vscode(ip):
    """Generate VS Code Continue config for the given host IP."""
    config = {
        "models": [
            {
                "title": "Ollama Llama3.1",
                "provider": "ollama",
                "model": "llama3.1",
                "apiBase": f"http://{ip}:{OLLAMA_PORT}"
            }
        ]
    }

    config_dir = Path.home() / ".continue"
    config_dir.mkdir(exist_ok=True)
    config_file = config_dir / "config.json"

    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)

    click.echo(f"VS Code config generated at {config_file}")
    click.echo("Restart VS Code and use the Continue extension.")

@cli.command()
def list():
    """List all installed Ollama models."""
    click.echo("📦 Installed Ollama models:")
    click.echo("-" * 50)

    try:
        result = subprocess.run(
            ["docker", "compose", "exec", "ollama", "ollama", "list"],
            capture_output=True,
            text=True,
            cwd="."
        )
        if result.returncode == 0:
            click.echo(result.stdout)
        else:
            click.echo(f"❌ Error listing models: {result.stderr}")
    except subprocess.CalledProcessError as e:
        click.echo(f"❌ Error listing models: {e}")
    except FileNotFoundError:
        click.echo("❌ docker compose not found. Please install Docker Compose v2.")
    except Exception as e:
        click.echo(f"❌ Unexpected error: {e}")

@cli.command()
@click.argument('model')
def remove(model):
    """Remove a model from Ollama."""
    click.echo(f"🗑️  Removing model: {model}")

    try:
        result = subprocess.run(
            ["docker", "compose", "exec", "ollama", "ollama", "rm", model],
            capture_output=True,
            text=True,
            cwd="."
        )
        if result.returncode == 0:
            click.echo(f"✅ Model {model} removed successfully!")
        else:
            click.echo(f"❌ Error removing model: {result.stderr}")
    except subprocess.CalledProcessError as e:
        click.echo(f"❌ Error removing model: {e}")
    except FileNotFoundError:
        click.echo("❌ docker compose not found. Please install Docker Compose v2.")
    except Exception as e:
        click.echo(f"❌ Unexpected error: {e}")

@cli.command()
@click.option('--server-address', default='localhost', help='Server address to bind to')
@click.option('--server-port', default=8501, type=int, help='Server port to bind to')
def webui(server_address, server_port):
    """Launch the FaceRunner web UI."""
    subprocess.run([
        "streamlit", "run", "src/webui.py",
        "--server.address", server_address,
        "--server.port", str(server_port)
    ])

def main():
    cli()

if __name__ == '__main__':
    main()