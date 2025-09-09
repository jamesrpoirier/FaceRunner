"""
FaceRunner System Utilities - System monitoring and basic utilities.
"""

import subprocess
import platform
import socket
from pathlib import Path

OLLAMA_PORT = 11434
WEBUI_PORT = 8080

def get_gpu_info():
    """Utility to get GPU info (type and count)"""
    try:
        result = subprocess.run([
            "nvidia-smi", "--query-gpu=name,count", "--format=csv,noheader"
        ], capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            gpus = [line.split(',')[0].strip() for line in lines if line.strip()]
            count = len(gpus)
            if count == 0:
                return "No GPU detected. Running on CPU.", 0, []
            return f"{count} GPU(s) detected: {', '.join(gpus)}", count, gpus
        else:
            return "No GPU detected (nvidia-smi not available). Running on CPU.", 0, []
    except Exception:
        return "No GPU detected (nvidia-smi error). Running on CPU.", 0, []

def get_system_load():
    """Get system load information"""
    try:
        import psutil
        cpu = psutil.cpu_percent(interval=0.5)
        mem = psutil.virtual_memory().percent
        gpu_load = None
        try:
            result = subprocess.run(["nvidia-smi", "--query-gpu=utilization.gpu", "--format=csv,noheader,nounits"], capture_output=True, text=True)
            if result.returncode == 0:
                gpu_load = result.stdout.strip().split('\n')[0]
        except Exception:
            gpu_load = None
        return cpu, mem, gpu_load
    except ImportError:
        return 0, 0, None

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

