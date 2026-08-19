import watchdog.observers
from ApacheBeam.config import LANDING_DIR
from Automation.LogicAutomation import Handler

event_handler = Handler()
observer = watchdog.observers.Observer()
observer.schedule(event_handler,LANDING_DIR, recursive=False)  # Path of Read Data (Salma)
observer.start()
observer.join()