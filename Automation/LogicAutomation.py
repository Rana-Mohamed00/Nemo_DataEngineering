import time
import os
import watchdog.events
from ApacheBeam.pipeline import run_pipeline
class Handler (watchdog.events.PatternMatchingEventHandler):
    def __init__(self):
        watchdog.events.PatternMatchingEventHandler.__init__(self,patterns=['*.csv'],ignore_patterns= None , ignore_directories=  True, case_sensitive=False)

    def on_created(self, event):
        print(f"File was created at {event.src_path}")
        run_pipeline(event.src_path)
        time.sleep(3)             #Creating file takes some time  
        print('Function of run Pipeline Works Successfully')
        os.remove(event.src_path)
        print('Dirty File was deleted successfuly')
