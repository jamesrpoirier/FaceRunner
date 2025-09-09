"""
FaceRunner Web UI - Main application entry point.
"""

import streamlit as st
import time

from system_utils import get_gpu_info, get_host_ip
from network_utils import verify_accessibility, configure_network
from ui_components import (
    create_system_monitor_sidebar,
    create_model_management_ui,
    create_popular_models_ui,
    create_vscode_integration_ui,
    create_settings_ui,
    update_system_monitor,
    create_model_browser_ui
)

OLLAMA_PORT = 11434
WEBUI_PORT = 8080

def main():
    # Custom CSS to reduce top margin and bring sidebar closer to the top
    st.markdown("""
        <style>
        /* Remove top padding from main and sidebar containers */
        .css-18e3th9, .css-1d391kg, .css-1v0mbdj, .css-1dp5vir {
            padding-top: 0rem !important;
        }
        /* Hide sidebar collapse arrow */
        [data-testid="collapsedControl"] {
            display: none !important;
        }
        /* Remove extra margin above sidebar title */
        .css-1v0mbdj > div:first-child {
            margin-top: 0 !important;
        }
        </style>
    """, unsafe_allow_html=True)
    st.set_page_config(page_title="FaceRunner Web UI", layout="wide", page_icon="🤖")

    # Initialize session state
    if "sort_col" not in st.session_state:
        st.session_state["sort_col"] = "Model"
    if "sort_asc" not in st.session_state:
        st.session_state["sort_asc"] = True
    if "show_vscode_config_modal" not in st.session_state:
        st.session_state["show_vscode_config_modal"] = False

    # Get system info
    gpu_msg, gpu_count, gpu_types = get_gpu_info()
    local_ip = get_host_ip()

    # Concise service status block in sidebar above resource info
    with st.sidebar:
        status_msgs = verify_accessibility()
        st.markdown("**Service Status**")
        ollama_ok = any("Ollama is accessible locally" in msg for msg in status_msgs)
        webui_local_ok = any("Open WebUI is accessible locally" in msg for msg in status_msgs)
        button_style = "display:block;padding:0.5em 1em;margin:0.2em 0;background:#28a745;color:white;border-radius:6px;text-align:center;text-decoration:none;font-weight:600;box-shadow:0 1px 2px rgba(0,0,0,0.04);"
        import base64
        def svg_to_base64(path):
            with open(path, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
        ollama_icon_b64 = svg_to_base64("src/assets/ollama.svg")
        openwebui_icon_b64 = svg_to_base64("src/assets/openwebui.svg")
        # Show Ollama status only as a styled block, not a clickable button to avoid duplicate
        if ollama_ok:
            st.markdown(f"<div style='{button_style}'><img src='data:image/svg+xml;base64,{ollama_icon_b64}' alt='Ollama' style='height:1.5em;vertical-align:middle;margin-right:0.5em;'> Ollama</div>", unsafe_allow_html=True)
        else:
            st.error("Ollama is not running")
        if webui_local_ok:
            st.markdown(f"<a href='http://localhost:{WEBUI_PORT}' target='_blank' style='{button_style}'><img src='data:image/svg+xml;base64,{openwebui_icon_b64}' alt='Open WebUI' style='height:1.5em;vertical-align:middle;margin-right:0.5em;'> Open WebUI</a>", unsafe_allow_html=True)
        else:
            st.error("Open WebUI is not running")
        st.markdown("---")

        # Sidebar with live system load bar graphs and Ollama mode toggle
        st.sidebar.title("FaceRunner")
        # Ollama mode is now always local
        st.session_state["ollama_mode"] = "Local"
        # Create system monitor
        create_system_monitor_sidebar()
        st.sidebar.markdown("---")

    # Add refresh button for system monitor
    if st.sidebar.button("🔄 Refresh System Monitor"):
        update_system_monitor()
        st.sidebar.success("System monitor updated!")

    # Modern tab-based navigation
    tab_labels = [
        "🤖 Model Management",
        "📋 Model Browser",
        "🔗 VS Code Integration",
        "🛠️ Setup & Management",
        "⚙️ Settings"
    ]
    if "active_tab" not in st.session_state:
        st.session_state["active_tab"] = 0
    tab1, tab2, tab3, tab4, tab5 = st.tabs(tab_labels)
    active_tab = st.session_state["active_tab"]

    with tab1:
        create_model_management_ui()

    with tab2:
        create_popular_models_ui()
        create_model_browser_ui()

    with tab3:
        create_vscode_integration_ui()

    with tab4:
        st.title("🛠️ Setup & Management")
        st.markdown("Use this page to setup and manage FaceRunner services locally.")
        st.markdown("---")
        st.subheader("Service Status")
        if st.button("🔍 Check Service Status"):
            with st.spinner("Checking service status..."):
                status_msgs = verify_accessibility()
            st.success("FaceRunner Web UI is running.")
            ollama_ok = any("Ollama is accessible locally" in msg for msg in status_msgs)
            webui_ok = any("Open WebUI is accessible locally" in msg for msg in status_msgs)
            for msg in status_msgs:
                st.info(msg)
            if not ollama_ok:
                st.warning("Ollama is not running.")
            if not webui_ok:
                st.warning("Open WebUI is not running.")
            if not (ollama_ok or webui_ok):
                st.info("To start FaceRunner services, please run `facerunner setup` in your terminal.")
        st.markdown("**Ollama Model Management** is available in the Model Management tab.")

    with tab5:
        create_settings_ui()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"An error occurred: {e}")
        import traceback
        st.text(traceback.format_exc())