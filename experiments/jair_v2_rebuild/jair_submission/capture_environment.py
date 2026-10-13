"""Capture the exact final Colab execution environment for the JAIR checklist."""

import json
import os
import platform
import subprocess
import sys
from pathlib import Path

def sh(cmd):
    try:
        return subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.STDOUT).strip()
    except Exception as e:
        return f"unavailable: {e}"

def pkg_version(name):
    try:
        from importlib.metadata import version
        return version(name)
    except Exception:
        return "unavailable"

def main():
    out = {
        "python": sys.version.replace("\n", " "),
        "platform": platform.platform(),
        "system": platform.system(),
        "release": platform.release(),
        "machine": platform.machine(),
        "cpu_model": sh("lscpu | grep 'Model name' | head -1 | sed 's/Model name:[[:space:]]*//'"),
        "cpu_count_logical": os.cpu_count(),
        "ram_total": sh("free -h | awk '/Mem:/ {print $2}'"),
        "gpu": sh("nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader"),
        "cuda_nvidia_smi": sh("nvidia-smi | grep 'CUDA Version' | head -1"),
        "torch": pkg_version("torch"),
        "transformers": pkg_version("transformers"),
        "datasets": pkg_version("datasets"),
        "accelerate": pkg_version("accelerate"),
        "huggingface_hub": pkg_version("huggingface-hub"),
        "scipy": pkg_version("scipy"),
        "numpy": pkg_version("numpy"),
        "pandas": pkg_version("pandas"),
        "fsspec": pkg_version("fsspec"),
    }
    try:
        import torch
        out["torch_cuda_available"] = torch.cuda.is_available()
        out["torch_cuda_version"] = torch.version.cuda
        if torch.cuda.is_available():
            out["torch_gpu_name"] = torch.cuda.get_device_name(0)
            p = torch.cuda.get_device_properties(0)
            out["torch_gpu_total_memory_bytes"] = p.total_memory
    except Exception as e:
        out["torch_runtime_error"] = str(e)

    text = json.dumps(out, indent=2)
    print(text)

if __name__ == "__main__":
    main()
