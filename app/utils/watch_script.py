import subprocess
import time
from watchdog.observers.polling import PollingObserver as Observer
from watchdog.events import FileSystemEventHandler

# command that starts streamlit
STREAMLIT_CMD = [
    "streamlit",
    "run",
    "app.py",
    "--server.port=8051",
    "--server.address=0.0.0.0"
]

path_to_watch = "/home/streamlit-user/.streamlit"


# StreamlitReloader class is responsible for the start/restart of Streamlit
class StreamlitReloader(FileSystemEventHandler):

    # class' instance starts Streamlit immediately
    def __init__(self):
        self.process = subprocess.Popen(STREAMLIT_CMD)
        print("Streamlit started with PID:", self.process.pid)

    # restarts Streamlit
    def restart_streamlit(self):
        try:
            self.process.terminate()
            self.process.wait(timeout=5)
        except Exception:
            print("Failed to terminate Streamlit, killing process...")
            self.process.kill()
        time.sleep(1)
        self.process = subprocess.Popen(STREAMLIT_CMD)
        print("Streamlit started with PID:", self.process.pid)

    # calls restart_streamlit if a config.toml configuration occurs
    def on_modified(self, event):
        print(f"Detected change in: {event.src_path}")
        if event.src_path.endswith("config.toml"):
            self.restart_streamlit()


# script starts streamlit and restarts it whenever
# a .streamlit/config.toml change is observed
if __name__ == "__main__":
    event_handler = StreamlitReloader()
    observer = Observer()
    observer.schedule(event_handler, path=path_to_watch, recursive=True)
    observer.start()
    print("Watching .streamlit/config.toml for changes...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        event_handler.process.terminate()
    observer.join()
