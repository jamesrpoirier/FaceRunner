import requests

def create_model_browser_ui():
    """Create the Model Browser UI section for browsing available models from Ollama."""
    st.title("📋 Model Browser")
    st.markdown("Browse available models from Ollama. Search and pull models directly.")

    # Fetch models from the community-maintained Ollama models list
    try:
        response = requests.get("https://ollama-models.zwz.workers.dev/")
        if response.status_code == 200:
            models = response.json()
        else:
            st.error("Failed to fetch models from Ollama community list.")
            models = []
    except Exception as e:
        st.error(f"Error fetching models: {e}")
        models = []

    # Search/filter box
    search = st.text_input("Search models", "")
    filtered_models = [m for m in models if search.lower() in m.get("name", "").lower()]

    # Parameter size options for popular models
    PARAM_SIZES = {
        "llama3.1": ["8b", "70b", "405b"],
        "llama3": ["8b", "70b", "405b"],
        "codellama": ["7b", "13b", "34b"],
        "mistral": ["7b", "8x7b"],
        "phi3": ["3.8b", "14b"],
        "gemma": ["2b", "7b"],
        "gemma2": ["2b", "9b", "27b"],
        "wizardlm2": ["8x22b"],
        "mixtral": ["8x7b"],
        # Add more as needed
    }

    # Estimated filesize (GB) for common models and sizes
    ESTIMATED_SIZE_GB = {
        "llama3.1:8b": 4.5,
        "llama3.1:70b": 40,
        "llama3.1:405b": 220,
        "llama3:8b": 4.5,
        "llama3:70b": 40,
        "llama3:405b": 220,
        "codellama:7b": 4.5,
        "codellama:13b": 8,
        "codellama:34b": 22,
        "mistral:7b": 4.5,
        "mistral:8x7b": 32,
        "phi3:3.8b": 2.2,
        "phi3:14b": 8.5,
        "gemma:2b": 1.2,
        "gemma:7b": 4.5,
        "gemma2:2b": 1.2,
        "gemma2:9b": 5.5,
        "gemma2:27b": 16.0,
        "wizardlm2:8x22b": 48.0,
        "mixtral:8x7b": 32.0,
        # Add more as needed
    }

    if filtered_models:
        for model in filtered_models:
            model_name = model.get('name', '')
            st.markdown(f"**{model_name}**")
            st.write(model.get('description', ''))

            base_name = model_name.split(':')[0]
            sizes = PARAM_SIZES.get(base_name, None)
            if sizes:
                size = st.selectbox(
                    f"Select parameter size for {model_name}",
                    sizes,
                    key=f"size_{model_name}"
                )
                full_model_name = f"{base_name}:{size}"
                est_size = ESTIMATED_SIZE_GB.get(full_model_name)
                size_str = f"{size} ({est_size:.1f} GB)" if est_size else size
                st.caption(f"Parameter size: {size_str}")
            else:
                full_model_name = model_name
                est_size = ESTIMATED_SIZE_GB.get(full_model_name)
                if ':' in model_name:
                    size_str = model_name.split(':')[1]
                else:
                    size_str = "default"
                if est_size:
                    st.caption(f"Parameter size: {size_str} ({est_size:.1f} GB)")
                else:
                    st.caption(f"Parameter size: {size_str}")

            if st.button(f"Pull {full_model_name}", key=f"pull_{model_name}"):
                from ollama_utils import pull_model
                with st.spinner(f"Pulling {full_model_name}..."):
                    msg = pull_model(full_model_name)
                    if "successfully" in msg:
                        st.success(msg)
                    else:
                        st.error(msg)
            st.markdown("---")


def log_viewer_ui():
    """Streamlit UI for viewing and filtering service logs."""
    st.header("Log Viewer")
    import os
    log_files = {
        "FaceRunner": os.path.expanduser("~/.facerunner/logs/facerunner.log"),
        "Ollama": os.path.expanduser("~/.facerunner/logs/ollama.log"),
        "Open WebUI": os.path.expanduser("~/.facerunner/logs/openwebui.log")
    }
    service = st.selectbox("Select Service", list(log_files.keys()))
    level = st.selectbox("Log Level", ["ALL", "INFO", "WARNING", "ERROR"])
    search = st.text_input("Search logs")
    log_path = log_files[service]
    level_filter = None if level == "ALL" else level
    from system_utils import read_service_logs
    logs = read_service_logs(log_path, level=level_filter, search=search)
    st.text_area("Logs", "\n".join(logs), height=400)
