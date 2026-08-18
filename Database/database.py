import os
import psycopg2


def get_connection():
    try:
        connection = psycopg2.connect(
            host="localhost",
            database="F1_Telemetry",
            user="postgres",
            password=os.getenv("DB_PASSWORD"),
            port="5432"
        )
        return connection

    except Exception as error:
        print(f"Error connecting to the database: {error}")
        return None



def insert_cleansed_data(records):
    connection = get_connection()

    if connection is None:
        return

    cursor = connection.cursor()

    for record in records:
        cursor.execute(
            """
            INSERT INTO cleansed_telemetry
            (date, rpm, speed, ngear, throttle, brake, drs,
             source, time, session_time, driver)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                record['date'],
                record['rpm'],
                record['speed'],
                record['ngear'],
                record['throttle'],
                record['brake'],
                record['drs'],
                record['source'],
                record['time'],
                record['session_time'],
                record['driver']
            )
        )

    connection.commit()
    cursor.close()
    connection.close()




def insert_dead_letter(records):
    connection = get_connection()

    if connection is None:
        return

    cursor = connection.cursor()

    for record in records:
        cursor.execute(
            """
            INSERT INTO dead_letter
            (raw_line, error_reason)
            VALUES (%s, %s)
            """,
            (
                record['raw_line'],
                record['error_reason']
            )
        )

    connection.commit()
    cursor.close()
    connection.close()


    