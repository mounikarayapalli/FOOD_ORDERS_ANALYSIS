# Food Orders Data Analysis and Batch ELT Pipeline

## Project Overview

This project focuses on analysing a Food Orders dataset and developing a batch ELT pipeline using Python, Pandas and MySQL.

The project is divided into two parts. The first part focuses on understanding, cleaning and analysing the dataset using Pandas. The second part implements a batch ELT pipeline that extracts the original data, loads it into a raw MySQL database, retrieves and transforms the records using Pandas, validates the data and loads the processed records into a separate analytics database.

The main objective is to understand the complete data workflow, from the original CSV file to structured data that can be used for business analysis.

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
Food-Orders-Data-Analysis-ELT/
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

## Part 1 – Data Analysis Using Pandas

In the first part, I used Jupyter Notebook and Pandas to explore and analyse the Food Orders dataset.

The work included:

1. Loading the original CSV dataset and understanding its structure.
2. Checking missing values, duplicate records, data types and possible data quality issues.
3. Identifying suitable data cleaning rules based on the meaning of each column.
4. Cleaning the data while handling missing values carefully.
5. Creating additional columns such as delivery time, order date, order hour and platform net revenue.
6. Answering business questions using Pandas calculations and groupby operations.
7. Creating visualizations to understand the data and identify useful patterns.
8. Validating the cleaned dataset and checking the results.

## Part 2 – Batch ELT Pipeline Using Python and MySQL

In the second part, I developed a batch ELT pipeline to process the Food Orders dataset.

### 1. Extract the Source Data

I used Pandas to read the original CSV file in batches of 100 records using the `chunksize` parameter.

The original records were extracted without cleaning or modifying their values.

**Result:** 1,010 records extracted in 11 batches.

### 2. Load Raw Data into MySQL

I created a MySQL database named `food_orders_raw_db` and a table named `raw_food_orders`.

The original records were loaded using MySQL Connector and `executemany()`. Batch transactions were used to commit successful insertions and roll back failed insertions.

**Result:** 1,010 raw records loaded and verified in MySQL.

### 3. Retrieve Raw Data from MySQL

I retrieved the raw records using MySQL Connector and `fetchmany()`.

Each batch was converted into a Pandas DataFrame for further processing. The original raw table remained unchanged.

**Result:** 1,010 records retrieved in 11 batches.

### 4. Transform Data Using Pandas

I used Pandas to clean and transform the retrieved records.

The main operations included:

- Removing exact duplicate records, including duplicates across different batches.
- Handling missing payment methods using `Unknown`.
- Handling missing discounts and offers using `Not Specified`.
- Converting timestamps into datetime format.
- Converting financial columns into numeric data types.
- Calculating `Delivery_Time_Minutes`.
- Calculating `Platform_Net_Revenue`.
- Identifying invalid timestamps and negative delivery durations.
- Separating valid and rejected records with rejection reasons.

Missing financial values were not automatically replaced with zero. Platform net revenue was calculated only when all required financial components were available.

### 5. Validate Transformed Data

I performed validation checks on the transformed records.

The checks included missing values, duplicate records, data types, delivery duration calculations, revenue calculations and rejected records.

The validation results were saved in `validation_report.txt`, and rejected records were stored in `rejected_records.csv` if that is the filename used in the project.

### 6. Load Transformed Data into MySQL

I created a separate analytics database named `food_orders_analytics_db` and a table named `cleaned_food_orders`.

Only validated records were loaded into the analytics database in batches of 100. Transactions were used to handle successful and failed insertions.

**Result:**

- Analytics database: `food_orders_analytics_db`
- Analytics table: `cleaned_food_orders`
- Batch size: 100
- Successful loading batches in the initial load: 10
- Total records loaded: 1,000
- Final MySQL record count: 1,000
- Loading status: PASS

### 7. Pipeline Execution

I created `elt_batch_pipeline.py` to coordinate the complete workflow.

The pipeline executes extraction, raw loading, retrieval, transformation, validation and analytics loading in the required order.

Record-count checks were included to avoid loading the same records again when the pipeline is rerun.

**Execution Results:**

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

### 8. SQL Business Analysis

I prepared SQL queries in `business_analysis.sql` to analyse the processed data in the analytics database.

The queries are designed to calculate:

- Total order value.
- Average order value.
- Payment method with the highest number of orders.
- Order channel with the highest number of orders.
- Average delivery time.
- Total platform net revenue.

## How to Run the Project

### Step 1: Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/Food-Orders-Data-Analysis-ELT.git
```

### Step 2: Open the Project

Open the downloaded project folder in Visual Studio Code.

### Step 3: Install Required Packages

```bash
pip install -r Part2_Batch_ELT_Pipeline/requirements.txt
```

### Step 4: Configure MySQL

Update the database connection settings in `config.py` with your local MySQL details. Do not publish your database password or other credentials.

Create the required databases and tables through the pipeline or the provided SQL scripts, as configured in the project.

### Step 5: Run the ELT Pipeline

Open the Part 2 folder in the terminal:

```bash
cd Part2_Batch_ELT_Pipeline
```

Execute:

```bash
python elt_batch_pipeline.py
```

### Step 6: Execute SQL Business Analysis

Open `sql/business_analysis.sql` in MySQL Workbench, select the analytics database and execute the queries to view the business analysis results.

## Key Learning Outcomes

Through this project, I gained practical experience in:

- Exploring and analysing real-world datasets using Pandas.
- Identifying and handling data quality issues.
- Understanding the difference between ETL and ELT.
- Extracting and loading data in batches.
- Connecting Python applications with MySQL.
- Performing data transformations using Pandas.
- Validating records and identifying rejected data.
- Managing separate raw and analytics databases.
- Building and executing an automated data pipeline.
- Writing SQL queries for business analysis.

## Conclusion

This project helped me understand how raw data can be extracted, stored, processed, validated and prepared for analysis through a batch ELT workflow.

By combining Python, Pandas and MySQL, I developed a pipeline that preserves the original raw data and stores validated records separately for analytics. It also gave me practical experience in data analysis, database operations, batch processing and pipeline execution.