
import pandas as pd
from transform import run_transformation


def validate_data(transformed_df, rejected_df):

    report = []

    report.append("FOOD ORDERS - DATA VALIDATION REPORT")
    report.append("=" * 50)

    # 1. Check missing values
    print("\n1. CHECKING MISSING VALUES")

    missing_values = transformed_df.isnull().sum()

    print(missing_values)
    total_missing = int(missing_values.sum())

    print(f"Total missing values: {total_missing}")

    report.append("\n1. MISSING VALUE CHECK")
    report.append(missing_values.to_string())
    report.append(f"Total missing values: {total_missing}")

    # 2. Check duplicate records
    print("\n2. CHECKING DUPLICATE RECORDS")

    duplicate_count = int(transformed_df.duplicated().sum())

    print(f"Duplicate records in transformed data: {duplicate_count}")

    report.append("\n2. DUPLICATE RECORD CHECK")
    report.append(f"Duplicate records: {duplicate_count}")

    # 3. Verify data types
    print("\n3. CHECKING DATA TYPES")

    print(transformed_df.dtypes)

    datetime_columns = [
        "Order Date and Time",
        "Delivery Date and Time"
    ]

    numeric_columns = [
        "Order Value",
        "Delivery Fee",
        "Commission Fee",
        "Payment Processing Fee",
        "Refunds/Chargebacks",
        "Delivery_Time_Minutes",
        "Platform_Net_Revenue"
    ]

    datetime_check = all(
        pd.api.types.is_datetime64_any_dtype(transformed_df[col])
        for col in datetime_columns
    )

    numeric_check = all(
        pd.api.types.is_numeric_dtype(transformed_df[col])
        for col in numeric_columns
    )

    print("Datetime columns:", "PASS" if datetime_check else "FAIL")
    print("Numeric columns:", "PASS" if numeric_check else "FAIL")

    report.append("\n3. DATA TYPE CHECK")
    report.append(f"Datetime columns: {'PASS' if datetime_check else 'FAIL'}")
    report.append(f"Numeric columns: {'PASS' if numeric_check else 'FAIL'}")
    report.append(transformed_df.dtypes.to_string())

    # 4. Validate delivery duration
    print("\n4. VALIDATING DELIVERY DURATION")

    expected_duration = (
        transformed_df["Delivery Date and Time"]
        - transformed_df["Order Date and Time"]
    ).dt.total_seconds() / 60

    duration_check = (
        transformed_df["Delivery_Time_Minutes"].notna().all()
        and transformed_df["Delivery_Time_Minutes"].ge(0).all()
        and transformed_df["Delivery_Time_Minutes"].sub(
            expected_duration
        ).abs().le(0.000001).all()
    )

    print(
        "Delivery duration calculation:",
        "PASS" if duration_check else "FAIL"
    )

    report.append("\n4. DELIVERY DURATION CHECK")
    report.append(
        f"Delivery duration calculation: {'PASS' if duration_check else 'FAIL'}"
    )

    # 5. Validate platform net revenue
    print("\n5. VALIDATING PLATFORM NET REVENUE")

    revenue_columns = [
        "Commission Fee",
        "Delivery Fee",
        "Payment Processing Fee",
        "Refunds/Chargebacks"
    ]

    expected_revenue = (
        transformed_df["Commission Fee"]
        + transformed_df["Delivery Fee"]
        - transformed_df["Payment Processing Fee"]
        - transformed_df["Refunds/Chargebacks"]
    )

    revenue_available = transformed_df[revenue_columns].notna().all(axis=1)

    revenue_check = (
        transformed_df.loc[
            revenue_available, "Platform_Net_Revenue"
        ].notna().all()
        and transformed_df.loc[
            revenue_available, "Platform_Net_Revenue"
        ].sub(expected_revenue[revenue_available]).abs().le(
            0.000001
        ).all()
        and transformed_df.loc[
            ~revenue_available, "Platform_Net_Revenue"
        ].isna().all()
    )

    print(
        "Platform net revenue calculation:",
        "PASS" if revenue_check else "FAIL"
    )

    report.append("\n5. PLATFORM NET REVENUE CHECK")
    report.append(
        f"Platform net revenue calculation: {'PASS' if revenue_check else 'FAIL'}"
    )

    # 6. Check rejected records
    print("\n6. CHECKING REJECTED RECORDS")

    print(f"Total rejected records: {len(rejected_df)}")

    if not rejected_df.empty:
        print("\nRejection reasons:")
        print(rejected_df["Rejection_Reason"].value_counts())

        report.append("\nRejection reasons:")
        report.append(
            rejected_df["Rejection_Reason"].value_counts().to_string()
        )
    else:
        report.append("No rejected records")

    report.append(f"Total rejected records: {len(rejected_df)}")

    # 7. Overall validation result
    checks = [
        duplicate_count == 0,
        datetime_check,
        numeric_check,
        duration_check,
        revenue_check
    ]

    overall_status = "PASS" if all(checks) else "FAIL"

    print("\n" + "=" * 50)
    print("OVERALL VALIDATION STATUS:", overall_status)
    print("=" * 50)

    report.append("\n7. OVERALL VALIDATION STATUS")
    report.append(overall_status)

    # Save validation report
    with open("validation_report.txt", "w", encoding="utf-8") as file:
        file.write("\n".join(report))

    # Save rejected records
    rejected_df.to_csv("rejected_records.csv", index=False)

    print("\nValidation report saved: validation_report.txt")
    print("Rejected records saved: rejected_records.csv")

    return overall_status


if __name__ == "__main__":

    transformed_df, rejected_df = run_transformation()

    validate_data(transformed_df, rejected_df)
