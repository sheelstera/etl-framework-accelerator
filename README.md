
# Lean ETL Framework

## Project Overview

This project is a **lean** React based ETL (Extract, Transform, Load) framework that leverages LLMs to expedite and bootstrap the journey along the flow. It is designed to handle multiple data sources (such as ADLS, S3, etc.) and supports different file formats (CSV, TSV, Parquet, and JSON). The framework dynamically processes these sources and sinks, runs SQL transformations, and saves the results to specified output destinations.

## Directory Structure

The project is structured as follows:

```
project_root/
├── README.md
├── data-quality-check-app
│      ├── .env
│      ├── README.md
│      ├── backend
│      │       ├── DQC_TEMPLATE.py
│      │       ├── app.py
│      │       └── requirements.txt
│      └── src
│           ├── App.js
│           ├── components
│           │       ├── ConfigFileUpload.js
│           │       ├── FileUpload.js
│           │       ├── MappingTable.js
│           │       ├── RecordIdentifierSelection.js
│           │       ├── SchemaFileUpload.js
│           │       ├── SqlCheckTable.js
│           │       └── SqlToXmlConverter.js
│           ├── components
│           └── index.js
├── example
│       ├── config.yaml
│       ├── generated_queries.xml
│       ├── input.sql
│       ├── table1.csv
│       └── table2.csv
└── src
    ├── connectors
    │       ├── __init__.py
    │       ├── adls_connector.py
    │       ├── connector_interfaces.py
    │       ├── kafka_connector.py
    │       ├── mongodb_connector.py
    │       ├── mysql_connector.py
    │       ├── postgres_connector.py
    │       └── s3_connector.py
    ├── decorators
    │       ├── __init__.py
    │       └── logger_decorator.py
    ├── dynamic_loader.py
    ├── etl_executor.py
    └── utils
        ├── __init__.py
        └── logging_util.py
```

## Setup Instructions

1. **Clone the Repository**:
   Download or clone the project from the source repository.

