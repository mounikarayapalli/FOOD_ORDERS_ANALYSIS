# Food Orders Data Analysis and Batch ELT Pipeline

A practical data analysis and data engineering project using Python, Pandas, and MySQL. This project covers exploratory data analysis and the implementation of a batch-based ELT pipeline.

## Project Overview

This project focuses on analysing a Food Orders dataset and building a batch ELT pipeline using Python, Pandas, and MySQL.

The project is divided into two parts.

- **Part 1 – Data Analysis:** Exploring, cleaning, and analysing the Food Orders dataset using Python and Pandas.
- **Part 2 – Batch ELT Pipeline:** Extracting the original data, storing it in a raw MySQL database, retrieving and transforming records in batches, validating the results, and loading the processed data into a separate analytics database.

The main purpose of this project is to understand how data moves from an original CSV file through different processing stages and becomes ready for business analysis.

## Technologies Used

- Python
- Pandas
- MySQL
- MySQL Connector for Python
- Jupyter Notebook
- Visual Studio Code
- Git and GitHub

## Project Structure

```text
FOOD_ORDERS_ANALYSIS/
│
├── Part1_Data_Analysis/
│   └── Food_Orders.ipynb
│
├── Part2_Batch_ELT_Pipeline/
│   ├── config.py
│   ├── extract.py
│   ├── load_raw.py
│   ├── retrieve_raw.py
│   ├── transform.py
│   ├── validate.py
│   ├── load_transformed.py
│   ├── elt_batch_pipeline.py
│   ├── requirements.txt
│   ├── validation_report.txt
│   ├── rejected_records.csv
│   └── sql/
│       └── business_analysis.sql
│
└── README.md
```

## Part 1 – Food Orders Data Analysis Using Pandas

The first part of the project involves exploring and analysing the Food Orders dataset using Jupyter Notebook and Pandas.

The following activities were performed:

1. Loaded the original CSV dataset and explored its structure.
2. Checked missing values, duplicate records, data types, and other data quality issues.
3. Identified suitable cleaning methods based on the information stored in each column.
4. Cleaned the dataset while handling missing values carefully.
5. Created additional columns such as delivery time, order date, order hour, and platform net revenue.
6. Answered business questions using Pandas operations and groupby analysis.
7. Created visualizations to understand different patterns in the dataset.
8. Performed validation checks on the cleaned dataset.

## Part 2 – Batch ELT Pipeline Using Python and MySQL

In this part, I developed a batch-based ELT pipeline to process the Food Orders dataset.

### 1. Extracting the Source Data

The original CSV file was read using Pandas. The `chunksize` parameter was used to extract the records in batches of 100.

The original source values were preserved during extraction without performing any cleaning or transformation.

**Execution result:**
- Total records extracted: 1,010
- Batch size: 100
- Total extraction batches: 11

### 2. Loading Raw Data into MySQL

A MySQL database named `food_orders_raw_db` and a table named `raw_food_orders` were created.

The extracted records were loaded using MySQL Connector and the `executemany()` method.

Batch transactions were used to handle successful insertions and roll back failed operations.

**Execution result:**
- Database: `food_orders_raw_db`
- Table: `raw_food_orders`
- Total raw records loaded: 1,010
- Loading batches: 11

### 3. Retrieving Raw Data from MySQL

After loading the original records, the data was retrieved from MySQL using the `fetchmany()` method.

Each retrieved batch was converted into a Pandas DataFrame for further processing. The original raw table was kept unchanged.

**Execution result:**
- Total records retrieved: 1,010
- Retrieval batches: 11

### 4. Transforming Data Using Pandas

Pandas was used to clean and transform the retrieved records.

The main transformation activities included:

- Removing exact duplicate records, including duplicates appearing across different batches.
- Replacing missing payment methods with `Unknown`.
- Replacing missing discounts and offers with `Not Specified`.
- Converting timestamp columns into datetime format.
- Converting financial columns into numeric data types.
- Calculating `Delivery_Time_Minutes`.
- Calculating `Platform_Net_Revenue`.
- Identifying invalid timestamps and negative delivery durations.
- Separating valid and rejected records with appropriate rejection reasons.

Missing financial values were not automatically replaced with zero. Platform net revenue was calculated only when all the required financial components were available.

### 5. Validating Transformed Data

After transformation, validation checks were performed to make sure the records were suitable for loading into the analytics database.

The validation process covered:

- Missing value checks.
- Duplicate record checks.
- Data type validation.
- Delivery duration validation.
- Revenue calculation validation.
- Rejected record identification.

The validation results were stored in `validation_report.txt`, and rejected records were saved in `rejected_records.csv`.

