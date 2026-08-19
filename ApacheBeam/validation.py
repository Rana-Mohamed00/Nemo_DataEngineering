# import datetime
# import apache_beam as beam  
# from ApacheBeam.config import TAG_CLEAN, TAG_DEAD_LETTER

# class ValidateAndCleanF1DoFn(beam.DoFn):
#     def process(self, element):
#         try:
#             fields = [f.strip() for f in element.split(',')]
            
#             if fields[0] == 'Date' or fields[1] == 'RPM':
#                 return

#             if len(fields) < 11:
#                 raise ValueError(f"Incomplete record row, expected 11 fields but got {len(fields)}")

#             date_val, raw_rpm, raw_speed, raw_ngear, raw_throttle, brake_val, drs_val, source_val, time_val, session_time, driver_val = fields[:11]

#             if not driver_val or driver_val.lower() == 'nan':
#                 raise ValueError("Missing critical field: Driver ID")

#             if not date_val or not time_val or not session_time:
#                 raise ValueError("Missing critical timestamp field (Date, Time, or SessionTime)")
            
#             try:
#                 datetime.strptime(date_val, '%Y-%m-%d')
#             except ValueError:
#                 raise ValueError(f"Invalid Date format: {date_val}")

#             rpm = float(raw_rpm)
#             if not (0 <= rpm <= 15000):
#                 raise ValueError(f"Invalid RPM value out of range [0-15000]: {rpm}")

#             speed = float(raw_speed)
#             if not (0 <= speed <= 360):
#                 raise ValueError(f"Invalid Speed value out of range [0-360]: {speed}")

#             ngear = int(raw_ngear)
#             if not (0 <= ngear <= 8):
#                 raise ValueError(f"Invalid nGear range [0-8]: {ngear}")

#             throttle = float(raw_throttle)
#             if not (0.0 <= throttle <= 100.0):
#                 raise ValueError(f"Throttle out of range [0-100]: {throttle}")

#             drs = int(drs_val)
#             if not (0 <= drs <= 15):
#                 raise ValueError(f"Invalid DRS flag out of range [0-15]: {drs}")

#             clean_data = {
#                 'date': date_val,
#                 'rpm': rpm,
#                 'speed': speed,
#                 'ngear': ngear,
#                 'throttle': throttle,
#                 'brake': brake_val.lower() == 'true',
#                 'drs': drs,
#                 'source': source_val,
#                 'time': time_val,
#                 'session_time': session_time,
#                 'driver': float(driver_val)
#             }
            
#             yield beam.pvalue.TaggedOutput(TAG_CLEAN, clean_data)

#         except Exception as error:
#             error_metadata = {
#                 'raw_line': element,
#                 'error_reason': str(error)
#             }
#             yield beam.pvalue.TaggedOutput(TAG_DEAD_LETTER, error_metadata)

import datetime
import apache_beam as beam  
from ApacheBeam.config import TAG_CLEAN, TAG_DEAD_LETTER

class ValidateAndCleanF1DoFn(beam.DoFn):
    def process(self, element):
        try:
            fields = [f.strip() for f in element.split(',')]
            
            # 1. Skip Header
            if fields[0].lower() in ['date', 'datetime'] or fields[1].lower() in ['rpm', 'speed']:
                return

            if len(fields) < 11:
                raise ValueError(f"Incomplete record row, expected 11 fields but got {len(fields)}")

            date_val, raw_rpm, raw_speed, raw_ngear, raw_throttle, brake_val, drs_val, source_val, time_val, session_time, driver_val = fields[:11]

            # 2. Driver Validation (Critical drop on missing/NaN)
            if not driver_val or driver_val.lower() in ['nan', 'null', 'none', '']:
                raise ValueError("Anomaly: Missing or NaN Driver ID (Critical Data Drop)")
            
            try:
                driver = float(driver_val)
            except ValueError:
                raise ValueError(f"Anomaly: Invalid Driver ID format '{driver_val}'")

            # 3. Timestamps Validation
            if not date_val or not time_val or not session_time:
                raise ValueError("Anomaly: Missing critical timestamp field (Date, Time, or SessionTime)")
            
            clean_date = None
            for fmt in ('%Y-%m-%d %H:%M:%S.%f', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d'):
                try:
                    clean_date = datetime.datetime.strptime(date_val, fmt)
                    break
                except ValueError:
                    pass
            
            if not clean_date:
                raise ValueError(f"Anomaly: Invalid Date/Time format '{date_val}'")

            # 4. RPM Validation (0 to 15,000 & Type-Cast check)
            try:
                rpm = float(raw_rpm)
            except ValueError:
                raise ValueError(f"Anomaly: Type-cast error in RPM (String/Sensor Error: '{raw_rpm}')")
            
            if not (0.0 <= rpm <= 15000.0):
                raise ValueError(f"Anomaly: Out of bounds RPM value '{rpm}' [0 - 15000]")

            # 5. Speed Validation (0 to 360 km/h)
            try:
                speed = float(raw_speed)
            except ValueError:
                raise ValueError(f"Anomaly: Type-cast error in Speed '{raw_speed}'")
            
            if speed < 0.0:
                raise ValueError(f"Anomaly: Physically impossible negative Speed '{speed}'")
            if speed > 360.0:
                raise ValueError(f"Anomaly: Out of bounds Speed '{speed}' (> 360 km/h)")

            # 6. nGear Validation (0 to 8)
            try:
                ngear = int(float(raw_ngear))
            except ValueError:
                raise ValueError(f"Anomaly: Type-cast error in nGear '{raw_ngear}'")
            
            if not (0 <= ngear <= 8):
                raise ValueError(f"Anomaly: Fault code or sensor overflow in nGear '{ngear}' (Valid: 0-8)")

            # 7. Throttle Validation (0.0 to 100.0)
            try:
                throttle = float(raw_throttle)
            except ValueError:
                raise ValueError(f"Anomaly: Type-cast error in Throttle '{raw_throttle}'")
            
            if not (0.0 <= throttle <= 100.0):
                raise ValueError(f"Anomaly: Calibration error in Throttle '{throttle}' [0.0 - 100.0]")

            # 8. Brake Validation (Boolean)
            brake = brake_val.lower() in ['true', '1', 't']

            # 9. DRS Validation (0 to 15)
            try:
                drs = int(float(drs_val))
            except ValueError:
                raise ValueError(f"Anomaly: Type-cast error in DRS '{drs_val}'")
            
            if not (0 <= drs <= 15):
                raise ValueError(f"Anomaly: Invalid DRS status code '{drs}' [0 - 15]")

            # Valid Cleaned Data Output
            clean_data = {
                'date': date_val,
                'rpm': rpm,
                'speed': speed,
                'ngear': ngear,
                'throttle': throttle,
                'brake': brake,
                'drs': drs,
                'source': source_val,
                'time': time_val,
                'session_time': session_time,
                'driver': driver
            }
            
            yield beam.pvalue.TaggedOutput(TAG_CLEAN, clean_data)

        except Exception as error:
            error_metadata = {
                'raw_line': element,
                'error_reason': str(error)
            }
            yield beam.pvalue.TaggedOutput(TAG_DEAD_LETTER, error_metadata)