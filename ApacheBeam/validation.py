import apache_beam as beam
from ApacheBeam.config import TAG_CLEAN, TAG_DEAD_LETTER

class ValidateAndCleanF1DoFn(beam.DoFn):
    def process(self, element):
        try:
            fields = [f.strip() for f in element.split(',')]
            
            if fields[0] == 'Date' or fields[1] == 'RPM':
                return

            if len(fields) < 11:
                raise ValueError(f"Incomplete record row, expected 11 fields but got {len(fields)}")

            date_val, raw_rpm, raw_speed, raw_ngear, raw_throttle, brake_val, drs_val, source_val, time_val, session_time, driver_val = fields[:11]

            if not driver_val or driver_val.lower() == 'nan':
                raise ValueError("Missing critical field: Driver ID")

            rpm = float(raw_rpm)
            if rpm < 0:
                raise ValueError(f"Invalid RPM value: {rpm}")

            speed = float(raw_speed)
            if speed < 0:
                raise ValueError(f"Invalid Speed value: {speed}")

            ngear = int(raw_ngear)
            if not (0 <= ngear <= 8):
                raise ValueError(f"Invalid nGear range: {ngear}")

            throttle = float(raw_throttle)
            if not (0 <= throttle <= 100):
                raise ValueError(f"Throttle out of range [0-100]: {throttle}")

            drs = int(drs_val)
            if drs not in [0, 1]:
                raise ValueError(f"Invalid DRS flag: {drs}")

            clean_data = {
                'date': date_val, 'rpm': rpm, 'speed': speed, 'ngear': ngear,
                'throttle': throttle, 'brake': brake_val.lower() == 'true',
                'drs': drs, 'source': source_val, 'time': time_val,
                'session_time': session_time, 'driver': float(driver_val)
            }
            
            yield beam.pvalue.TaggedOutput(TAG_CLEAN, clean_data)

        except Exception as error:
            error_metadata = {
                'raw_line': element,
                'error_reason': str(error)
            }
            yield beam.pvalue.TaggedOutput(TAG_DEAD_LETTER, error_metadata)