
import pandas as pd

from retrieve_raw import retrieve_raw_batches


# Financial columns
FINANCIAL_COLUMNS = [
    "Order Value",
    "Delivery Fee",
    "Commission Fee",
    "Payment Processing Fee",
    "Refunds/Chargebacks"
]


def transform_batch(batch_number, batch_df, seen_hashes):

    print(f"\nTransforming Batch {batch_number}...")

    # Make a copy so the retrieved DataFrame is not modified
    batch_df = batch_df.copy()

    # ------------------------------------------------
    # 1. Identify exact duplicates across all batches
    # ------------------------------------------------

    # Generate a unique fingerprint for each original row
    row_hashes = pd.util.hash_pandas_object(
        batch_df,
        index=False
    )

    duplicate_mask = row_hashes.isin(seen_hashes)

    # Also identify duplicates within the current batch
    duplicate_mask |= row_hashes.duplicated(keep="first")

    # Remember every row fingerprint for future batches
    seen_hashes.update(row_hashes.tolist())

    duplicate_records = batch_df.loc[duplicate_mask].copy()
    duplicate_records["Rejection_Reason"] = "Duplicate record"

    # Keep only non-duplicate records
    batch_df = batch_df.loc[~duplicate_mask].copy()

    # ------------------------------------------------
    # 2. Handle missing values using business rules
    # ------------------------------------------------

    batch_df["Payment Method"] = (
        batch_df["Payment Method"].fillna("Unknown")
    )

    batch_df["Discounts and Offers"] = (
        batch_df["Discounts and Offers"].fillna("Not Specified")
    )

    # ------------------------------------------------
    # 3. Convert timestamps into datetime format
    # ------------------------------------------------

    batch_df["Order Date and Time"] = pd.to_datetime(
        batch_df["Order Date and Time"],
        errors="coerce"
    )

    batch_df["Delivery Date and Time"] = pd.to_datetime(
        batch_df["Delivery Date and Time"],
        errors="coerce"
    )

    # ------------------------------------------------
    # 4. Convert financial columns into numeric format
    # ------------------------------------------------

    for column in FINANCIAL_COLUMNS:

        batch_df[column] = pd.to_numeric(
            batch_df[column],
            errors="coerce"
        )

    # ------------------------------------------------
    # 5. Calculate delivery duration in minutes
    # ------------------------------------------------

    batch_df["Delivery_Time_Minutes"] = (
        batch_df["Delivery Date and Time"]
        - batch_df["Order Date and Time"]
    ).dt.total_seconds() / 60

    # ------------------------------------------------
    # 6. Calculate platform net revenue
    # ------------------------------------------------

    batch_df["Platform_Net_Revenue"] = (
        batch_df["Commission Fee"]
        + batch_df["Delivery Fee"]
        - batch_df["Payment Processing Fee"]
        - batch_df["Refunds/Chargebacks"]
    )

    # Keep revenue missing if any required component is missing
    revenue_columns = [
        "Commission Fee",
        "Delivery Fee",
        "Payment Processing Fee",
        "Refunds/Chargebacks"
    ]

    batch_df.loc[
        batch_df[revenue_columns].isna().any(axis=1),
        "Platform_Net_Revenue"
    ] = float("nan")

    # ------------------------------------------------
    # 7. Identify invalid records
    # ------------------------------------------------

    invalid_timestamp_mask = (
        batch_df["Order Date and Time"].isna()
        | batch_df["Delivery Date and Time"].isna()
    )

    negative_duration_mask = (
        batch_df["Delivery_Time_Minutes"] < 0
    )

    invalid_mask = (
        invalid_timestamp_mask
        | negative_duration_mask
    )

    rejected_records = batch_df.loc[invalid_mask].copy()

    # Add rejection reasons
    rejected_records["Rejection_Reason"] = ""

    rejected_records.loc[
        invalid_timestamp_mask[invalid_mask],
        "Rejection_Reason"
    ] = "Missing or invalid order/delivery timestamp"

    rejected_records.loc[
        negative_duration_mask[invalid_mask],
        "Rejection_Reason"
    ] = "Negative delivery duration"

    # Keep only valid records
    valid_records = batch_df.loc[~invalid_mask].copy()

    # Combine duplicate and invalid records
    rejected_batch = pd.concat(
        [duplicate_records, rejected_records],
        ignore_index=True
    )

    print(f"Batch {batch_number} input records: {len(batch_df) + len(duplicate_records)}")
    print(f"Duplicate records: {len(duplicate_records)}")
    print(f"Valid records: {len(valid_records)}")
    print(f"Rejected records: {len(rejected_batch)}")

    return valid_records, rejected_batch



# ------------------------------------------------
# Run transformation for all retrieved batches
# ------------------------------------------------

def run_transformation():

    seen_hashes = set()
    transformed_batches = []
    rejected_batches = []

    for batch_number, batch_df in retrieve_raw_batches():

        valid_df, rejected_df = transform_batch(
            batch_number, batch_df, seen_hashes
        )

        transformed_batches.append(valid_df)
        rejected_batches.append(rejected_df)

    final_transformed_df = pd.concat(
        transformed_batches, ignore_index=True
    )

    final_rejected_df = pd.concat(
        rejected_batches, ignore_index=True
    )

    print("\nTRANSFORMATION SUMMARY")
    print("-" * 40)
    print(f"Total valid records: {len(final_transformed_df)}")
    print(f"Total rejected records: {len(final_rejected_df)}")

    return final_transformed_df, final_rejected_df


# Run transformation when this file is executed directly

if __name__ == "__main__":

    final_transformed_df, final_rejected_df = run_transformation()

    print("\nTransformed Data Preview:")
    print(final_transformed_df.head())

    print("\nRejected Records Preview:")
    print(final_rejected_df.head())

    print("\nTransformed Data Types:")
    print(final_transformed_df.dtypes)


    