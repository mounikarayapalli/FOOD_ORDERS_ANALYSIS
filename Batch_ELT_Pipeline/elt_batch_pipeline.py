
import mysql.connector

from config import (
    DB_HOST,
    DB_USER,
    DB_PASSWORD,
    RAW_DATABASE,
    RAW_TABLE,
    ANALYTICS_DATABASE,
    ANALYTICS_TABLE,
    BATCH_SIZE
)

from extract import extract_batches

from load_raw import (
    create_raw_database,
    create_raw_table,
    load_raw_data,
    verify_raw_data
)

from retrieve_raw import retrieve_raw_batches

from transform import run_transformation

from validate import validate_data

from load_transformed import (
    create_analytics_database,
    create_analytics_table,
    load_transformed_data,
    verify_analytics_data
)


# Get record count from MySQL
def get_record_count(database, table):

    connection = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=database
    )

    cursor = connection.cursor()

    try:
        cursor.execute(
            f"SELECT COUNT(*) FROM `{table}`"
        )

        return cursor.fetchone()[0]

    finally:
        cursor.close()
        connection.close()


# Main ELT Pipeline
def run_elt_pipeline():

    print("\n======================================")
    print("       FOOD ORDERS ELT PIPELINE")
    print("======================================")

    # STEP 1: Extract source CSV
    print("\nSTEP 1: Extracting source CSV")

    total_extracted = 0
    total_extraction_batches = 0

    for batch_number, batch_df in extract_batches():

        total_extracted += len(batch_df)
        total_extraction_batches += 1

        print(
            f"Extracted batch {batch_number}: "
            f"{len(batch_df)} records"
        )

    print(f"Total extracted records: {total_extracted}")
    print(f"Total extraction batches: {total_extraction_batches}")

    # STEP 2: Prepare raw database
    print("\nSTEP 2: Preparing raw database")

    create_raw_database()
    create_raw_table()

    raw_count = get_record_count(
        RAW_DATABASE,
        RAW_TABLE
    )

    raw_loaded_this_run = 0
    raw_successful_batches = 0

    if raw_count == 0:

        print("\nRaw table is empty. Loading source data.")

        load_raw_data()

        new_raw_count = get_record_count(
            RAW_DATABASE,
            RAW_TABLE
        )

        raw_loaded_this_run = new_raw_count - raw_count

        raw_successful_batches = (
            raw_loaded_this_run + BATCH_SIZE - 1
        ) // BATCH_SIZE

    else:

        print(
            f"Raw table already contains {raw_count} records."
        )
        print("Skipping raw loading to prevent duplicates.")

    verify_raw_data()

    # STEP 3: Retrieve raw data
    print("\nSTEP 3: Retrieving raw data")

    retrieved_count = 0
    retrieved_batches = 0

    for batch_number, batch_df in retrieve_raw_batches():

        retrieved_batches += 1
        retrieved_count += len(batch_df)

        print(
            f"Retrieved batch {batch_number}: "
            f"{len(batch_df)} records"
        )

    print(f"Total retrieved records: {retrieved_count}")

    # STEP 4: Transform data
    print("\nSTEP 4: Transforming data")

    transformed_df, rejected_df = run_transformation()

    # STEP 5: Validate data
    print("\nSTEP 5: Validating transformed data")

    validation_status = validate_data(
        transformed_df,
        rejected_df
    )

    if validation_status != "PASS":

        raise SystemExit(
            "\nPipeline stopped because validation failed."
        )

    print("\nValidation status: PASS")

    # STEP 6: Prepare analytics database
    print("\nSTEP 6: Preparing analytics database")

    create_analytics_database()
    create_analytics_table()

    analytics_count = get_record_count(
        ANALYTICS_DATABASE,
        ANALYTICS_TABLE
    )

    loaded_count = 0
    analytics_successful_batches = 0

    if analytics_count == 0:

        print("\nAnalytics table is empty. Loading validated data.")

        loaded_count = load_transformed_data(
            transformed_df
        )

        analytics_successful_batches = (
            loaded_count + BATCH_SIZE - 1
        ) // BATCH_SIZE

    else:

        print(
            f"Analytics table already contains "
            f"{analytics_count} records."
        )
        print("Skipping loading to prevent duplicate records.")

    # STEP 7: Verify final data
    print("\nSTEP 7: Verifying analytics data")

    final_count = verify_analytics_data()

    # STEP 8: Final Execution Report
    print("\n======================================")
    print("          FINAL EXECUTION REPORT")
    print("======================================")

    print(f"Total records extracted from CSV: {total_extracted}")

    print(f"Total extraction batches: {total_extraction_batches}")

    print(f"Total raw records loaded in this run: {raw_loaded_this_run}")

    print(f"Total raw records in MySQL: {get_record_count(RAW_DATABASE, RAW_TABLE)}")

    print(f"Total raw records retrieved: {retrieved_count}")

    print(f"Total retrieval batches: {retrieved_batches}")

    print(f"Total valid records transformed: {len(transformed_df)}")

    print(f"Total rejected records: {len(rejected_df)}")

    print(f"Total transformed records loaded in this run: {loaded_count}")

    print(f"Total records in analytics database: {final_count}")

    print("\nBATCH EXECUTION DETAILS")
    print("--------------------------------------")

    print(f"Raw loading successful batches: {raw_successful_batches}")

    print(f"Analytics loading successful batches: {analytics_successful_batches}")

    total_successful_batches = (
        raw_successful_batches + analytics_successful_batches
    )

    print(f"Total successful loading batches: {total_successful_batches}")

    # Failed batches stop the pipeline by raising an error.
    # Reaching this report means no loading batch failed.
    print("Total failed loading batches: 0")

    print("\nFINAL VALIDATION STATUS")
    print("--------------------------------------")

    print(f"Validation status: {validation_status}")

    if (
        validation_status == "PASS"
        and total_extracted == retrieved_count
        and len(transformed_df) + len(rejected_df) == retrieved_count
        and final_count == len(transformed_df)
    ):

        print("\nOVERALL PIPELINE STATUS: PASS")

    else:

        print("\nOVERALL PIPELINE STATUS: CHECK REQUIRED")


if __name__ == "__main__":

    run_elt_pipeline()