2. **Dependencies**:
   Ensure that the following dependencies are installed:
   - Python 3.x
   - PySpark
   - Python dependencies for DQ backend in requirements.txt
   - React dependencies for DQ backend in requirements.txt
   - [Node.js](https://nodejs.org/) (v14 or later)
   - [npm](https://www.npmjs.com/) (comes with Node.js) or [yarn](https://yarnpkg.com/)
3. Install Dependencies
   ```bash
   pip install -r requirements.txt
   npm install
   ```
4. **Start the app**
   
   Start the Backend (Flask):
   ```yaml
   cd backend
   python app.py
   ```
   Start the Frontend (React):
      ```bash
      npm start
      ```

5. **Prepare Configuration File**:

   This file defines the data sources and sinks for the ETL job. Here, you specify the source and sink types (e.g., `adls`, `s3`), file formats (e.g., `csv`, `tsv`, `parquet`, `json`), and other relevant configurations (such as paths and access keys).

   Example `config.yaml`:
   ```yaml
   data_sources:
     adls1:
       abfss_path: "abfss://<container>@<storage_account>.dfs.core.windows.net/path/to/file.csv"
       format: csv
       type: adls
     s3_source:
       bucket: "<bucket_name>"
       file_path: "<path/to/file>"
       format: parquet
       type: s3

   data_sink:
     mysink:
       abfss_path: "abfss://<container>@<storage_account>.dfs.core.windows.net/path/to/output.parquet"
       format: parquet
       type: adls
   
   custom_functions:
     - name: custom_length
        function: |
           def custom_length(string):
              if string:
                 return len(string)
              return 0
        return_type: IntegerType()

   - name: custom_upper
        function: |
           def custom_upper(string):
              if string:
                 return string.upper()
              return None
        return_type: StringType()
   ```

6. **Prepare Input SQL File**:   

   This file contains SQL queries for data transformations. You can use Common Table Expressions (CTEs) and complex queries to transform the data from the sources.

   Example `input.sql`:

   ```sql
   WITH join_result AS (SELECT t1.customer_id, t1.email, t1.phone, t1.date_of_birth, t1.postal_code, t1.transaction_date, t1.order_amount, t1.product_code, t1.account_number, t2.customer_name, t2.membership_status, t2.join_date, t2.last_purchase_date FROM adls1 AS t1 JOIN adls2 AS t2 ON t1.customer_id = t2.customer_id)
   WITH clean AS (SELECT customer_id, email, phone, date_of_birth, postal_code, transaction_date, order_amount, product_code, account_number, custom_upper(customer_name) as customer_name, membership_status FROM join_result)
   SELECT customer_name,sum(order_amount) FROM clean group by customer_name
   ```

7. **Run the Workflow**:

   To execute the ETL pipeline,
   - Upload Config and SQL File
   ![upload configs and sql.png](images%2Fupload%20configs%20and%20sql.png)
   - Based on your Config, the application figures out how many sources have been configured and asks you to upload a sample data file or schema file to upload the schema from
   ![upload sources.png](images%2Fupload%20sources.png)
   - Click on **Upload Files**
   - The application: 
     - uses or infers the schema
     - runs it by an LLM to map it to the best possible semantic
     - suggests it to the user as a bootstrap
      ![mapped fields.png](images%2Fmapped%20fields.png)
   - The user can now add, remove or change the mappings to the bootstrap and proceeds to approve the mappings. In our example, the `Membership` field was mapped to `nothing`. So you may remove it and change it.
   ![final mapped fields for adls2.png](images%2Ffinal%20mapped%20fields%20for%20adls2.png)
   - Click **Next**
   - Provide the Record Identifier for each dataset
   ![Record Identifier.png](images%2FRecord%20Identifier.png)
   - Generate the SQL Checks
   ![DQ SQL.png](images%2FDQ%20SQL.png)
   - The user can add, remove or change the suggestions and then save the DQ SQL checks
   - Generate the Job
   ![Generate Job.jpg](images%2FGenerate%20Job.jpg)
      ```xml
      <?xml version="1.0" ?>
      <Queries>
        <LogDQResult table="DeadLetterTable">SELECT 'ce153e45-b3b4-4388-b599-bb07c0f37e7b' AS run_id, 'Completeness' as check_type, &quot;adls1&quot; as table_name, &quot;customer_id&quot; as field_name, customer_id as field_value, 'customer_id' as record_identifier_name, customer_id as record_identifier_value, current_timestamp() as run_time FROM adls1 WHERE customer_id IS NULL;</LogDQResult>
        <LogDQResult table="DeadLetterTable">SELECT 'ce153e45-b3b4-4388-b599-bb07c0f37e7b' AS run_id, 'Uniqueness' as check_type, &quot;adls1&quot; as table_name, &quot;customer_id&quot; as field_name, customer_id as field_value, 'customer_id' as record_identifier_name, customer_id as record_identifier_value, current_timestamp() as run_time FROM adls1 WHERE customer_id IN (SELECT customer_id FROM adls1 GROUP BY customer_id HAVING COUNT(*) &gt; 1);</LogDQResult>
        <LogDQResult table="DeadLetterTable">SELECT 'ce153e45-b3b4-4388-b599-bb07c0f37e7b' AS run_id, 'Completeness' as check_type, &quot;adls1&quot; as table_name, &quot;email&quot; as field_name, email as field_value, 'customer_id' as record_identifier_name, customer_id as record_identifier_value, current_timestamp() as run_time FROM adls1 WHERE email IS NULL;</LogDQResult>
        <LogDQResult table="DeadLetterTable">SELECT 'ce153e45-b3b4-4388-b599-bb07c0f37e7b' AS run_id, 'Validity' as check_type, &quot;adls1&quot; as table_name, &quot;email&quot; as field_name, email as field_value, 'customer_id' as record_identifier_name, customer_id as record_identifier_value, current_timestamp() as run_time FROM adls1 WHERE email NOT LIKE '%@%';</LogDQResult>
        <LogDQResult table="DeadLetterTable">SELECT 'ce153e45-b3b4-4388-b599-bb07c0f37e7b' AS run_id, 'Completeness' as check_type, &quot;adls1&quot; as table_name, &quot;phone&quot; as field_name, phone as field_value, 'customer_id' as record_identifier_name, customer_id as record_identifier_value, current_timestamp() as run_time FROM adls1 WHERE phone IS NULL;</LogDQResult>
        <LogDQResult table="DeadLetterTable">SELECT 'ce153e45-b3b4-4388-b599-bb07c0f37e7b' AS run_id, 'Validity' as check_type, &quot;adls1&quot; as table_name, &quot;phone&quot; as field_name, phone as field_value, 'customer_id' as record_identifier_name, customer_id as record_identifier_value, current_timestamp() as run_time FROM adls1 WHERE LENGTH(phone) &lt; 10;</LogDQResult>
        <LogDQResult table="DeadLetterTable">SELECT 'ce153e45-b3b4-4388-b599-bb07c0f37e7b' AS run_id, 'Completeness' as check_type, &quot;adls1&quot; as table_name, &quot;date_of_birth&quot; as field_name, date_of_birth as field_value, 'customer_id' as record_identifier_name, customer_id as record_identifier_value, current_timestamp() as run_time FROM adls1 WHERE date_of_birth IS NULL;</LogDQResult>
        <LogDQResult table="DeadLetterTable">SELECT 'ce153e45-b3b4-4388-b599-bb07c0f37e7b' AS run_id, 'Validity' as check_type, &quot;adls1&quot; as table_name, &quot;date_of_birth&quot; as field_name, date_of_birth as field_value, 'customer_id' as record_identifier_name, customer_id as record_identifier_value, current_timestamp() as run_time FROM adls1 WHERE date_of_birth &gt; CURRENT_DATE();</LogDQResult>
        <LogDQResult table="DeadLetterTable">SELECT 'ce153e45-b3b4-4388-b599-bb07c0f37e7b' AS run_id, 'Completeness' as check_type, &quot;adls1&quot; as table_name, &quot;postal_code&quot; as field_name, postal_code as field_value, 'customer_id' as record_identifier_name, customer_id as record_identifier_value, current_timestamp() as run_time FROM adls1 WHERE postal_code IS NULL;</LogDQResult>
        <LogDQResult table="DeadLetterTable">SELECT 'ce153e45-b3b4-4388-b599-bb07c0f37e7b' AS run_id, 'Validity' as check_type, &quot;adls1&quot; as table_name, &quot;postal_code&quot; as field_name, postal_code as field_value, 'customer_id' as record_identifier_name, customer_id as record_identifier_value, current_timestamp() as run_time FROM adls1 WHERE postal_code RLIKE '^[0-9]{5}$' = FALSE;</LogDQResult>
        <LogDQResult table="DeadLetterTable">SELECT 'ce153e45-b3b4-4388-b599-bb07c0f37e7b' AS run_id, 'Completeness' as check_type, &quot;adls1&quot; as table_name, &quot;transaction_date&quot; as field_name, transaction_date as field_value, 'customer_id' as record_identifier_name, customer_id as record_identifier_value, current_timestamp() as run_time FROM adls1 WHERE transaction_date IS NULL;</LogDQResult>
        <LogDQResult table="DeadLetterTable">SELECT 'ce153e45-b3b4-4388-b599-bb07c0f37e7b' AS run_id, 'Timeliness' as check_type, &quot;adls1&quot; as table_name, &quot;transaction_date&quot; as field_name, transaction_date as field_value, 'customer_id' as record_identifier_name, customer_id as record_identifier_value, current_timestamp() as run_time FROM adls1 WHERE transaction_date &lt; DATEADD(year, -1, CURRENT_DATE());</LogDQResult>
        <LogDQResult table="DeadLetterTable">SELECT 'ce153e45-b3b4-4388-b599-bb07c0f37e7b' AS run_id, 'Completeness' as check_type, &quot;adls1&quot; as table_name, &quot;order_amount&quot; as field_name, order_amount as field_value, 'customer_id' as record_identifier_name, customer_id as record_identifier_value, current_timestamp() as run_time FROM adls1 WHERE order_amount IS NULL;</LogDQResult>
        <LogDQResult table="DeadLetterTable">SELECT 'ce153e45-b3b4-4388-b599-bb07c0f37e7b' AS run_id, 'Validity' as check_type, &quot;adls1&quot; as table_name, &quot;order_amount&quot; as field_name, order_amount as field_value, 'customer_id' as record_identifier_name, customer_id as record_identifier_value, current_timestamp() as run_time FROM adls1 WHERE order_amount &lt;= 0;</LogDQResult>
        <LogDQResult table="DeadLetterTable">SELECT 'ce153e45-b3b4-4388-b599-bb07c0f37e7b' AS run_id, 'Completeness' as check_type, &quot;adls1&quot; as table_name, &quot;product_code&quot; as field_name, product_code as field_value, 'customer_id' as record_identifier_name, customer_id as record_identifier_value, current_timestamp() as run_time FROM adls1 WHERE product_code IS NULL;</LogDQResult>
        <LogDQResult table="DeadLetterTable">SELECT 'ce153e45-b3b4-4388-b599-bb07c0f37e7b' AS run_id, 'Completeness' as check_type, &quot;adls1&quot; as table_name, &quot;account_number&quot; as field_name, account_number as field_value, 'customer_id' as record_identifier_name, customer_id as record_identifier_value, current_timestamp() as run_time FROM adls1 WHERE account_number IS NULL;</LogDQResult>
        <LogDQResult table="DeadLetterTable">SELECT 'ce153e45-b3b4-4388-b599-bb07c0f37e7b' AS run_id, 'Uniqueness' as check_type, &quot;adls1&quot; as table_name, &quot;account_number&quot; as field_name, account_number as field_value, 'customer_id' as record_identifier_name, customer_id as record_identifier_value, current_timestamp() as run_time FROM adls1 WHERE account_number IN (SELECT account_number FROM adls1 GROUP BY account_number HAVING COUNT(*) &gt; 1);</LogDQResult>
        <LogDQResult table="DeadLetterTable">SELECT 'ce153e45-b3b4-4388-b599-bb07c0f37e7b' AS run_id, 'Validity' as check_type, &quot;adls1&quot; as table_name, &quot;account_number&quot; as field_name, account_number as field_value, 'customer_id' as record_identifier_name, customer_id as record_identifier_value, current_timestamp() as run_time FROM adls1 WHERE LENGTH(account_number) != 10;</LogDQResult>
        <Query id="filtered_adls1">SELECT * FROM adls1 WHERE customer_id NOT IN (SELECT field_value FROM DeadLetterTable)</Query>
        <LogDQResult table="DeadLetterTable">SELECT 'ea5a5c98-a757-4a3f-86c7-83fda9b366d3' AS run_id, 'Completeness' as check_type, &quot;adls2&quot; as table_name, &quot;customer_id&quot; as field_name, customer_id as field_value, 'customer_id' as record_identifier_name, customer_id as record_identifier_value, current_timestamp() as run_time FROM adls2 WHERE customer_id IS NULL;</LogDQResult>
        <LogDQResult table="DeadLetterTable">SELECT 'ea5a5c98-a757-4a3f-86c7-83fda9b366d3' AS run_id, 'Uniqueness' as check_type, &quot;adls2&quot; as table_name, &quot;customer_id&quot; as field_name, customer_id as field_value, 'customer_id' as record_identifier_name, customer_id as record_identifier_value, current_timestamp() as run_time FROM adls2 WHERE customer_id IN (SELECT customer_id FROM adls2 GROUP BY customer_id HAVING COUNT(*) &gt; 1);</LogDQResult>
        <LogDQResult table="DeadLetterTable">SELECT 'ea5a5c98-a757-4a3f-86c7-83fda9b366d3' AS run_id, 'Completeness' as check_type, &quot;adls2&quot; as table_name, &quot;customer_name&quot; as field_name, customer_name as field_value, 'customer_id' as record_identifier_name, customer_id as record_identifier_value, current_timestamp() as run_time FROM adls2 WHERE customer_name IS NULL;</LogDQResult>
        <LogDQResult table="DeadLetterTable">SELECT 'ea5a5c98-a757-4a3f-86c7-83fda9b366d3' AS run_id, 'Validity' as check_type, &quot;adls2&quot; as table_name, &quot;customer_name&quot; as field_name, customer_name as field_value, 'customer_id' as record_identifier_name, customer_id as record_identifier_value, current_timestamp() as run_time FROM adls2 WHERE customer_name RLIKE '^[A-Za-z ]+$' = FALSE;</LogDQResult>
        <LogDQResult table="DeadLetterTable">SELECT 'ea5a5c98-a757-4a3f-86c7-83fda9b366d3' AS run_id, 'Completeness' as check_type, &quot;adls2&quot; as table_name, &quot;join_date&quot; as field_name, join_date as field_value, 'customer_id' as record_identifier_name, customer_id as record_identifier_value, current_timestamp() as run_time FROM adls2 WHERE join_date IS NULL;</LogDQResult>
        <LogDQResult table="DeadLetterTable">SELECT 'ea5a5c98-a757-4a3f-86c7-83fda9b366d3' AS run_id, 'Validity' as check_type, &quot;adls2&quot; as table_name, &quot;join_date&quot; as field_name, join_date as field_value, 'customer_id' as record_identifier_name, customer_id as record_identifier_value, current_timestamp() as run_time FROM adls2 WHERE join_date &gt; CURRENT_DATE();</LogDQResult>
        <LogDQResult table="DeadLetterTable">SELECT 'ea5a5c98-a757-4a3f-86c7-83fda9b366d3' AS run_id, 'Completeness' as check_type, &quot;adls2&quot; as table_name, &quot;last_purchase_date&quot; as field_name, last_purchase_date as field_value, 'customer_id' as record_identifier_name, customer_id as record_identifier_value, current_timestamp() as run_time FROM adls2 WHERE last_purchase_date IS NULL;</LogDQResult>
        <LogDQResult table="DeadLetterTable">SELECT 'ea5a5c98-a757-4a3f-86c7-83fda9b366d3' AS run_id, 'Timeliness' as check_type, &quot;adls2&quot; as table_name, &quot;last_purchase_date&quot; as field_name, last_purchase_date as field_value, 'customer_id' as record_identifier_name, customer_id as record_identifier_value, current_timestamp() as run_time FROM adls2 WHERE last_purchase_date &lt; DATEADD(year, -1, CURRENT_DATE());</LogDQResult>
        <Query id="filtered_adls2">SELECT * FROM adls2 WHERE customer_id NOT IN (SELECT field_value FROM DeadLetterTable)</Query>
        <Query id="user_query_1" type="User">SELECT t1.customer_id, t1.email, t1.phone, t1.date_of_birth, t1.postal_code, t1.transaction_date, t1.order_amount, t1.product_code, t1.account_number, t2.customer_name, t2.membership_status, t2.join_date, t2.last_purchase_date FROM filtered_adls1 AS t1 JOIN filtered_adls2 AS t2 ON t1.customer_id = t2.customer_id</Query>
        <Query id="user_query_2" type="User">SELECT customer_id, email, phone, date_of_birth, postal_code, transaction_date, order_amount, product_code, account_number, custom_upper(customer_name) as customer_name, membership_status FROM user_query_1</Query>
        <Query id="user_query_3" type="User">SELECT customer_name,sum(order_amount) FROM user_query_2 group by customer_name</Query>
      </Queries>
      ```
     **Notice:** how the input SQL file consisted of just business transformations and the final job automatically includes all DQ checks relevant
   - Run the Job
     - **Job Results**
     ![results.png](images%2Fresults.jpg)
     - **Job Logs**
      ![logs.jpg](images%2Flogs.jpg)
     - **Dead Letter Table**
     ![Dead Letter.png](images%2FDead%20Letter.png)
## Connector Support

The framework supports multiple connectors for different data sources and sinks. Each connector is dynamically loaded based on the `type` field in the YAML configuration.

- **ADLS**: Reads and writes to Azure Data Lake Storage.
- **S3**: Reads and writes to Amazon S3.
- **MySQL**: Reads and writes from/to MySQL databases.
- **PostgreSQL**: Reads and writes from/to PostgreSQL databases.
- **Kafka**: Reads and writes from/to Kafka topics.

Each connector supports multiple file formats, including **CSV**, **TSV**, **Parquet**, and **JSON**.

## Custom SQL Functions

The framework supports plugging in custom SQL functions. Just add your function to the custom_functions key in the yaml file as shown above.

## Logging and Error Handling

The framework includes detailed logging using Python's `logging` module. Logs are automatically generated for all major actions, such as reading from sources, executing queries, and writing to sinks. Any errors encountered during execution are logged, and exceptions are raised when unsupported file formats or configurations are encountered.

## Customization

- **Adding New Connectors**: You can extend the framework by adding new connectors for different sources and sinks. Simply add a new connector in the `connectors/` directory and ensure that it implements the `SourceConnector` or `SinkConnector` interface.

## Next Steps

- Adding a sixth step that pushes the job to a Databricks cluster and executes it
- The error handling is not robust on the React frontend and needs to be worked upon. 
- State Management is not robust in the React frontend and needs to be worked upon. 

## Contributions

Feel free to contribute by adding support for new connectors or improving the existing ones by creating PRs. For any questions or issues, please feel free to create issue in the `Issues` tab 
