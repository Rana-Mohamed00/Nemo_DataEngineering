import shutil
import time
import watchdog.events
import watchdog.observers

from Automation.Landing import Handler
event_handler = Handler()
observer = watchdog.observers.Observer()
observer.schedule(event_handler,'D:/', recursive=False)  # Path of Read Data (Salma)
observer.start()
observer.join()