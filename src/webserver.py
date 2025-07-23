import os
import signal
import subprocess
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

WATCH_PATHS = [
    Path(__file__).parent / "templates",          # default templates
    Path(__file__).parent / "assets",             # default assets
    Path(__file__).parent.parent / "assets",      # custom assets
    Path(__file__).parent / "data.json",          # default data
    Path(__file__).parent.parent / "data.json",   # custom data
    Path(__file__).parent / "routes.json",        # default routes
    Path(__file__).parent.parent / "routes.json"  # custom routes
]


class ReloadHandler(FileSystemEventHandler):
    def __init__(self, restart_callback):
        self.restart_callback = restart_callback

    def on_any_event(self, event):
        if not event.is_directory:
            print(f"🔄 Change detected: {event.src_path}")
            self.restart_callback()


class ServerManager:
    def __init__(self):
        self.process = None

    def start(self):
        print("🚀 Starting server...")
        self.process = subprocess.Popen(["python", "server.py"])

    def stop(self):
        if self.process:
            print("🛑 Stopping server...")
            self.process.send_signal(signal.SIGINT)
            self.process.wait()

    def restart(self):
        self.stop()
        self.start()


if __name__ == "__main__":
    server = ServerManager()
    server.start()

    event_handler = ReloadHandler(server.restart)
    observer = Observer()

    for path in WATCH_PATHS:
        observer.schedule(event_handler, str(path), recursive=True)

    observer.start()
    print("👀 Watching for changes...")

    try:
        while True:
            pass
    except KeyboardInterrupt:
        observer.stop()
        server.stop()

    observer.join()