"""
FaceRunner UI Components - Streamlit UI components and helpers.
"""

import streamlit as st
import time
import threading

def create_system_monitor_sidebar():
    """Create live-updating system monitor in sidebar."""
    from system_utils import get_gpu_info, get_system_load
    import time

    gpu_msg, gpu_count, gpu_types = get_gpu_info()

    # Create placeholders for the bars
    cpu_placeholder = st.sidebar.empty()
    mem_placeholder = st.sidebar.empty()
    gpu_placeholder = st.sidebar.empty()

    # Get initial values
    cpu, mem, gpu_load = get_system_load()

    # Display initial bars
    cpu_placeholder.markdown(f"CPU: <div style='background:#eee;width:100%;height:10px;border-radius:5px;'><div style='background:#4caf50;width:{cpu}%;height:10px;border-radius:5px;'></div></div><span style='font-size:0.9em'>{cpu:.1f}%</span>", unsafe_allow_html=True)
    mem_placeholder.markdown(f"Memory: <div style='background:#eee;width:100%;height:10px;border-radius:5px;'><div style='background:#2196f3;width:{mem}%;height:10px;border-radius:5px;'></div></div><span style='font-size:0.9em'>{mem:.1f}%</span>", unsafe_allow_html=True)
    if gpu_load is not None:
        gpu_placeholder.markdown(f"GPU: <div style='background:#eee;width:100%;height:10px;border-radius:5px;'><div style='background:#ff9800;width:{gpu_load}%;height:10px;border-radius:5px;'></div></div><span style='font-size:0.9em'>{gpu_load}%</span>", unsafe_allow_html=True)
    else:
        gpu_placeholder.markdown(f"GPU: <span style='font-size:0.9em'>N/A</span>", unsafe_allow_html=True)

    # Store placeholders in session state for updates
    if 'system_monitor_placeholders' not in st.session_state:
        st.session_state['system_monitor_placeholders'] = {
            'cpu': cpu_placeholder,
            'mem': mem_placeholder,
            'gpu': gpu_placeholder,
            'last_update': time.time()
        }

    # Auto-refresh every 30 seconds
    current_time = time.time()
    if 'system_monitor_placeholders' in st.session_state:
        last_update = st.session_state['system_monitor_placeholders'].get('last_update', 0)
        if current_time - last_update > 30:  # 30 seconds
            update_system_monitor()
            st.session_state['system_monitor_placeholders']['last_update'] = current_time

def update_system_monitor():
    """Update the system monitor bars with current values."""
    from system_utils import get_system_load
    import time

    if 'system_monitor_placeholders' in st.session_state:
        cpu, mem, gpu_load = get_system_load()

        placeholders = st.session_state['system_monitor_placeholders']
        placeholders['cpu'].markdown(f"CPU: <div style='background:#eee;width:100%;height:10px;border-radius:5px;'><div style='background:#4caf50;width:{cpu}%;height:10px;border-radius:5px;'></div></div><span style='font-size:0.9em'>{cpu:.1f}%</span>", unsafe_allow_html=True)
        placeholders['mem'].markdown(f"Memory: <div style='background:#eee;width:100%;height:10px;border-radius:5px;'><div style='background:#2196f3;width:{mem}%;height:10px;border-radius:5px;'></div></div><span style='font-size:0.9em'>{mem:.1f}%</span>", unsafe_allow_html=True)
        if gpu_load is not None:
            placeholders['gpu'].markdown(f"GPU: <div style='background:#eee;width:100%;height:10px;border-radius:5px;'><div style='background:#ff9800;width:{gpu_load}%;height:10px;border-radius:5px;'></div></div><span style='font-size:0.9em'>{gpu_load}%</span>", unsafe_allow_html=True)
        else:
            placeholders['gpu'].markdown(f"GPU: <span style='font-size:0.9em'>N/A</span>", unsafe_allow_html=True)

        # Update last update timestamp
        st.session_state['system_monitor_placeholders']['last_update'] = time.time()

