# FaceRunner Features

This document outlines the features and roadmap for FaceRunner, a tool for managing Ollama, Open WebUI, and Hugging Face models—fully local, no containers or Docker required.

## Core Features

- **One-command setup and start:** `facerunner setup` prepares and launches all services.
- **Automatic model name conversion:** Hugging Face model names are converted to Ollama-compatible names in CLI and web UI.
- **Model management:** List, pull, and remove models via CLI and web UI. Parameter size selection and popular model suggestions in the UI.
- **Service orchestration:** Starts Ollama, Open WebUI, and FaceRunner Web UI as local processes.
- **Streamlit-based management UI:** Graphical interface for model management, conversion, and service status.
- **Clear error feedback:** Improved error handling and messaging for setup and service management.
- **Simple start/stop:** `facerunner start` and `facerunner stop` launch and kill all associated services with friendly status messages.
- **No firewall or network config needed:** Everything runs on localhost.

## CLI Features

- **Setup Command:** One-command initialization of the entire environment.
- **Pull Command:** Download specific models with progress indication.
- **Start/Stop Commands:** Control running state of services.
- **Verify Command:** Test accessibility of Ollama API and WebUI.
- **Web UI Command:** Launch the Streamlit-based web interface.
- **VS Code Integration Command:** Generate configuration for Continue extension.
- **Update Command:** Check for and apply updates to FaceRunner.
- **Interactive Mode (Planned):** Guided setup with prompts for user preferences.
- **Configuration File (Planned):** Support for YAML/JSON config files for custom settings.
- **Batch Operations (Planned):** Support for pulling multiple models at once.
- **Dry Run Mode (Planned):** Preview actions without executing them.
- **Status Command (Planned):** Show current state of services.
- **Logs Command (Planned):** Display service logs for debugging.

## Web UI Features

- **Dashboard:** Main interface with buttons for all major operations.
- **Setup Interface:** Guided setup process with progress indicators.
- **Model Management:** Pull models with input field and status feedback.
- **Service Control:** Start/stop buttons with real-time status updates.
- **Verification Tools:** Test connectivity with detailed results.
- **VS Code Integration:** Generate config files with IP input.
- **Model Browser (Planned):** Browse available models from Ollama and Hugging Face.
- **Chat Interface Integration (Planned):** Direct link to Open WebUI chat.
- **Log Viewer (Planned):** Display and filter service logs in the web UI.
- **Settings Panel (Planned):** Configure FaceRunner preferences through the web.
- **Multi-user Support (Planned):** Basic user management for shared deployments.
- **Real-time Monitoring (Planned):** Live status dashboard with service metrics.

## Model and Data Features

- **Custom Model Support (Planned):** Upload and serve custom models.
- **Universal Hugging Face Model & Transformer Support (Planned):** Add, run, and manage all types of models and transformers from Hugging Face (not limited to GGUF/Ollama-compatible models).
- **Model Optimization (Planned):** Automatic quantization and optimization.
- **Dataset Management (Planned):** Tools for managing training datasets.
- **Backup and Restore (Planned):** Backup/restore model data and configurations.

## Platform Support

- **Linux:** Full support.
- **macOS:** Support with manual firewall configuration guidance.
- **Windows:** Support with Windows Firewall management.
- **NVIDIA GPU:** CUDA support for GPU acceleration.
- **AMD GPU (Planned):** ROCm support for AMD GPUs.
- **Apple Silicon (Planned):** Optimized support for M1/M2 Macs.
- **CPU-only (Planned):** Fallback for systems without GPU support.

## Advanced Features (Planned)

- **Performance Monitoring:** Track GPU usage, memory consumption, and inference times.
- **Usage Statistics:** Log model usage patterns and popular models.
- **Health Checks:** Automated monitoring of service availability.
- **Alert System:** Notifications for service failures or resource issues.
- **API Endpoints:** REST API for programmatic access to FaceRunner functions.
- **Webhook Support:** Callbacks for events like model downloads or service status changes.
- **Multi-host Deployment:** Manage multiple FaceRunner instances.
- **Load Balancing:** Distribute requests across multiple Ollama instances.

## Quality Assurance

- **Unit Tests (Planned):** Test individual functions and modules.
- **Integration Tests (Planned):** Test end-to-end workflows.
- **UI Tests (Planned):** Automated testing of web interface.
- **Performance Tests (Planned):** Benchmark model loading and inference.

## Documentation

- **README:** Basic installation and usage instructions.
- **API Documentation (Planned):** Detailed API reference.
- **Troubleshooting Guide (Planned):** Common issues and solutions.
- **Developer Guide (Planned):** Contributing guidelines and architecture.

## Maintenance

- **Automated Updates (Planned):** Check for FaceRunner and dependency updates.
- **Dependency Management (Planned):** Keep Python packages up to date.
- **Security Audits (Planned):** Regular security vulnerability checks.
- **Backup Strategies (Planned):** Automated backup of configurations and data.

## Roadmap

### Short Term (Next Release)
- Secure key generation
- Status and logs commands in CLI
- Real-time monitoring in web UI
- Configuration file support

### Medium Term (3-6 Months)
- Multi-user authentication
- API endpoints for external integrations
- Advanced monitoring and analytics
- Support for additional model formats

### Long Term (6+ Months)
- Enterprise features (audit logs, compliance)
- Plugin system for extensibility
- Mobile app companion

## Upcoming Detailed Features

### On Hold: Model/Hugging Face Enhancement

**Status:** ⏸️ On Hold (Deferred for future releases)

**Goal:**
Expand FaceRunner's model compatibility to support a wider range of Hugging Face models, including transformers, ONNX, TensorFlow, and other formats beyond GGUF/Ollama-compatible models.

**Key Objectives:**
- Integrate Hugging Face's `transformers` library for direct model loading and inference.
- Add support for ONNX and TensorFlow models, allowing users to run models that are not natively supported by Ollama.
- Provide a unified interface in both CLI and web UI for listing, pulling, and running any supported Hugging Face model.
- Enable automatic conversion or optimization (quantization, pruning) for models where possible.
- Allow users to upload custom models and manage them through the FaceRunner UI.
- Display model format, size, and hardware compatibility in the UI.
- Add error handling and feedback for unsupported or failed model loads.

**User Stories:**
- As a user, I want to run any Hugging Face model locally, regardless of format.
- As a user, I want to see which models are compatible with my hardware (CPU/GPU).
- As a user, I want to upload and manage my own custom models.
- As a user, I want to optimize models for faster inference.

**Planned Steps (Deferred):**
1. Research and integrate Hugging Face `transformers` for direct model support.
2. Add ONNX and TensorFlow runtime support.
3. Update CLI and web UI to allow selection and management of all supported model types.
4. Implement model upload and conversion features.
5. Add UI elements for model details, compatibility, and optimization options.
6. Test with a variety of models and hardware setups.

---

This feature is currently on hold and will be revisited in a future release based on user demand and project priorities.
