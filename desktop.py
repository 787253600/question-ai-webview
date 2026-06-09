import threading
import time
from urllib.request import urlopen

import uvicorn
import webview

from main import read_config

HOST = "127.0.0.1"
DEFAULT_PORT = 5130


def get_port() -> int:
    return int(read_config().get("port", DEFAULT_PORT))


def build_url(port: int) -> str:
    return f"http://{HOST}:{port}/"


def run_server(port: int) -> None:
    uvicorn.run("main:app", host=HOST, port=port, log_level="info")


def wait_for_server(url: str, timeout_seconds: float = 10, interval_seconds: float = 0.2) -> bool:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        try:
            urlopen(url, timeout=1)
            return True
        except OSError:
            time.sleep(interval_seconds)
    return False


def main() -> None:
    port = get_port()
    url = build_url(port)
    server_thread = threading.Thread(target=run_server, args=(port,), daemon=True)
    server_thread.start()
    wait_for_server(url)
    webview.create_window("AI 题库助手", url, width=1180, height=820, min_size=(960, 680))
    webview.start()


if __name__ == "__main__":
    main()
