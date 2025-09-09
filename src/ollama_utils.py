
def get_active_ollama_task():
    """Return a string describing the current Ollama task, if any."""
    try:
        # Check for running ollama pull/generate processes
        result = subprocess.run(["ps", "-eo", "pid,cmd"], capture_output=True, text=True)
        for line in result.stdout.splitlines():
            if "ollama" in line and ("pull" in line or "generate" in line):
                if "pull" in line:
                    return "Pulling model..."
                elif "generate" in line:
                    return "Generating response..."
        return "Idle"
    except Exception:
        return "Unknown"
"""
FaceRunner Ollama Utilities - Ollama model management functions.
"""

import subprocess
import os
import re
import streamlit as st

OLLAMA_PORT = 11434
WEBUI_PORT = 8080

def parse_model_name(model_input):
    """Parse and convert various model name formats to Ollama format."""
    # Remove any leading/trailing whitespace
    model_input = model_input.strip()

    # Handle full Hugging Face URLs
    if model_input.startswith("https://huggingface.co/"):
        # Extract model name from URL
        match = re.search(r"huggingface\.co/([^/]+/[^/]+)", model_input)
        if match:
            model_name = match.group(1)
        else:
            return model_input, f"Could not parse model name from URL: {model_input}"
    elif "/" in model_input:
        # Handle Hugging Face format like "openai/gpt-oss-20b"
        model_name = model_input
    else:
        # Assume it's already an Ollama format or simple name
        return model_input, None

    # Convert common Hugging Face formats to Ollama formats
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

    # Check for exact matches
    if model_name in conversions:
        ollama_name = conversions[model_name]
        return ollama_name, f"Converted {model_name} → {ollama_name}"

    # Try pattern matching for common formats
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

    # If no conversion found, try the original name
    return model_name, f"No conversion found for {model_name}, trying as-is"

def pull_model(model_input):
    """Pull a model using Ollama."""
    try:
        ollama_model, conversion_msg = parse_model_name(model_input)
        if conversion_msg:
            st.info(conversion_msg)
        result = subprocess.run(["ollama", "pull", ollama_model], capture_output=True, text=True)
        if result.returncode == 0:
            return f"✅ Model {ollama_model} pulled successfully."
        else:
            return f"❌ Error pulling model {ollama_model}: {result.stderr}"
    except subprocess.CalledProcessError as e:
        return f"❌ Error pulling model: {e}"
    except Exception as e:
        return f"❌ Unexpected error: {e}"

def list_installed_models():
    """List all installed Ollama models."""
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return f"Error listing models: {result.stderr}"
    except subprocess.CalledProcessError as e:
        return f"Error listing models: {e}"
    except Exception as e:
        return f"Unexpected error: {e}"

def remove_model(model_name):
    """Remove a model from Ollama."""
    try:
        result = subprocess.run(["ollama", "rm", model_name], capture_output=True, text=True)
        if result.returncode == 0:
            return f"✅ Model {model_name} removed successfully."
        else:
            return f"❌ Error removing model {model_name}: {result.stderr}"
    except subprocess.CalledProcessError as e:
        return f"❌ Error removing model: {e}"
    except Exception as e:
        return f"❌ Unexpected error: {e}"