### 6. Loading Processed Data into MySQL

A separate analytics database named `food_orders_analytics_db` and a table named `cleaned_food_orders` were created.

Only validated records were loaded into the analytics database using batch insertion.

Transactions were used to handle successful and failed loading operations.

**Execution result:**

| Description | Result |
|---|---:|
| Analytics database | food_orders_analytics_db |
| Analytics table | cleaned_food_orders |
| Batch size | 100 |
| Successful loading batches | 10 |
| Total records loaded | 1,000 |
| Final MySQL record count | 1,000 |
| Loading status | PASS |

### 7. Complete Pipeline Execution

The `elt_batch_pipeline.py` file was developed to coordinate the complete ELT workflow.

It executes the following stages in order:

1. Source data extraction.
2. Raw data loading into MySQL.
3. Raw data retrieval in batches.
4. Data transformation using Pandas.
5. Data validation.
6. Loading valid records into the analytics database.
7. Final record-count verification.

Record-count checks were also included to avoid loading the same records again when the pipeline is rerun.

**Final execution results:**

| Description | Result |
|---|---:|
| Source records | 1,010 |
| Extraction batches | 11 |
| Raw records in MySQL | 1,010 |
| Retrieved records | 1,010 |
| Retrieval batches | 11 |
| Valid transformed records | 1,000 |
| Rejected records | 10 |
| Analytics records | 1,000 |
| Validation status | PASS |
| Pipeline status | PASS |

All 10 rejected records were identified as duplicate records.

### 8. SQL-Based Business Analysis

After loading the cleaned records into the analytics database, SQL queries were prepared in `business_analysis.sql` to analyse the processed data.

The queries cover the following business questions:

1. What is the total order value?
2. What is the average order value?
3. Which payment method has the highest number of orders?
4. Which order channel has the highest number of orders?
5. What is the average delivery time?
6. What is the total platform net revenue?

These queries help understand order patterns, customer payment preferences, delivery performance, and platform revenue.

## How to Run the Project

Follow the steps below to download and execute the project locally.

### Step 1: Clone the Repository

```bash
git clone https://github.com/mounikarayapalli/FOOD_ORDERS_ANALYSIS.git
```

### Step 2: Open the Project

Navigate to the downloaded project directory:

```bash
cd FOOD_ORDERS_ANALYSIS
```

Open the folder in Visual Studio Code.

### Step 3: Install Required Packages

Install the required Python libraries:

```bash
pip install -r Part2_Batch_ELT_Pipeline/requirements.txt
```

### Step 4: Configure MySQL

Update the database connection settings in `config.py` according to your local MySQL configuration.

Make sure the required databases and tables are created through the pipeline or the configured SQL scripts.

**Note:** Do not upload database passwords or other sensitive credentials to GitHub. Use environment variables for database credentials.

### Step 5: Run the ELT Pipeline

Navigate to the pipeline folder:

```bash
cd Part2_Batch_ELT_Pipeline
```

Execute the main pipeline:

```bash
python elt_batch_pipeline.py
```

The script will execute the complete batch ELT workflow.

### Step 6: Run SQL Business Analysis

Open `sql/business_analysis.sql` in MySQL Workbench.

Select the `food_orders_analytics_db` database and execute the queries to view the business analysis results.

## Key Learning Outcomes

Through this project, I gained practical experience in:

- Exploring and analysing datasets using Pandas.
- Identifying and handling data quality issues.
- Understanding the difference between ETL and ELT.
- Extracting and loading data in batches.
- Connecting Python applications with MySQL.
- Performing data cleaning and transformation using Pandas.
- Validating records and identifying rejected data.
- Managing separate raw and analytics databases.
- Building and executing an automated data pipeline.
- Writing SQL queries for business analysis.
- Understanding batch processing and pipeline execution.

## Conclusion

Working on this project helped me understand how raw data can be extracted, stored, processed, validated, and prepared for business analysis through a batch ELT workflow.

By combining Python, Pandas, and MySQL, I implemented a pipeline that keeps the original source data separate from the transformed data. The project also gave me practical experience in data analysis, database connectivity, batch processing, data validation, and pipeline automation.

Overall, this project helped me connect the concepts I learned in data analysis and data engineering with a practical implementation.

## Author

**Mounika Rayapalli**

B.Tech – Computer Science and Engineering

GitHub Profile: [mounikarayapalli](https://github.com/mounikarayapalli)

Project Repository: [FOOD_ORDERS_ANALYSIS](https://github.com/mounikarayapalli/FOOD_ORDERS_ANALYSIS)

---

*This project represents my practical learning experience in data analysis and data engineering using Python, Pandas, and MySQL.*