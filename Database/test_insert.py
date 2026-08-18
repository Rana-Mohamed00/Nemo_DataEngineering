from database import insert_cleansed_data

test_record = {
    'date': '2021-12-12 13:50:53.603',
    'rpm': 7380.0,
    'speed': 99.0,
    'ngear': 3,
    'throttle': 12.0,
    'brake': False,
    'drs': 0,
    'source': 'car',
    'time': '0 days 01:49:53.593000',
    'session_time': '0 days 01:49:53.593000',
    'driver': 3.0
}

insert_cleansed_data([test_record])

print("Test record inserted successfully!")