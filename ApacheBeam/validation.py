import datetime
import apache_beam as beam
from ApacheBeam.config import TAG_CLEAN, TAG_DEAD_LETTER

class ValidateAndCleanF1DoFn(beam.DoFn):
    def process(self, element):
        try:
            fields = [f.strip() for f in element.split(',')]
            
            if fields[0].lower() in ['date', 'datetime'] or fields[1].lower() in ['rpm', 'speed']:
                return

            if len(fields) < 11:
                raise ValueError("Incomplete record row")

            date_val, raw_rpm, raw_speed, raw_ngear, raw_throttle, brake_val, drs_val, source_val, time_val, session_time, driver_val = fields[:11]

            if not driver_val or driver_val.lower() in ['nan', 'null', 'none', ''] or not date_val or not time_val or not session_time:
                raise ValueError("Missing critical fields (Driver or Timestamps)")

            for fmt in ('%Y-%m-%d %H:%M:%S.%f', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d'):
                try:
                    datetime.datetime.strptime(date_val, fmt)
                    break
                except ValueError:
                    pass
            else:
                raise ValueError(f"Invalid Date format: {date_val}")

            driver = float(driver_val)
            rpm = float(raw_rpm)
            speed = float(raw_speed)
            ngear = int(float(raw_ngear))
            throttle = float(raw_throttle)
            drs = int(float(drs_val))

            if not (0.0 <= rpm <= 15000.0) or not (0.0 <= speed <= 360.0) or not (0 <= ngear <= 8) or not (0.0 <= throttle <= 100.0) or not (0 <= drs <= 15):
                raise ValueError("One or more numerical values are out of valid bounds")

            clean_data = {
                'date': date_val, 'rpm': rpm, 'speed': speed, 'ngear': ngear, 
                'throttle': throttle, 'brake': brake_val.lower() in ['true', '1', 't'], 
                'drs': drs, 'source': source_val, 'time': time_val, 
                'session_time': session_time, 'driver': driver
            }
            
            yield beam.pvalue.TaggedOutput(TAG_CLEAN, clean_data)

        except Exception as error:
            yield beam.pvalue.TaggedOutput(TAG_DEAD_LETTER, {'raw_line': element, 'error_reason': str(error)})