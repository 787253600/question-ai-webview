import threading
import time
from urllib.request import urlopen

import uvicorn
import webview

HOST = "127.0.0.1"
PORT = 5130
URL = f"http://{HOST}:{PORT}/"


def run_server() -> None:
    uvicorn.run("main:app", host=HOST, port=PORT, log_level="info")


def wait_for_server(timeout_seconds: float = 10, interval_seconds: float = 0.2) -> bool:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        try:
            urlopen(URL, timeout=1)
            return True
        except OSError:
            time.sleep(interval_seconds)
    return False


def main() -> None:
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    wait_for_server()
    webview.create_window("AI 题库助手", URL, width=1180, height=820, min_size=(960, 680))
    webview.start()


if __name__ == "__main__":
    main()
