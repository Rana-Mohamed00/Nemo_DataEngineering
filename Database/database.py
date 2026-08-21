import os
from dotenv import load_dotenv
import psycopg2
def get_connection():
    try:
        load_dotenv()
        connection = psycopg2.connect(
            host= os.getenv("DB_HOST"),
            database= os.getenv("DB_NAME"),
            user= os.getenv("DB_USER"),
            password= os.getenv("DB_PASSWORD"),
            port= os.getenv("DB_PORT")
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


    