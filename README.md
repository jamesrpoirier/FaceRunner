# FaceRunner 🚀

FaceRunner is a modern tool for managing and running local AI models (Ollama) with a simple CLI and a Streamlit-based web UI. It is designed for local use only—no Docker, no remote access, no network configuration required.

## Features ✨

- 🟢 **One-command setup and start:** `facerunner setup` and `facerunner start` handle everything for you.
- 🔄 **Automatic model name conversion:** Hugging Face model names are converted to Ollama-compatible names in both CLI and web UI.
- 📦 **Model management:** List, pull, and remove models via CLI and web UI. The web UI suggests popular models and allows parameter size selection for supported models.
- 🧩 **Service orchestration:** Starts Ollama, Open WebUI, and FaceRunner Web UI as local processes (no Docker required).
- 🖥️ **Streamlit-based management UI:** Enhanced graphical interface for model management, conversion, and service status.
- ⚠️ **Clear error feedback:** Improved error handling and messaging for setup and service management.
- ▶️ **Simple start/stop:** `facerunner start` and `facerunner stop` launch and kill all associated services with friendly status messages.
- 🔒 **No firewall or network config needed:** Everything runs on localhost.

## Project Structure 🗂️

```
FaceRunner/
├── src/
│   ├── facerunner/
│   │   └── __init__.py  # Main CLI code
│   └── main.py          # Web UI code
├── pyproject.toml       # Project configuration and dependencies
└── README.md            # This file
```

## Installation and Usage 🛠️

### Prerequisites
- 🐍 Python 3.8+
- (Optional) ⚡ GPU support for acceleration

### Installation (for all users)
Create a Python virtual environment and install FaceRunner in editable mode:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

After installation, you can run FaceRunner commands from the same terminal session:
```bash
facerunner setup
facerunner start
```

### Development Setup (for contributors)
If you want to develop or customize FaceRunner, use a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### Usage 💡

**Quick Start:**

Just run:
```bash
facerunner setup
```
This command will automatically start Ollama, Open WebUI, and the FaceRunner Web UI. For most users, this is all you need—no manual steps required.

---

Other commands:
```bash
# ▶️ Start all services (if you need to restart after setup)
facerunner start

# ⏹️ Stop all services
facerunner stop

# 📥 Pull a model
facerunner pull llama3.1

# 🗑️ Remove a model
facerunner remove llama3.1

# 🖥️ Launch just the web UI (if needed)
facerunner webui
```

### Web UI 🌐
- **FaceRunner Management Web UI:** http://localhost:8501
- **Open WebUI Chat Interface:** http://localhost:8080

### Model Management 🧠
- Use the CLI or the web UI to pull, list, and remove models.
- The web UI allows you to select parameter sizes for supported models (e.g., gemma2:2b, gemma2:9b, gemma2:27b, etc.).
- Popular models are suggested in the UI for quick access.

## Troubleshooting 🛟
- If a service does not start, run it manually in your terminal to see error output (e.g., `ollama serve`, `open-webui serve --host 0.0.0.0 --port 8080`).
- Make sure all required executables are installed and available in your PATH.
- Use `facerunner stop` to cleanly kill all services if something hangs.

## Development & Customization 🛠️
- All code is in `src/` for easy modification.
- The CLI and web UI are designed to be extensible for new features and model types.
- No Docker, no network config, no firewall rules—just local Python and binaries.

## Suggestions & Roadmap 🗺️
- Add support for more model formats (ONNX, TensorFlow, etc.)
- Add user authentication for the web UI
- Add model performance monitoring
- Add multi-user support
- Add more RESTful API endpoints
- Expand documentation and troubleshooting guides

---

FaceRunner is designed for simplicity, reliability, and local-first AI workflows. If you have feature requests or want to contribute, open an issue or pull request! 😄