def create_model_management_ui():
    """Create the model management UI section."""
    from ollama_utils import pull_model, list_installed_models, remove_model

    st.title("🤖 Model Management")
    st.markdown("Manage your Ollama and Open WebUI models below.")

    model = st.text_input(
        "Ollama Model to Pull",
        placeholder="e.g., llama3.1, codellama:7b, mistral:7b",
        help="Enter the name of a model from https://ollama.com/search. Only Ollama-compatible models are supported."
    )
    if st.button("📥 Pull Model", type="primary") and model:
        with st.spinner(f"Downloading {model}... This may take several minutes..."):
            msg = pull_model(model.strip())
            if "successfully" in msg:
                st.success(msg)
                st.balloons()
            else:
                st.error(msg)

    st.markdown("---")
    st.subheader("📦 Installed Models")
    if st.button("🔄 Refresh Model List"):
        st.rerun()

    models_output = list_installed_models()
    if "Error" in models_output:
        st.error(models_output)
    else:
        lines = models_output.strip().split('\n')
        if len(lines) > 1:
            header = lines[0].split()
            # Try to find the size column index
            size_idx = None
            for i, col in enumerate(header):
                if col.lower() in ["size", "disk", "space"]:
                    size_idx = i
                    break
            if size_idx is None:
                size_idx = 2  # Default to third column

            model_data = []
            for line in lines[1:]:
                if line.strip():
                    parts = line.split()
                    model_name = parts[0]
                    model_size = parts[size_idx] if len(parts) > size_idx else "Unknown"
                    model_data.append({"Model": model_name, "Size": model_size})

            if model_data:
                st.markdown("### Installed Models")

                # Sorting state
                sort_col = st.session_state.get("sort_col", "Model")
                sort_asc = st.session_state.get("sort_asc", True)

                def parse_size(s):
                    s = s.strip()
                    try:
                        import re
                        match = re.match(r"([\d\.]+)\s*([a-zA-Z]+)?", s)
                        if match:
                            value, unit = match.groups()
                            value = float(value)
                            if unit and unit.lower() == "mb":
                                return value / 1024  # Convert MB to GB for sorting
                            # Default to GB if unit is missing or is GB
                            return value
                        else:
                            return float(s)
                    except:
                        return 0

                # Sorting logic
                if sort_col == "Model":
                    model_data = sorted(model_data, key=lambda x: x["Model"].lower(), reverse=not sort_asc)
                elif sort_col == "Size":
                    model_data = sorted(model_data, key=lambda x: parse_size(x["Size"]), reverse=not sort_asc)

                # Header with sort buttons
                header_cols = st.columns([3, 2, 1])
                if header_cols[0].button(("Model " + ("↑" if sort_col=="Model" and sort_asc else "↓")), key="sort_model"):
                    st.session_state["sort_col"] = "Model"
                    st.session_state["sort_asc"] = not (sort_col=="Model" and sort_asc)
                    st.rerun()
                if header_cols[1].button(("Size " + ("↑" if sort_col=="Size" and sort_asc else "↓")), key="sort_size"):
                    st.session_state["sort_col"] = "Size"
                    st.session_state["sort_asc"] = not (sort_col=="Size" and sort_asc)
                    st.rerun()
                header_cols[2].write("Remove")

                # Model rows
                for row in model_data:
                    cols = st.columns([3, 2, 1])
                    cols[0].write(f"**{row['Model']}**")
                    size_str = row['Size']
                    import re
                    match = re.match(r"([\d\.]+)\s*([a-zA-Z]+)?", size_str)
                    if match:
                        value, unit = match.groups()
                        if unit and unit.lower() == "mb":
                            display_size = f"{float(value)/1024:.2f} GB"
                        else:
                            display_size = f"{value} GB"
                    else:
                        display_size = f"{size_str} GB"
                    cols[1].write(display_size)
                    if cols[2].button("🗑️", key=f"remove_{row['Model']}"):
                        with st.spinner(f"Removing {row['Model']}..."):
                            remove_msg = remove_model(row['Model'])
                            if "successfully" in remove_msg:
                                st.success(remove_msg)
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error(remove_msg)
            else:
                st.info("No models installed yet. Pull a model above to get started!")
        else:
            st.info("No models installed yet. Pull a model above to get started!")

