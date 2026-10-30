
import pandas as pd
from config import CSV_FILE, BATCH_SIZE


def extract_batches():

    # Check whether the source CSV file exists
    if not CSV_FILE.exists():
        raise FileNotFoundError(f"CSV file not found: {CSV_FILE}")

    print("Starting batch extraction...")
    print(f"Source file: {CSV_FILE}")
    print(f"Batch size: {BATCH_SIZE}")
    print("-" * 40)

    # Read the CSV file in batches of 100 records
    batch_number = 0
    total_records = 0

    for batch_number, batch_df in enumerate(
        pd.read_csv(CSV_FILE, chunksize=BATCH_SIZE),
        start=1
    ):

        record_count = len(batch_df)
        total_records += record_count

        print(
            f"Batch {batch_number}: "
            f"{record_count} records extracted"
        )

        yield batch_number, batch_df

    print("-" * 40)
    print(f"Total batches extracted: {batch_number}")
    print(f"Total records extracted: {total_records}")


if __name__ == "__main__":

    for batch_number, batch_df in extract_batches():
        pass
