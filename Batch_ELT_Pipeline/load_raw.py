
import mysql.connector
import pandas as pd

from config import (
    DB_HOST,
    DB_USER,
    DB_PASSWORD,
    RAW_DATABASE,
    RAW_TABLE,
    CSV_FILE,
    BATCH_SIZE
)

from extract import extract_batches


def create_raw_database():

    # Connect to MySQL server
    connection = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD
    )

    cursor = connection.cursor()

    # Create raw database if it does not exist
    cursor.execute(
        f"CREATE DATABASE IF NOT EXISTS `{RAW_DATABASE}`"
    )

    print(f"Database '{RAW_DATABASE}' is ready.")

    cursor.close()
    connection.close()


def create_raw_table():

    connection = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=RAW_DATABASE
    )

    cursor = connection.cursor()

    # Read only the original CSV column names
    columns = pd.read_csv(
        CSV_FILE,
        nrows=0,
        dtype=str
    ).columns.tolist()

    # Create all original columns as TEXT
    column_definitions = ", ".join(
        f"`{column.replace('`', '``')}` TEXT NULL"
        for column in columns
    )

    create_table_query = f"""
        CREATE TABLE IF NOT EXISTS `{RAW_TABLE}` (
            {column_definitions}
        )
    """

    cursor.execute(create_table_query)

    connection.commit()

    print(f"Table '{RAW_TABLE}' is ready.")

    cursor.close()
    connection.close()


def load_raw_data():

    connection = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=RAW_DATABASE
    )

    cursor = connection.cursor()

    # Get original CSV column names
    columns = pd.read_csv(
        CSV_FILE,
        nrows=0,
        dtype=str
    ).columns.tolist()

    column_names = ", ".join(
        f"`{column.replace('`', '``')}`"
        for column in columns
    )

    placeholders = ", ".join(["%s"] * len(columns))

    insert_query = f"""
        INSERT INTO `{RAW_TABLE}` ({column_names})
        VALUES ({placeholders})
    """

    total_loaded = 0
    successful_batches = 0

    try:

        # Extract and insert records batch by batch
        for batch_number, batch_df in extract_batches():

            # Convert missing values to SQL NULL
            batch_df = batch_df.astype(object).where(
                pd.notna(batch_df),
                None
            )

            records = [
                tuple(row)
                for row in batch_df.itertuples(
                    index=False,
                    name=None
                )
            ]

            try:

                # Insert the complete batch
                cursor.executemany(
                    insert_query,
                    records
                )

                # Commit this batch
                connection.commit()

                total_loaded += len(records)
                successful_batches += 1

                print(
                    f"Batch {batch_number} loaded successfully: "
                    f"{len(records)} records"
                )

            except mysql.connector.Error as error:

                # Roll back the failed batch
                connection.rollback()

                print(
                    f"Batch {batch_number} failed: {error}"
                )

                raise

    finally:

        cursor.close()
        connection.close()

    print("-" * 45)
    print(f"Successful batches: {successful_batches}")
    print(f"Total records loaded: {total_loaded}")


def verify_raw_data():

    connection = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=RAW_DATABASE
    )

    cursor = connection.cursor()

    cursor.execute(
        f"SELECT COUNT(*) FROM `{RAW_TABLE}`"
    )

    total_records = cursor.fetchone()[0]

    print("-" * 45)
    print("RAW DATABASE VERIFICATION")
    print(f"Database: {RAW_DATABASE}")
    print(f"Table: {RAW_TABLE}")
    print(f"Total records in MySQL: {total_records}")

    cursor.close()
    connection.close()


if __name__ == "__main__":

    create_raw_database()

    create_raw_table()

    load_raw_data()

    verify_raw_data()