def create_popular_models_ui():
    """Create the popular models UI section."""
    from ollama_utils import pull_model

    st.title("💡 Popular Models")
    st.markdown("**Try these popular Ollama models:**")

    # List of popular models
    popular_models = [
        {"name": "llama3.1", "desc": "Meta's Llama 3.1 (8B parameters)"},
        {"name": "llama3.1:70b", "desc": "Meta's Llama 3.1 (70B parameters)"},
        {"name": "codellama:7b", "desc": "Code generation model"},
        {"name": "mistral:7b", "desc": "Fast and efficient model"},
        {"name": "phi3:14b", "desc": "Microsoft's Phi-3 model"},
    ]

    for model in popular_models:
        col1, col2 = st.columns([2, 1])
        col1.markdown(f"**{model['name']}** - {model['desc']}")
        if col2.button(f"Install", key=f"install_{model['name']}"):
            with st.spinner(f"Pulling {model['name']}..."):
                msg = pull_model(model['name'])
                if "successfully" in msg:
                    st.success(msg)
                else:
                    st.error(msg)

    with st.expander("🔧 Ollama Model Info"):
        st.markdown("""
        **Supported Models:**
        FaceRunner only supports models published for Ollama. See [Ollama Model Search](https://ollama.com/search) for available models.

        **Model Size Options:**
        - `:7b` - 7 billion parameters (good balance)
        - `:13b` - 13 billion parameters (better quality)
        - `:70b` - 70 billion parameters (best quality, slower)

        **Specialized Models:**
        - `codellama` - Code generation and understanding
        - `mathstral` - Mathematical reasoning
        - `dolphin-mistral` - Uncensored conversations
        """)

def create_vscode_integration_ui():
    """Create the VS Code integration UI section."""
    from network_utils import integrate_vscode
    from system_utils import get_host_ip

    st.title("🔗 VS Code Integration")
    # Always show the local ethernet adapter IP for integration
    ip = get_host_ip()
    st.text_input("Host IP for VS Code integration", value=ip, disabled=True)
    if st.button("Generate VS Code Config") and ip:
        config_yaml = integrate_vscode(ip)
        st.session_state["vscode_config_yaml"] = config_yaml
        st.session_state["show_vscode_config_modal"] = True

    # Always show the config block if YAML is present in session state
    if st.session_state.get("vscode_config_yaml"):
        st.markdown("### VS Code Continue config.yaml")
        st.code(st.session_state["vscode_config_yaml"], language="yaml")
        st.info("Copy and paste this into ~/.continue/config.yaml, or click 'Auto Apply' to write it directly.")

        col1, col2, col3 = st.columns(3)
        if col1.button("Auto Apply to ~/.continue/config.yaml"):
            try:
                config_dir = Path.home() / ".continue"
                config_dir.mkdir(exist_ok=True)
                config_file = config_dir / "config.yaml"
                with open(config_file, 'w') as f:
                    f.write(st.session_state["vscode_config_yaml"])
                st.success(f"VS Code config written to {config_file}. Restart VS Code and use the Continue extension.")
            except Exception as e:
                st.error(f"Error writing config file: {e}")

        if col2.button("Save to Windows User Profile"):
            try:
                import os
                win_profile = os.environ.get("USERPROFILE")
                if win_profile:
                    config_dir = Path(win_profile) / ".continue"
                    config_dir.mkdir(exist_ok=True)
                    config_file = config_dir / "config.yaml"
                    with open(config_file, 'w') as f:
                        f.write(st.session_state["vscode_config_yaml"])
                    st.success(f"VS Code config written to {config_file} in Windows user profile.")
                else:
                    st.error("Could not determine Windows user profile directory.")
            except Exception as e:
                st.error(f"Error writing config file to Windows user profile: {e}")

        # Download button for config.yaml
        st.download_button(
            label="Download config.yaml",
            data=st.session_state["vscode_config_yaml"],
            file_name="config.yaml",
            mime="text/yaml"
        )

def create_settings_ui():
    """Create the settings UI section."""
    from system_utils import get_os, get_host_ip, get_gpu_info

    st.title("⚙️ Settings & Info")
    st.markdown("Configure FaceRunner, view logs, and more coming soon.")

    st.subheader("System Information")
    st.write(f"**Host IP:** {get_host_ip()}")
    st.write(f"**Operating System:** {get_os().title()}")
    gpu_msg, gpu_count, gpu_types = get_gpu_info()
    st.write(f"**GPU Info:** {gpu_msg}")
    st.markdown("---")
