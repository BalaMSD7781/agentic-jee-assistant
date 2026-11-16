"""Local-only demo launcher. Does not use Render or modify cloud settings."""
import os
from pathlib import Path
import subprocess
import sys
import socket
import threading
import time
import urllib.request
import webbrowser


def find_free_port(start=8501, count=30):
    for port in range(start, start + count):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
            try:
                probe.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    raise RuntimeError("No free local demo port found between 8501 and 8530. Close an old demo window and retry.")


def open_when_ready(port, process):
    url = f"http://127.0.0.1:{port}"
    for _ in range(60):
        if process.poll() is not None:
            return
        try:
            with urllib.request.urlopen(url + "/_stcore/health", timeout=1) as response:
                if response.status == 200:
                    webbrowser.open(url)
                    return
        except (OSError, ValueError):
            pass
        time.sleep(.5)

if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    os.chdir(root)
    env = os.environ.copy()
    env.update(JEE_LOCAL_ONLY="1", JEE_API_URL="", JEE_HISTORY_MODE="session",
               CREWAI_TRACING_ENABLED="false", OTEL_SDK_DISABLED="true",
               LITELLM_LOCAL_MODEL_COST_MAP="true", PYTHONUTF8="1")
    try:
        port = find_free_port()
    except RuntimeError as exc:
        print(str(exc), flush=True)
        raise SystemExit(1)
    if port != 8501:
        print(f"Port 8501 is busy; using free port {port}. Existing apps are left running.", flush=True)
    print(f"Local JEE demo: http://localhost:{port} (keep this window open)", flush=True)
    process = subprocess.Popen([sys.executable, "-m", "streamlit", "run", str(root / "app.py"),
        "--server.address=127.0.0.1", f"--server.port={port}", "--server.headless=true"], env=env)
    threading.Thread(target=open_when_ready, args=(port, process), daemon=True).start()
    try:
        raise SystemExit(process.wait())
    except KeyboardInterrupt:
        process.terminate()
        process.wait()
