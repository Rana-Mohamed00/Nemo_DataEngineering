from database import insert_dead_letter

test_record = {
    'raw_line': '2021-12-12,INVALID_DATA,ABC',
    'error_reason': 'Invalid RPM value'
}

insert_dead_letter([test_record])

print("Dead letter test record inserted successfully!")