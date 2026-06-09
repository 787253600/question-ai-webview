import threading
import time

import uvicorn
import webview

HOST = "127.0.0.1"
PORT = 5130
URL = f"http://{HOST}:{PORT}/"


def run_server() -> None:
    uvicorn.run("main:app", host=HOST, port=PORT, log_level="info")


def main() -> None:
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    time.sleep(1)
    webview.create_window("AI 题库助手", URL, width=1180, height=820, min_size=(960, 680))
    webview.start()


if __name__ == "__main__":
    main()
