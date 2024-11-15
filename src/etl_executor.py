import xml.etree.ElementTree as ET
import yaml
from pyspark.sql import SparkSession
from dynamic_loader import get_connector
from utils.logging_util import setup_logger   # Import logger setup utility
from decorators.logger_decorator import log_method  # Import logger decorator
from pyspark.sql.functions import udf
from pyspark.sql.types import *

class ETLExecutor:
    def __init__(self, spark: SparkSession, yaml_config: dict, xml_file: str):
        self.spark = spark
        self.yaml_config = yaml_config
        self.xml_file = xml_file
        self.logger = setup_logger(self.__class__.__name__)
        self.register_custom_functions()
        self.deadletter_df = None

    def _unescape_xml_characters(self, text):
        """Replaces all XML escape sequences with their original characters for Spark SQL compatibility."""
        escape_sequences = {
            "&quot;": "\"",
            "&apos;": "'",
            "&amp;": "&",
            "&lt;": "<",
            "&gt;": ">"
        }
        for seq, char in escape_sequences.items():
            text = text.replace(seq, char)
        return text

    def register_custom_functions(self):
        custom_functions = self.yaml_config.get("custom_functions", [])

        for func in custom_functions:
            exec(func["function"], globals())  # Define function in global scope
            udf_function = udf(globals()[func["name"]], eval(func["return_type"]))
            self.spark.udf.register(func["name"], udf_function)
            self.logger.info(f"Registered custom function: {func['name']}")
    def _append_to_deadletter(self, df):
        """Appends records to DeadLetterTable, maintaining it as a rolling DataFrame."""
        if self.deadletter_df is None:
            self.deadletter_schema = df.schema
            self.deadletter_df = df
        else:
            df = self.spark.createDataFrame(df.rdd, schema=self.deadletter_schema)
            self.deadletter_df = self.deadletter_df.union(df)

        # Register DeadLetterTable as a temporary view for immediate querying
        self.deadletter_df.createOrReplaceTempView("DeadLetterTable")

    @log_method
    def execute(self):
        self.logger.info("Starting ETL execution.")

        # Parse the XML file to extract SQL queries and their sequence
        tree = ET.parse(self.xml_file)
        root = tree.getroot()

        # A map to store DataFrame references after each query
        df_map = {}
        dq_results = []
        for source_name, source_config in self.yaml_config['data_sources'].items():
            source_type = source_config['type']
            self.logger.info(f"Processing source: {source_name} of type: {source_type}")

            # Dynamically load the appropriate connector for the source based on its type
            connector = get_connector(f'{source_type.capitalize()}Source', source_config)
            df_map[source_name] = connector.read(self.spark)
            df_map[source_name].createOrReplaceTempView(source_name)
            self.logger.info(f"Registered {source_name} as a temporary view")

        # Execute <Query> and <LogDQResult> tags from the XML file
        for elem in root:
            if elem.tag == "Query":
                query_id = elem.get("id")
                sql_statement = self._unescape_xml_characters(elem.text.strip())
                self.logger.info(f"Executing query: {query_id} - {sql_statement}")

                # Execute the SQL query using the temporary views
                df_map[query_id] = self.spark.sql(sql_statement)
                df_map[query_id].createOrReplaceTempView(query_id)
                self.logger.info(f"Registered query result {query_id} as a temporary view")

            elif elem.tag == "LogDQResult":
                table_name = elem.get("table")
                sql_statement = self._unescape_xml_characters(elem.text.strip())
                self.logger.info(f"Logging DQ Result into: {table_name} - {sql_statement}")

                dq_df = self.spark.sql(sql_statement)
                self._append_to_deadletter(dq_df)  # Append results to DeadLetterTable

        # Write DeadLetterTable to a CSV file at the end of processing
        if self.deadletter_df:
            output_path = "DeadLetterTable"
            self.deadletter_df.write.mode("overwrite").parquet(output_path)
            self.logger.info(f"Written accumulated DeadLetterTable to {output_path}")

        # Write to the sink
        for sink_name, sink_config in self.yaml_config['data_sink'].items():
            sink_type = sink_config['type']
            sink_connector = get_connector(f'{sink_type.capitalize()}Sink', sink_config)
            sink_connector.write(df_map[query_id])

        self.logger.info("ETL execution completed successfully.")
