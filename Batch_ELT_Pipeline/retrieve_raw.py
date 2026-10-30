
import mysql.connector
import pandas as pd

from config import (
    DB_HOST,
    DB_USER,
    DB_PASSWORD,
    RAW_DATABASE,
    RAW_TABLE,
    BATCH_SIZE
)


def retrieve_raw_batches():

    # Connect to the raw MySQL database
    connection = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=RAW_DATABASE
    )

    cursor = connection.cursor()

    try:

        # Retrieve all records from the raw table
        query = f"SELECT * FROM `{RAW_TABLE}`"
        cursor.execute(query)

        # Get original column names
        columns = [column[0] for column in cursor.description]

        batch_number = 0
        total_retrieved = 0

        print("Starting raw data retrieval...")
        print(f"Database: {RAW_DATABASE}")
        print(f"Table: {RAW_TABLE}")
        print(f"Batch size: {BATCH_SIZE}")
        print("-" * 45)

        while True:

            # Retrieve the next 100 records
            records = cursor.fetchmany(BATCH_SIZE)

            # Stop when no more records are available
            if not records:
                break

            batch_number += 1

            # Convert retrieved records into a Pandas DataFrame
            batch_df = pd.DataFrame(
                records,
                columns=columns
            )

            total_retrieved += len(batch_df)

            print(
                f"Batch {batch_number}: "
                f"{len(batch_df)} records retrieved"
            )

            # Return the batch number and DataFrame
            yield batch_number, batch_df

        print("-" * 45)
        print(f"Total batches retrieved: {batch_number}")
        print(f"Total records retrieved: {total_retrieved}")

    finally:

        cursor.close()
        connection.close()


if __name__ == "__main__":

    for batch_number, batch_df in retrieve_raw_batches():
        pass
