import shutil
import time
import watchdog.events
import watchdog.observers
class Handler (watchdog.events.PatternMatchingEventHandler):
    def __init__(self):
        watchdog.events.PatternMatchingEventHandler.__init__(self,patterns=['*.csv'],ignore_patterns= None , ignore_directories=  True, case_sensitive=False)

    def on_created(self, event):
        print(f"File was created at {event.src_path}")

        
        while True:
            try:
                shutil.move(event.src_path,'D:/Nemo/ApacheBeam')
                print(f"File was moved at D:/Nemo/ApacheBeam")
                time.sleep(3)
                break
            except PermissionError:
                print('please wait this operation take time')
            except Exception as e:
                print(f'There is anthor error occured {e}')
                break

event_handler = Handler()
observer = watchdog.observers.Observer()
observer.schedule(event_handler,'D:/', recursive=False)  # Path of Read Data (Salma)
observer.start()
observer.join()