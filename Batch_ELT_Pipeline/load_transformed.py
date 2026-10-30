
import mysql.connector
import pandas as pd

from config import (
    DB_HOST,
    DB_USER,
    DB_PASSWORD,
    ANALYTICS_DATABASE,
    ANALYTICS_TABLE,
    BATCH_SIZE
)

from transform import run_transformation
from validate import validate_data


# ------------------------------------------------
# 1. Create analytics database
# ------------------------------------------------

def create_analytics_database():

    connection = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD
    )

    cursor = connection.cursor()

    try:
        cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS `{ANALYTICS_DATABASE}`"
        )
        connection.commit()

        print(f"Database '{ANALYTICS_DATABASE}' is ready.")

    finally:
        cursor.close()
        connection.close()


# ------------------------------------------------
# 2. Create analytics table
# ------------------------------------------------

def create_analytics_table():

    connection = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=ANALYTICS_DATABASE
    )

    cursor = connection.cursor()

    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS `{ANALYTICS_TABLE}` (

        load_id BIGINT AUTO_INCREMENT PRIMARY KEY,

        `Order ID` VARCHAR(50) NOT NULL,
        `Customer ID` VARCHAR(50),
        `Restaurant ID` VARCHAR(50),

        `Order Date and Time` DATETIME,
        `Delivery Date and Time` DATETIME,

        `Order Value` DECIMAL(12,2),
        `Delivery Fee` DECIMAL(12,2),

        `Payment Method` VARCHAR(100),
        `Discounts and Offers` TEXT,

        `Commission Fee` DECIMAL(12,2),
        `Payment Processing Fee` DECIMAL(12,2),
        `Refunds/Chargebacks` DECIMAL(12,2),

        `Weather Condition` VARCHAR(100),
        `Order Channel` VARCHAR(100),

        `Delivery_Time_Minutes` DECIMAL(12,2),
        `Platform_Net_Revenue` DECIMAL(12,2)

    )
    """

    try:
        cursor.execute(create_table_query)
        connection.commit()

        print(f"Table '{ANALYTICS_TABLE}' is ready.")

    finally:
        cursor.close()
        connection.close()


# ------------------------------------------------
# 3. Convert Pandas values for MySQL insertion
# ------------------------------------------------

def convert_value(value):

    if pd.isna(value):
        return None

    if isinstance(value, pd.Timestamp):
        return value.to_pydatetime()

    if hasattr(value, "item"):
        return value.item()

    return value


# ------------------------------------------------
# 4. Load transformed data in batches
# ------------------------------------------------

def load_transformed_data(transformed_df):

    connection = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=ANALYTICS_DATABASE
    )

    cursor = connection.cursor()

    columns = [
        "Order ID",
        "Customer ID",
        "Restaurant ID",
        "Order Date and Time",
        "Delivery Date and Time",
        "Order Value",
        "Delivery Fee",
        "Payment Method",
        "Discounts and Offers",
        "Commission Fee",
        "Payment Processing Fee",
        "Refunds/Chargebacks",
        "Weather Condition",
        "Order Channel",
        "Delivery_Time_Minutes",
        "Platform_Net_Revenue"
    ]

    insert_query = f"""
    INSERT INTO `{ANALYTICS_TABLE}` (
        `Order ID`,
        `Customer ID`,
        `Restaurant ID`,
        `Order Date and Time`,
        `Delivery Date and Time`,
        `Order Value`,
        `Delivery Fee`,
        `Payment Method`,
        `Discounts and Offers`,
        `Commission Fee`,
        `Payment Processing Fee`,
        `Refunds/Chargebacks`,
        `Weather Condition`,
        `Order Channel`,
        `Delivery_Time_Minutes`,
        `Platform_Net_Revenue`
    )
    VALUES ({', '.join(['%s'] * len(columns))})
    """

    total_loaded = 0
    successful_batches = 0

    try:

        print("\nStarting transformed data loading...")
        print(f"Batch size: {BATCH_SIZE}")
        print("-" * 45)

        for start in range(0, len(transformed_df), BATCH_SIZE):

            batch_number = (start // BATCH_SIZE) + 1

            batch_df = transformed_df.iloc[
                start:start + BATCH_SIZE
            ][columns]

            batch_data = [
                tuple(convert_value(value) for value in row)
                for row in batch_df.itertuples(
                    index=False,
                    name=None
                )
            ]

            try:

                cursor.executemany(
                    insert_query,
                    batch_data
                )

                connection.commit()

                successful_batches += 1
                total_loaded += len(batch_data)

                print(
                    f"Batch {batch_number} loaded successfully: "
                    f"{len(batch_data)} records"
                )

            except mysql.connector.Error as error:

                connection.rollback()

                print(
                    f"Batch {batch_number} failed. "
                    f"Transaction rolled back."
                )

                raise RuntimeError(
                    f"Database insertion failed in batch "
                    f"{batch_number}: {error}"
                ) from error

        print("-" * 45)
        print(f"Successful batches: {successful_batches}")
        print(f"Total records loaded: {total_loaded}")

        return total_loaded

    finally:
        cursor.close()
        connection.close()


# ------------------------------------------------
# 5. Verify final analytics table
# ------------------------------------------------

def verify_analytics_data():

    connection = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=ANALYTICS_DATABASE
    )

    cursor = connection.cursor()

    try:

        cursor.execute(
            f"SELECT COUNT(*) FROM `{ANALYTICS_TABLE}`"
        )

        final_count = cursor.fetchone()[0]

        print("\nANALYTICS DATABASE VERIFICATION")
        print("-" * 45)
        print(f"Database: {ANALYTICS_DATABASE}")
        print(f"Table: {ANALYTICS_TABLE}")
        print(f"Total records in MySQL: {final_count}")

        return final_count

    finally:
        cursor.close()
        connection.close()


# ------------------------------------------------
# 6. Execute Task 6
# ------------------------------------------------

if __name__ == "__main__":

    # Get transformed and rejected records
    transformed_df, rejected_df = run_transformation()

    # Validate before loading
    validation_status = validate_data(
        transformed_df,
        rejected_df
    )

    if validation_status != "PASS":
        raise SystemExit(
            "Loading stopped because data validation failed."
        )

    print("\nData validation passed. Starting database loading.")

    # Create analytics database and table
    create_analytics_database()
    create_analytics_table()

    # Load transformed records
    loaded_count = load_transformed_data(transformed_df)

    # Verify final record count
    final_count = verify_analytics_data()

    print("\nFINAL LOAD SUMMARY")
    print("-" * 45)
    print(f"Records loaded in this run: {loaded_count}")
    print(f"Records present in analytics table: {final_count}")

    if loaded_count == len(transformed_df):
        print("Task 6 loading status: PASS")
    else:
        print("Task 6 loading status: FAIL")
